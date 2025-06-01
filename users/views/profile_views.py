from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from dbmodels.models.usuario import Usuario

def mi_cuenta(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = get_object_or_404(Usuario, id_usuario=request.session['usuario_id'])

    if request.method == 'POST' and 'delete_account' in request.POST:
        usuario.estado = False
        usuario.save()
        messages.success(request, "Cuenta desactivada exitosamente.")
        return redirect('logout')

    return render(request, 'usuarios/mi_cuenta.html', {
        'usuario': usuario,
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'ocultar_navbar': False
    })

def cambiar_contraseña(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = get_object_or_404(Usuario, id_usuario=request.session['usuario_id'])

    if request.method == 'POST':
        actual = request.POST.get('clave_actual')
        nueva = request.POST.get('nueva_clave')
        confirmar = request.POST.get('confirmar_clave')

        if not check_password(actual, usuario.clave):
            messages.error(request, "La contraseña actual no es correcta.")
        elif nueva != confirmar:
            messages.error(request, "Las contraseñas nuevas no coinciden.")
        else:
            usuario.clave = make_password(nueva)
            usuario.save()
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('mi_cuenta')

    return render(request, 'usuarios/cambiar_contraseña.html', {
        'titulo': 'Cambiar contraseña',
        'ocultar_navbar': False
    })