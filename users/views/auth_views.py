from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from axes.handlers.proxy import AxesProxyHandler
from axes.utils import reset

from dbmodels.models.usuario import Usuario, Rol
from users.forms import LoginForm, RegistroForm
from users.services.auth_service import AuthService
from users.services.token_service import TokenService
from users.services.mail_service import MailService

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            clave = form.cleaned_data['clave']

            if AxesProxyHandler().is_locked(request):
                messages.error(request, "Demasiados intentos fallidos. Tu cuenta ha sido bloqueada temporalmente.")
                return render(request, 'usuarios/cuenta_bloqueada.html', {'form': form})

            usuario = AuthService.autenticar_usuario(request, correo, clave)
            if usuario:
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_nombre'] = usuario.nombre
                request.session['usuario_rol'] = usuario.id_rol.nombrerol if usuario.id_rol else None
                reset(ip=request.META.get('REMOTE_ADDR'))
                return redirect('panel_admin' if usuario.id_rol.nombrerol.lower() == 'admin' else 'dashboard')
            else:
                messages.error(request, "Correo o contraseña incorrectos.")
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {
        'form': form,
        'titulo': 'Inicio de sesión',
        'ocultar_navbar': True
    })

def logout_view(request):
    request.session.flush()
    request.session.clear_expired()
    return redirect('/')

def registro_view(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, "El correo ya está registrado.")
            else:
                try:
                    rol_user = Rol.objects.get(nombrerol='User')
                except Rol.DoesNotExist:
                    messages.error(request, "Error interno: rol no encontrado.")
                    return redirect('registro')

                token = TokenService.generar()
                usuario = AuthService.registrar_usuario(
                    nombre=form.cleaned_data['nombre'],
                    correo=correo,
                    clave=form.cleaned_data['clave'],
                    rol=rol_user
                )
                usuario.token = token
                usuario.save()

                url = request.build_absolute_uri(f"/confirmar/{token}/")
                html = render_to_string("correos/confirmacion_cuenta.html", {
                    'nombre': usuario.nombre,
                    'url_confirmacion': url
                })
                MailService.enviar_html(usuario.correo, "Confirma tu cuenta", html)

                messages.success(request, "Registro exitoso. Revisa tu correo.")
                return redirect('login')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {
        'form': form,
        'titulo': 'Registro',
        'ocultar_navbar': True
    })

def confirmar_cuenta(request, token):
    try:
        usuario = Usuario.objects.get(token=token)
        usuario.confirmado = True
        usuario.token = None
        usuario.fechatoken = None
        usuario.save()
        messages.success(request, "Cuenta confirmada con éxito. Ahora puedes iniciar sesión.")
    except Usuario.DoesNotExist:
        messages.error(request, "Token inválido o caducado.")
    return redirect('login')