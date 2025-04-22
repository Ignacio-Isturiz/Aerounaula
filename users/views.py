import secrets
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.template.loader import render_to_string
from dbmodels.models.usuario import Usuario
from .forms import LoginForm, RegistroForm, RecuperarClaveForm, RestablecerClaveForm
from django.utils.timezone import make_aware
from django.http import HttpResponseRedirect
from dbmodels.models.vuelos import Vuelos
from django.contrib.auth import authenticate
from axes.utils import reset 

# ---------------------- GENERAR TOKEN ----------------------

def generar_token():
    return secrets.token_urlsafe(32)

# ---------------------- LOGIN ----------------------

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            clave = form.cleaned_data['clave']

            from axes.handlers.proxy import AxesProxyHandler
            if AxesProxyHandler().is_locked(request):
                messages.error(request, "Demasiados intentos fallidos. Tu cuenta ha sido bloqueada temporalmente.")
                return render(request, 'usuarios/login.html', {
                    'form': form,
                    'titulo': 'Inicio de sesión',
                    'ocultar_navbar': True
                })


            usuario = authenticate(request, correo=correo, clave=clave)

            if usuario is not None:
                reset(ip=request.META.get('REMOTE_ADDR'))


                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_nombre'] = usuario.nombre
                return redirect('dashboard')
            else:
                messages.error(request, "Correo o contraseña incorrectos.")
        else:
            messages.error(request, "Formulario no válido.")
    else:
        form = LoginForm()

    context = {
        'form': form,
        'titulo': 'Inicio de sesión',
        'ocultar_navbar': True
    }
    return render(request, 'usuarios/login.html', context)

# ---------------------- REGISTRO ----------------------
def registro_view(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, "El correo ya está registrado.")
            else:
                token = generar_token()
                nuevo_usuario = Usuario(
                    nombre=form.cleaned_data['nombre'],
                    correo=correo,
                    clave=make_password(form.cleaned_data['clave']),
                    estado=True,
                    confirmado=False,
                    token=token,
                    fechatoken=timezone.now()
                )
                nuevo_usuario.save()

                url_confirmacion = request.build_absolute_uri(f"/confirmar/{token}/")
                html_content = render_to_string('correos/confirmacion_cuenta.html', {
                    'nombre': nuevo_usuario.nombre,
                    'url_confirmacion': url_confirmacion
                })
                send_mail(
                    subject="Confirma tu cuenta",
                    message="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[correo],
                    html_message=html_content
                )

                messages.success(request, "Registro exitoso. Revisa tu correo para confirmar tu cuenta.")
                return redirect('login')
    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {'form': form, 'titulo': 'Registro', 'ocultar_navbar': True})


# ---------------------- CONFIRMACIÓN DE CUENTA ----------------------
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


# ---------------------- DASHBOARD Y LOGOUT ----------------------
def dashboard(request):
    usuario_id = request.session.get('usuario_id')
    usuario_nombre = request.session.get('usuario_nombre')

    context = {
        'logueado': bool(usuario_id),
        'usuario_nombre': usuario_nombre,
        'ocultar_navbar': False
    }

    response = render(request, 'usuarios/dashboard.html', context)
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def logout_view(request):
    request.session.flush()
    request.session.clear_expired()

    response = HttpResponseRedirect('/')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


# ---------------------- RECUPERAR CLAVE ----------------------
def recuperar_clave(request):
    if request.method == 'POST':
        form = RecuperarClaveForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            try:
                usuario = Usuario.objects.get(correo=correo)
                token = generar_token()
                usuario.token = token
                usuario.fechatoken = timezone.now()
                usuario.save()

                enlace = request.build_absolute_uri(f"/restablecer/{token}/")
                html_content = render_to_string('correos/restablecer_clave.html', {
                    'nombre': usuario.nombre,
                    'url_reset': enlace
                })
                send_mail(
                    subject="Recuperación de contraseña",
                    message="",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[usuario.correo],
                    html_message=html_content
                )

                messages.success(request, "Correo enviado con instrucciones para restablecer la contraseña.")
                return redirect('login')
            except Usuario.DoesNotExist:
                messages.error(request, "El correo no está registrado.")
    else:
        form = RecuperarClaveForm()

    return render(request, 'usuarios/recuperar_clave.html', {'form': form, 'titulo': 'Recuperar contraseña', 'ocultar_navbar': True})


# ---------------------- RESTABLECER CONTRASEÑA ----------------------
def restablecer_clave(request, token):
    try:
        usuario = Usuario.objects.get(token=token)
    except Usuario.DoesNotExist:
        messages.error(request, "Enlace inválido o caducado.")
        return redirect('login')

    tiempo_actual = timezone.now()
    tiempo_expiracion = make_aware(usuario.fechatoken) + timezone.timedelta(hours=24)

    if tiempo_actual > tiempo_expiracion:
        messages.error(request, "El enlace ha expirado. Solicita uno nuevo.")
        return redirect('recuperar_clave')

    if request.method == 'POST':
        form = RestablecerClaveForm(request.POST)
        if form.is_valid():
            nueva = form.cleaned_data['nueva_clave']
            usuario.clave = make_password(nueva)
            usuario.token = None
            usuario.fechatoken = None
            usuario.save()
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('login')
    else:
        form = RestablecerClaveForm()

    return render(request, 'usuarios/restablecer_contraseña.html', {'form': form, 'titulo': 'Restablecer contraseña', 'ocultar_navbar': True})


# ---------------------- VER VUELOS ----------------------
def vuelos_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    vuelos = Vuelos.objects.filter(estado='Disponible')
    context = {
        'vuelos': vuelos,
        'usuario_nombre': request.session.get('usuario_nombre'),
        'ocultar_navbar': False
    }
    return render(request, 'usuarios/vuelos.html', context)
