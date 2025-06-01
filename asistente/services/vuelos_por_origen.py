from .vuelo_base import BuscadorVuelosBase
from dbmodels.models import Vuelos

class BuscadorPorOrigen(BuscadorVuelosBase):
    def buscar(self, origen):
        return Vuelos.objects.filter(origen__iexact=origen)