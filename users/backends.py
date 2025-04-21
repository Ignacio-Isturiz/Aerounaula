from django.contrib.auth.backends import BaseBackend
from dbmodels.models.usuario import Usuario
from django.contrib.auth.hashers import check_password

class UsuarioBackend(BaseBackend):
    def authenticate(self, request, correo=None, clave=None):
        try:
            usuario = Usuario.objects.get(correo=correo)
            if usuario.estado and usuario.confirmado and check_password(clave, usuario.clave):
                return usuario
        except Usuario.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
