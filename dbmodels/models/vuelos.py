from django.db import models

class Vuelos(models.Model):
    codigo = models.CharField(primary_key=True, max_length=6, editable=False)
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.DateTimeField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, default='Disponible', null=True, blank=True)
    imagen_url = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'vuelos'
