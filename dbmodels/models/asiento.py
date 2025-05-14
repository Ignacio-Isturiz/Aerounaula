from django.db import models
from dbmodels.models.vuelos import Vuelos
from dbmodels.models.usuario import Usuario

class Asiento(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.ForeignKey(Vuelos, on_delete=models.CASCADE, db_column='vuelo_codigo', to_field='codigo')
    asiento_numero = models.CharField(max_length=10)
    reservado = models.BooleanField(default=False, db_column='esta_reservado')
    usuario_reservado = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, db_column='usuario_reservado')

    class Meta:
        managed = False
        db_table = 'asientos'
        unique_together = ('codigo', 'asiento_numero')
