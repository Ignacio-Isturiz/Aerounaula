from .sugeridor_base import SugeridorBase
from dbmodels.models import Vuelos
from .localizacion import Localizador

class SugeridorPorCercania(SugeridorBase):
    def __init__(self):
        self.loc = Localizador()
    
    def sugerir(self, ciudad):
        coord_origen = self.loc.obtener_coordenadas(ciudad)
        if not coord_origen:
            return f"No encontramos ubicación para '{ciudad}'"

        destinos = list(Vuelos.objects.values_list('destino', flat=True).distinct())
        distancias = []

        for destino in destinos:
            distancia = self.loc.distancia_km(ciudad, destino)
            if distancia != float('inf'):
                distancias.append((destino, distancia))

        distancias.sort(key=lambda x: x[1])
        sugerencias = [d[0] for d in distancias[:3]]
        return f"Destinos cercanos: {', '.join(sugerencias)}"