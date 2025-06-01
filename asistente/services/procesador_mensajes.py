from rapidfuzz import process, fuzz
import re
from .vuelos_por_destino import BuscadorPorDestino
from .vuelos_por_origen import BuscadorPorOrigen
from .sugeridor_cercania import SugeridorPorCercania
from dbmodels.models import Vuelos

class ProcesadorMensajes:
    def __init__(self):
        self.sugeridor = SugeridorPorCercania()

    def extraer_destino(self, texto):
        match = re.search(r"(?:vuelos\s+(?:a|hacia)\s+)([a-záéíóúñ\s]+)", texto.lower())
        return match.group(1).strip(" .!?\"").title() if match else ""

    def extraer_origen(self, texto):
        match = re.search(r"(?:vuelos\s+(?:desde|de)\s+)([a-záéíóúñ\s]+)", texto.lower())
        return match.group(1).strip(" .!?\"").title() if match else ""

    def procesar(self, mensaje):
        mensaje = mensaje.lower()
        destinos_db = list(Vuelos.objects.values_list('destino', flat=True).distinct())
        origenes_db = list(Vuelos.objects.values_list('origen', flat=True).distinct())

        if "vuelos a" in mensaje or "hacia" in mensaje:
            ciudad = self.extraer_destino(mensaje)
            buscador = BuscadorPorDestino()
            vuelos = buscador.buscar(ciudad)
            return self._respuesta_vuelos(vuelos, ciudad, destinos_db, "destino")

        elif "vuelos desde" in mensaje or "de" in mensaje:
            ciudad = self.extraer_origen(mensaje)
            buscador = BuscadorPorOrigen()
            vuelos = buscador.buscar(ciudad)
            return self._respuesta_vuelos(vuelos, ciudad, origenes_db, "origen")

        return "Escribe algo como 'vuelos a Medellín' o 'vuelos desde Bogotá'."

    def _respuesta_vuelos(self, vuelos, ciudad, ciudades_db, tipo):
        if vuelos.exists():
            return "\n".join([
                f"{'Destino' if tipo == 'origen' else 'Origen'}: {getattr(v, 'destino' if tipo == 'origen' else 'origen')}\n"
                f"Fecha de salida: {v.fecha_salida.strftime('%d/%m/%Y')}\n"
                f"Precio: ${v.precio:,.0f} COP\n"
                for v in vuelos
            ])
        match = process.extractOne(ciudad, ciudades_db, scorer=fuzz.token_sort_ratio)
        if match and match[1] >= 70:
            return f"¿Quisiste decir '{match[0]}'?\n" + self.procesar(f"vuelos a {match[0]}" if tipo == "destino" else f"vuelos desde {match[0]}")
        return self.sugeridor.sugerir(ciudad)
