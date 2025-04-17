from django.db import models

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombrerol = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'rol'
