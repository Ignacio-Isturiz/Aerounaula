# models/reserva.py
from django.db import models
from .usuario import Usuario
from .vuelos import Vuelos

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)  
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    id_vuelo = models.ForeignKey(Vuelos, on_delete=models.CASCADE, db_column='id_vuelo')
    fecha_reserva = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False  
        db_table = 'reserva'  