from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from rapidfuzz import process, fuzz
from dbmodels.models import Vuelos
import re

# Geolocalizador
geolocator = Nominatim(user_agent="aerounaula")

# Caché para coordenadas
coordenadas_cache = {}

def obtener_coordenadas(ciudad):
    ciudad = ciudad.strip().title()
    if ciudad in coordenadas_cache:
        return coordenadas_cache[ciudad]
    
    try:
        ubicacion = geolocator.geocode(ciudad)
        if ubicacion:
            coords = (ubicacion.latitude, ubicacion.longitude)
            coordenadas_cache[ciudad] = coords
            return coords
    except:
        return None
    return None

def sugerir_por_cercania(destino_usuario):
    destino_usuario = destino_usuario.title()
    coord_origen = obtener_coordenadas(destino_usuario)

    if not coord_origen:
        return f"No encontramos la ubicación de '{destino_usuario}' para recomendar ciudades cercanas."

    destinos_bd = list(
        Vuelos.objects.values_list('destino', flat=True).distinct()
    )

    destinos_filtrados = []
    for destino in destinos_bd:
        coord_destino = obtener_coordenadas(destino)
        if coord_destino:
            try:
                distancia = geodesic(coord_origen, coord_destino).kilometers
                destinos_filtrados.append((destino, distancia))
            except:
                continue

    if not destinos_filtrados:
        return f"No pudimos calcular recomendaciones cercanas a '{destino_usuario}'."

    destinos_filtrados.sort(key=lambda x: x[1])
    sugerencias = [d[0] for d in destinos_filtrados[:3]]

    if sugerencias:
        return f"No hay vuelos a '{destino_usuario}', pero tenemos destinos cercanos como: {', '.join(sugerencias)}"
    else:
        return f"No encontramos destinos cercanos disponibles a '{destino_usuario}'."

def extraer_destino(texto):
    texto = texto.lower()
    match = re.search(r"(?:vuelos\s+(?:a|hacia)\s+)([a-záéíóúñ\s]+)", texto)
    if match:
        ciudad = match.group(1).strip(" .!?\"")
        return ciudad.title()
    return ""

def extraer_origen(texto):
    texto = texto.lower()
    for palabra in ["desde", "de"]:
        if palabra in texto:
            partes = texto.split(palabra)
            if len(partes) > 1:
                origen = partes[1].strip(" .!?\"")
                if origen:
                    return origen.title()
    return ""

def procesar_mensaje(mensaje):
    mensaje = mensaje.lower()

    destinos_db = list(Vuelos.objects.values_list('destino', flat=True).distinct())
    origenes_db = list(Vuelos.objects.values_list('origen', flat=True).distinct())

    # ----------- VUELOS HACIA -----------
    if "vuelos a" in mensaje or "hacia" in mensaje:
        ciudad_destino = extraer_destino(mensaje)
        if not ciudad_destino:
            return "No logré identificar el destino en tu mensaje. Intenta escribir algo como: 'vuelos a Medellín'"

        vuelos = Vuelos.objects.filter(destino__iexact=ciudad_destino)

        if vuelos.exists():
            return f"Tenemos {vuelos.count()} vuelos hacia {ciudad_destino.title()} ✈️"

        # Corrección ortográfica
        match_result = process.extractOne(ciudad_destino, destinos_db, scorer=fuzz.ratio)
        if match_result:
            mejor_match, score, _ = match_result
            if score >= 85:
                return f"¿Quisiste decir '{mejor_match}'? Tenemos vuelos hacia ese destino ✅"

        # Sugerencias por cercanía geográfica
        return sugerir_por_cercania(ciudad_destino)

    # ----------- VUELOS DESDE -----------
    elif "vuelos desde" in mensaje or "de" in mensaje:
        ciudad_origen = extraer_origen(mensaje)
        if not ciudad_origen:
            return "No logré identificar el origen en tu mensaje. Intenta escribir algo como: 'vuelos desde Bogotá'"

        vuelos = Vuelos.objects.filter(origen__iexact=ciudad_origen)

        if vuelos.exists():
            destinos = sorted(set(v.destino for v in vuelos))
            return f"Tenemos vuelos saliendo desde {ciudad_origen.title()} hacia: {', '.join(destinos)}"

        # Corrección ortográfica
        match_result = process.extractOne(ciudad_origen, origenes_db, scorer=fuzz.ratio)
        if match_result:
            mejor_match, score, _ = match_result
            if score >= 85:
                return f"¿Quisiste decir '{mejor_match}'? Tenemos vuelos desde esa ciudad ✅"

        return f"No encontramos vuelos saliendo desde '{ciudad_origen}'."

    return "Por favor escribe algo como: '¿Qué vuelos hay hacia Cartagena?' o '¿Qué vuelos hay desde Bogotá?'"
