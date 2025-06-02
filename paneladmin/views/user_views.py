from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from dbmodels.models import Usuario, Rol

class ManageUsersView(View):
    def get(self, request):
        if request.session.get('usuario_rol') != 'Admin':
            return redirect('dashboard')

        usuarios = Usuario.objects.all()
        roles = Rol.objects.all()
        context = {
            'usuarios': usuarios,
            'roles': roles,
            'titulo': 'Gestión de Usuarios'
        }
        return render(request, 'paneladmin/manage_users.html', context)

class CreateUserView(View):
    def post(self, request):
        try:
            Usuario.objects.create(
                nombre=request.POST.get('nombre'),
                correo=request.POST.get('correo'),
                clave=request.POST.get('clave'),  # En producción: hashear clave
                id_rol_id=request.POST.get('id_rol'),
                estado=True
            )
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
        return redirect('manage_users')

class EditUserView(View):
    def post(self, request, user_id):
        usuario = get_object_or_404(Usuario, id_usuario=user_id)
        try:
            usuario.nombre = request.POST.get('nombre')
            usuario.correo = request.POST.get('correo')
            usuario.id_rol_id = request.POST.get('id_rol')
            usuario.estado = request.POST.get('estado') == 'on'
            usuario.save()
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
        return redirect('manage_users')

class DeleteUserView(View):
    def post(self, request, user_id):
        usuario = get_object_or_404(Usuario, id_usuario=user_id)
        try:
            usuario.delete()
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
        return redirect('manage_users')
