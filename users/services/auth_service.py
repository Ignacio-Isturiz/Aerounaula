from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from dbmodels.models.usuario import Usuario


class AuthService:
    @staticmethod
    def autenticar_usuario(request, correo, clave):
        return authenticate(request, correo=correo, clave=clave)

    @staticmethod
    def registrar_usuario(nombre, correo, clave, rol):
        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            clave=make_password(clave),
            estado=True,
            confirmado=False,
            token=None,
            fechatoken=timezone.now(),
            id_rol=rol
        )
        usuario.save()
        return usuario
