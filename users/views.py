import secrets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.template.loader import render_to_string
from dbmodels.models.usuario import Usuario, Rol
from dbmodels.models.vuelos import Vuelos
from .forms import LoginForm, RegistroForm, RecuperarClaveForm, RestablecerClaveForm
from django.utils.timezone import make_aware
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from axes.utils import reset 
from django.contrib.auth.hashers import check_password
from axes.handlers.proxy import AxesProxyHandler
from django.http import HttpResponse


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
            if AxesProxyHandler().is_locked(request):
                messages.error(request, "Demasiados intentos fallidos. Tu cuenta ha sido bloqueada temporalmente.")
                return render(request, 'usuarios/cuenta_bloqueada.html', {
                    'form': form,
                    'titulo': 'Inicio de sesión',
                    'ocultar_navbar': False
                })
            
            usuario = authenticate(request, correo=correo, clave=clave)
            if usuario is not None:
                # Asegura que estás trabajando con un modelo actualizado
                usuario_db = Usuario.objects.get(pk=usuario.id_usuario)
                rol_nombre = usuario_db.id_rol.nombrerol if usuario_db.id_rol else None

                reset(ip=request.META.get('REMOTE_ADDR'))

                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_nombre'] = usuario.nombre
                request.session['usuario_rol'] = rol_nombre  

                if rol_nombre and rol_nombre.lower() == 'admin':
                    return redirect('panel_admin') 
                else:
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
                try:
                    rol_user = Rol.objects.get(nombrerol='User')
                except Rol.DoesNotExist:
                    messages.error(request, "Error interno: no se encontró el rol 'User'. Contacta al administrador.")
                    return redirect('registro')

                token = generar_token()

                nuevo_usuario = Usuario(
                    nombre=form.cleaned_data['nombre'],
                    correo=correo,
                    clave=make_password(form.cleaned_data['clave']),
                    estado=True,
                    confirmado=False,
                    token=token,
                    fechatoken=timezone.now(),
                    id_rol=rol_user
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

    return render(request, 'usuarios/registro.html', {
        'form': form,
        'titulo': 'Registro',
        'ocultar_navbar': True
    })

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
    usuario_rol = request.session.get('usuario_rol')

    # Extraer ciudades únicas de origen y destino
    origenes = Vuelos.objects.values_list('origen', flat=True).distinct()
    destinos = Vuelos.objects.values_list('destino', flat=True).distinct()

    context = {
        'logueado': bool(usuario_id),
        'usuario_nombre': usuario_nombre,
        'usuario_rol': usuario_rol,
        'origenes': origenes,
        'destinos': destinos,
        'ocultar_navbar': False,
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

#------------------------ MI CUENTA ----------------------------------------
def mi_cuenta(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario = get_object_or_404(Usuario, id_usuario=request.session['usuario_id'])
    
    if request.method == 'POST' and 'delete_account' in request.POST:
        # Lógica para eliminar la cuenta
        usuario.estado = False  # O puedes usar usuario.delete() para eliminación permanente
        usuario.save()
        messages.success(request, "Cuenta desactivada exitosamente")
        return logout_view(request)  # Cierra la sesión después de eliminar
    context = {
        'usuario': usuario,
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'ocultar_navbar': False
    }
    return render(request, 'usuarios/mi_cuenta.html', context)



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
