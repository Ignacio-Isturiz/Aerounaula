from .vuelo_base import BuscadorVuelosBase
from dbmodels.models import Vuelos

class BuscadorPorDestino(BuscadorVuelosBase):
    def buscar(self, destino):
        return Vuelos.objects.filter(destino__iexact=destino)