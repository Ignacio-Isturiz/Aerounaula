from django.db import models
from .rol import Rol

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.CharField(unique=True, max_length=100)
    clave = models.TextField()
    estado = models.BooleanField(blank=True, null=True)
    confirmado = models.BooleanField(blank=True, null=True)
    token = models.TextField(blank=True, null=True)
    fechatoken = models.DateTimeField(blank=True, null=True)  # ✅ Campo añadido
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuario'
