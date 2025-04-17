from django.db import models

class Vuelos(models.Model):
    id_vuelo = models.AutoField(primary_key=True)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, blank=True, null=True)
    imagen_url = models.TextField(blank=True, null=True)  # ✅ Nuevo campo agregado

    class Meta:
        managed = False
        db_table = 'vuelos'
