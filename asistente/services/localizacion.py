from geopy.geocoders import Nominatim
from geopy.distance import geodesic

class Localizador:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="aerounaula")
        self._cache = {}
        
    def obtener_coordenadas(self, ciudad):
        ciudad = ciudad.strip().title()
        if ciudad in self._cache:
            return self._cache[ciudad]

        try:
            ubicacion = self.geolocator.geocode(ciudad)
            if ubicacion:
                coords = (ubicacion.latitude, ubicacion.longitude)
                self._cache[ciudad] = coords
                return coords
        except:
            pass
        return None
    
    def distancia_km(self, ciudad1, ciudad2):
        coord1 = self.obtener_coordenadas(ciudad1)
        coord2 = self.obtener_coordenadas(ciudad2)
        if coord1 and coord2:
            return geodesic(coord1, coord2).kilometers
        return float('inf')
