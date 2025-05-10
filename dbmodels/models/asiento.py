from django.db import models
from dbmodels.models.vuelos import Vuelos
from dbmodels.models.usuario import Usuario  # Asegúrate de que importas el modelo correcto

class Asiento(models.Model):
    id = models.AutoField(primary_key=True)
    vuelo = models.ForeignKey(Vuelos, on_delete=models.CASCADE, db_column='vuelo_id')
    asiento_numero = models.CharField(max_length=10)
    reservado = models.BooleanField(default=False, db_column='esta_reservado')
    usuario_reservado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, db_column='usuario_reservado')

    class Meta:
        managed = False
        db_table = 'asientos'
