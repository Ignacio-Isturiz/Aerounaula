# paneladmin/views.py
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from dbmodels.models import Usuario, Rol,Vuelos, Reserva, Asiento
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from Aerounaula import settings
from django.core.mail import send_mail

def panel_admin_view(request):
    rol = request.session.get('usuario_rol')  
    if rol != 'Admin':
        return redirect('dashboard')
    return render(request, 'paneladmin/panel.html', {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'titulo': 'Panel de Administración'
    })

def logout_view(request):
    request.session.flush()
    request.session.clear_expired()

    response = HttpResponseRedirect('/')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def my_profile_view(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')
    
    try:
        usuario = Usuario.objects.get(id_usuario=usuario_id)
    except Usuario.DoesNotExist:
        messages.error(request, "Usuario no encontrado")
        return redirect('login')
    
    if request.method == 'POST' and 'delete_account' in request.POST:
        usuario.estado = False  
        usuario.save()
        messages.success(request, "Cuenta desactivada exitosamente")
        return logout_view(request)  

    context = {
        'usuario': usuario,
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'titulo': 'Mi Perfil'
    }
    return render(request, 'paneladmin/my_profile.html', context)

def manage_users_view(request):
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

#------------------------------Users-------------------------------------

def create_user_view(request):
    if request.method == 'POST':
        try:
            Usuario.objects.create(
                nombre=request.POST.get('nombre'),
                correo=request.POST.get('correo'),
                clave=request.POST.get('clave'),  # En producción, hashear la contraseña
                id_rol_id=request.POST.get('id_rol'),
                estado=True
            )
            messages.success(request, 'Usuario creado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear usuario: {str(e)}')
    return redirect('manage_users')

def edit_user_view(request, user_id):
    usuario = get_object_or_404(Usuario, id_usuario=user_id)
    if request.method == 'POST':
        try:
            usuario.nombre = request.POST.get('nombre')
            usuario.correo = request.POST.get('correo')
            usuario.id_rol_id = request.POST.get('id_rol')
            usuario.estado = request.POST.get('estado') == 'on'
            usuario.save()
            messages.success(request, 'Usuario actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar usuario: {str(e)}')
    return redirect('manage_users')

def delete_user_view(request, user_id):
    usuario = get_object_or_404(Usuario, id_usuario=user_id)
    if request.method == 'POST':
        try:
            usuario.delete()
            messages.success(request, 'Usuario eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar usuario: {str(e)}')
    return redirect('manage_users')

#<------------------------------ gestion de vuelos----------------------------->

def manage_flights_view(request):
    if request.session.get('usuario_rol') != 'Admin':
        return redirect('dashboard')
    
    vuelos = Vuelos.objects.all().order_by('fecha_salida')
    
    context = {
        'vuelos': vuelos,
        'titulo': 'Gestión de Vuelos'
    }
    return render(request, 'paneladmin/manage_flights.html', context)

def create_flight_view(request):
    if request.method == 'POST':
        try:
            Vuelos.objects.create(
                codigo=request.POST.get('codigo'),
                origen=request.POST.get('origen'),
                destino=request.POST.get('destino'),
                fecha_salida=request.POST.get('fecha_salida'),
                precio=request.POST.get('precio'),
                estado=request.POST.get('estado'),
                imagen_url=request.POST.get('imagen_url')
            )
            messages.success(request, 'Vuelo creado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al crear vuelo: {str(e)}')
    return redirect('manage_flights')

def edit_flight_view(request, flight_code):
    vuelo = get_object_or_404(Vuelos, codigo=flight_code)
    if request.method == 'POST':
        try:
            vuelo.origen = request.POST.get('origen')
            vuelo.destino = request.POST.get('destino')
            vuelo.fecha_salida = request.POST.get('fecha_salida')
            vuelo.precio = request.POST.get('precio')
            vuelo.estado = request.POST.get('estado')
            vuelo.imagen_url = request.POST.get('imagen_url')
            vuelo.save()
            messages.success(request, 'Vuelo actualizado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al actualizar vuelo: {str(e)}')
    return redirect('manage_flights')

def delete_flight_view(request, flight_code):
    vuelo = get_object_or_404(Vuelos, codigo=flight_code)
    if request.method == 'POST':
        try:
            vuelo.delete()
            messages.success(request, 'Vuelo eliminado exitosamente')
        except Exception as e:
            messages.error(request, f'Error al eliminar vuelo: {str(e)}')
    return redirect('manage_flights')

#<-------------------------------------reservas--------------------------------------------------->

def manage_reservations_view(request):
    if request.session.get('usuario_rol') != 'Admin':
        return redirect('dashboard')
    
    reservas = Reserva.objects.select_related('id_usuario', 'vuelo').all().order_by('-fecha_reserva')
    usuarios = Usuario.objects.filter(estado=True)
    vuelos = Vuelos.objects.filter(estado='Disponible')
    
    context = {
        'reservas': reservas,
        'usuarios': usuarios,
        'vuelos': vuelos,
        'titulo': 'Gestión de Reservas'
    }
    return render(request, 'paneladmin/manage_reservations.html', context)

def create_reservation_view(request):
    if request.method == 'POST':
        try:
            usuario = get_object_or_404(Usuario, id_usuario=request.POST.get('id_usuario'))
            vuelo = get_object_or_404(Vuelos, codigo=request.POST.get('vuelo_codigo'))
            
            Reserva.objects.create(
                id_usuario=usuario,
                vuelo=vuelo
            )
            messages.success(request, 'Reserva creada exitosamente')
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Error al crear reserva: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def edit_reservation_view(request, reservation_id):
    reserva = get_object_or_404(Reserva, id_reserva=reservation_id)
    if request.method == 'POST':
        try:
            vuelo = get_object_or_404(Vuelos, codigo=request.POST.get('vuelo_codigo'))
            reserva.vuelo = vuelo
            reserva.save()
            messages.success(request, 'Reserva actualizada exitosamente')
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Error al actualizar reserva: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def cancel_reservation_view(request, reservation_id):
    reserva = get_object_or_404(Reserva, id_reserva=reservation_id)
    if request.method == 'POST':
        try:
            motivo = request.POST.get('motivo', 'Cancelación administrativa')
            reserva.estado = 'cancelada'
            reserva.motivo_cancelacion = motivo
            reserva.save()
            
            # Enviar email de cancelación
            send_mail(
                'Cancelación de tu reserva',
                f'Hola {reserva.id_usuario.nombre},\n\nTu reserva #{reserva.id_reserva} ha sido cancelada.\nMotivo: {motivo}\n\nEquipo de Aerolínea',
                settings.DEFAULT_FROM_EMAIL,
                [reserva.id_usuario.correo],
                fail_silently=False,
            )
            
            messages.success(request, 'Reserva cancelada y usuario notificado')
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Error al cancelar reserva: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def delete_reservation_view(request, reservation_id):
    reserva = get_object_or_404(Reserva, id_reserva=reservation_id)
    if request.method == 'POST':
        try:
            reserva.delete()
            messages.success(request, 'Reserva eliminada exitosamente')
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Error al eliminar reserva: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

#<---------------------- Asientos ----------------------------->
def manage_seats_view(request):
    if request.session.get('usuario_rol') != 'Admin':
        return redirect('dashboard')
    
    asientos = Asiento.objects.select_related('codigo', 'usuario_reservado')\
    .all().order_by('-reservado', 'codigo__codigo', 'asiento_numero')
    vuelos = Vuelos.objects.all()
    usuarios = Usuario.objects.all()

    context = {
        'asientos': asientos,
        'vuelos': vuelos,
        'usuarios': usuarios,
        'titulo': 'Gestión de Asientos'
    }
    return render(request, 'paneladmin/manage_seats.html', context)

def create_seat_view(request):
    if request.method == 'POST':
        try:
            vuelo = get_object_or_404(Vuelos, codigo=request.POST.get('vuelo_codigo'))
            asiento_numero = request.POST.get('asiento_numero')
            reservado = request.POST.get('reservado') == 'on'
            usuario_id = request.POST.get('usuario_reservado') or None

            if usuario_id:
                asiento_existente = Asiento.objects.filter(codigo=vuelo, usuario_reservado_id=usuario_id).first()
                if asiento_existente:
                    asiento_existente.asiento_numero = asiento_numero
                    asiento_existente.reservado = reservado
                    asiento_existente.save()
                    asiento = asiento_existente
                else:
                    asiento = Asiento.objects.create(
                        codigo=vuelo,
                        asiento_numero=asiento_numero,
                        reservado=reservado,
                        usuario_reservado_id=usuario_id
                    )
                usuario = Usuario.objects.filter(id_usuario=usuario_id).first()
            else:
                asiento = Asiento.objects.create(
                    codigo=vuelo,
                    asiento_numero=asiento_numero,
                    reservado=reservado,
                    usuario_reservado=None
                )
                usuario = None

            if usuario:
                send_mail(
                    'Reserva de asiento',
                    f'Hola {usuario.nombre}, se te ha asignado el asiento {asiento.asiento_numero} en el vuelo {vuelo.codigo}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [usuario.correo],
                    fail_silently=True
                )

            messages.success(request, 'Asiento creado o actualizado exitosamente.')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        return redirect('manage_seats')

def edit_seat_view(request, seat_id):
    asiento = get_object_or_404(Asiento, id=seat_id)
    if request.method == 'POST':
        try:
            vuelo = get_object_or_404(Vuelos, codigo=request.POST.get('vuelo_codigo'))
            asiento.codigo = vuelo
            asiento.asiento_numero = request.POST.get('asiento_numero')
            asiento.reservado = request.POST.get('reservado') == 'on'
            usuario_id = request.POST.get('usuario_reservado') or None
            asiento.usuario_reservado_id = usuario_id
            asiento.save()

            usuario = Usuario.objects.filter(id_usuario=usuario_id).first() if usuario_id else None
            if usuario:
                send_mail(
                    'Asiento modificado',
                    f'Hola {usuario.nombre}, tu asiento ha sido actualizado a {asiento.asiento_numero} en el vuelo {asiento.codigo.codigo}.',
                    settings.DEFAULT_FROM_EMAIL,
                    [usuario.correo],
                    fail_silently=True
                )

            messages.success(request, 'Asiento actualizado exitosamente.')
            return redirect('manage_seats')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('manage_seats')

    vuelos = Vuelos.objects.all()
    usuarios = Usuario.objects.all()
    return render(request, 'paneladmin/edit_seat.html', {
        'asiento': asiento,
        'vuelos': vuelos,
        'usuarios': usuarios,
        'titulo': 'Editar Asiento'
    })

def delete_seat_view(request, seat_id):
    asiento = get_object_or_404(Asiento, id=seat_id)
    if request.method == 'POST':
        usuario = asiento.usuario_reservado
        # En lugar de eliminar el asiento, solo quitar la asignación:
        asiento.usuario_reservado = None
        asiento.reservado = False
        asiento.save()

        if usuario:
            send_mail(
                'Asignación de asiento eliminada',
                f'Hola {usuario.nombre}, la asignación del asiento que tenías reservado ha sido eliminada.',
                settings.DEFAULT_FROM_EMAIL,
                [usuario.correo],
                fail_silently=True
            )

        messages.success(request, 'Asignación del asiento eliminada correctamente.')
    return redirect('manage_seats')

