from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib.auth.hashers import make_password

from dbmodels.models.usuario import Usuario
from users.forms import RecuperarClaveForm, RestablecerClaveForm
from users.services.token_service import TokenService
from users.services.mail_service import MailService

def recuperar_clave(request):
    if request.method == 'POST':
        form = RecuperarClaveForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            try:
                usuario = Usuario.objects.get(correo=correo)
                token = TokenService.generar()
                usuario.token = token
                usuario.fechatoken = timezone.now()
                usuario.save()

                enlace = request.build_absolute_uri(f"/restablecer/{token}/")
                html = render_to_string('correos/restablecer_clave.html', {
                    'nombre': usuario.nombre,
                    'url_reset': enlace
                })
                MailService.enviar_html(correo, "Recuperación de contraseña", html)
                messages.success(request, "Correo enviado con instrucciones para restablecer la contraseña.")
                return redirect('login')
            except Usuario.DoesNotExist:
                messages.error(request, "El correo no está registrado.")
    else:
        form = RecuperarClaveForm()

    return render(request, 'usuarios/recuperar_clave.html', {
        'form': form,
        'titulo': 'Recuperar contraseña',
        'ocultar_navbar': True
    })

def restablecer_clave(request, token):
    try:
        usuario = Usuario.objects.get(token=token)
    except Usuario.DoesNotExist:
        messages.error(request, "Enlace inválido o caducado.")
        return redirect('login')

    if timezone.now() > make_aware(usuario.fechatoken) + timezone.timedelta(hours=24):
        messages.error(request, "El enlace ha expirado.")
        return redirect('recuperar_clave')

    if request.method == 'POST':
        form = RestablecerClaveForm(request.POST)
        if form.is_valid():
            usuario.clave = make_password(form.cleaned_data['nueva_clave'])
            usuario.token = None
            usuario.fechatoken = None
            usuario.save()
            messages.success(request, "Contraseña actualizada correctamente.")
            return redirect('login')
    else:
        form = RestablecerClaveForm()

    return render(request, 'usuarios/restablecer_contraseña.html', {
        'form': form,
        'titulo': 'Restablecer contraseña',
        'ocultar_navbar': True
    })