from django.shortcuts import render, redirect, get_object_or_404
from dbmodels.models.vuelos import Vuelos
from dbmodels.models.reserva import Reserva
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.dateparse import parse_datetime
from dbmodels.models.asiento import Asiento 
from dbmodels.models.usuario import Usuario
from django.contrib import messages
from django.utils.timezone import make_aware, now
from django.views.decorators.http import require_POST

def asignar_asientos(request, id_vuelo):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    vuelo = get_object_or_404(Vuelos, pk=id_vuelo)

    if not Reserva.objects.filter(id_usuario=usuario_id, id_vuelo=vuelo).exists():
        return redirect('mis_reservas')

    asientos = Asiento.objects.filter(vuelo=vuelo).order_by('asiento_numero')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    # Asientos actualmente asignados al usuario
    asientos_usuario = asientos.filter(usuario_reservado=usuario)
    disponibles = asientos.filter(reservado=False)

    if request.method == 'POST':
        seleccionados_ids = list(map(int, request.POST.getlist('asientos')))

        # Asientos que el usuario acaba de seleccionar
        nuevos = asientos.filter(id__in=seleccionados_ids, reservado=False)
        nuevos.update(reservado=True, usuario_reservado=usuario)

        # Asientos que el usuario tenía pero quitó
        desasignar = asientos_usuario.exclude(id__in=seleccionados_ids)
        desasignar_ids = list(desasignar.values_list('asiento_numero', flat=True))
        desasignar.update(reservado=False, usuario_reservado=None)

        # Asientos actualmente asignados después de actualizar
        nuevos_asientos = asientos.filter(id__in=seleccionados_ids, usuario_reservado=usuario)\
                                  .values_list('asiento_numero', flat=True)

        # Enviar correo si hay nuevos asientos
        if nuevos_asientos:
            send_mail(
                subject='Asignación de asientos actualizada',
                message=(
                    f'Hola {usuario.nombre},\n\nTus asientos para el vuelo {vuelo.origen} → {vuelo.destino} '
                    f'del {vuelo.fecha_salida.strftime("%d/%m/%Y %H:%M")} han sido actualizados.\n'
                    f'Nuevos asientos: {", ".join(nuevos_asientos)}.\n\nGracias.'
                ),
                from_email=None,
                recipient_list=[usuario.email],
                fail_silently=False
            )

        # Enviar correo si hubo desasignaciones
        if desasignar_ids:
            send_mail(
                subject='Cancelación de asientos',
                message=(
                    f'Hola {usuario.nombre},\n\nHas cancelado tu reserva de los siguientes asientos para el vuelo '
                    f'{vuelo.origen} → {vuelo.destino} del {vuelo.fecha_salida.strftime("%d/%m/%Y %H:%M")}:\n'
                    f'{", ".join(desasignar_ids)}.\n\nSi fue un error, puedes volver a asignarlos antes del vuelo.'
                ),
                from_email=None,
                recipient_list=[usuario.email],
                fail_silently=False
            )

        return redirect('mis_reservas')

    return render(request, 'asignar_asientos.html', {
        'vuelo': vuelo,
        'asientos': asientos,
        'disponibles': disponibles,
        'asientos_usuario': asientos_usuario
    })

    
def vuelos_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    # Obtener valores únicos para los filtros
    origenes = Vuelos.objects.values_list('origen', flat=True).distinct()
    destinos = Vuelos.objects.values_list('destino', flat=True).distinct()

    # Obtener los filtros desde GET
    origen = request.GET.get('origen')
    destino = request.GET.get('destino')
    fecha_salida = request.GET.get('fecha_salida')

    vuelos = Vuelos.objects.filter(estado='Disponible')

    # Aplicar filtros si existen
    if origen:
        vuelos = vuelos.filter(origen=origen)
    if destino:
        vuelos = vuelos.filter(destino=destino)
    if fecha_salida:
        vuelos = vuelos.filter(fecha_salida=fecha_salida)

    context = {
        'vuelos': vuelos,
        'origenes': origenes,
        'destinos': destinos,
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'ocultar_navbar': False
    }
    return render(request, 'vuelos.html', context)


def reservar_vuelo(request, id_vuelo):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    vuelo = get_object_or_404(Vuelos, pk=id_vuelo)

    # Verificar si el usuario ya ha reservado este vuelo
    ya_reservado = Reserva.objects.filter(id_usuario=usuario_id, id_vuelo=id_vuelo).exists()
    if not ya_reservado:
        Reserva.objects.create(id_usuario_id=usuario_id, id_vuelo=vuelo, fecha_reserva=timezone.now())

    return redirect('vuelos')

def mis_reservas(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    reservas = Reserva.objects.filter(id_usuario=usuario_id).select_related('id_vuelo')

    context = {
        'reservas': reservas,
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'ocultar_navbar': False
    }
    return render(request, 'mis_reservas.html', context)

@require_POST
def cancelar_reserva(request, id_reserva):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    reserva = get_object_or_404(Reserva, pk=id_reserva, id_usuario=usuario_id)

    reserva.delete()
    messages.success(request, "La reserva fue cancelada correctamente.")
    return redirect('mis_reservas')


def crear_vuelo(request):
    if request.method == 'POST':
        fecha_salida_str = request.POST['fecha_salida']
        fecha_salida = parse_datetime(fecha_salida_str)

        if fecha_salida is None:
            messages.error(request, "Formato de fecha inválido.")
            return redirect('vuelos')

        if timezone.is_naive(fecha_salida):
            fecha_salida = make_aware(fecha_salida)

        if fecha_salida < now():
            messages.error(request, "No puedes crear un vuelo con una fecha pasada.")
            return redirect('vuelos')

        Vuelos.objects.create(
            origen=request.POST['origen'],
            destino=request.POST['destino'],
            fecha_salida=fecha_salida,
            precio=request.POST['precio'],
            estado=request.POST.get('estado', ''),
            imagen_url=request.POST.get('imagen_url', '')
        )
        return redirect('vuelos')

    return render(request, 'crear.html', {'vuelo': None})

def editar_vuelo(request, id_vuelo):
    vuelo = get_object_or_404(Vuelos, pk=id_vuelo)

    if request.method == 'POST':
        fecha_salida_str = request.POST['fecha_salida']
        fecha_salida = parse_datetime(fecha_salida_str)

        if fecha_salida is None:
            messages.error(request, "Formato de fecha inválido.")
            return redirect('vuelos')

        if timezone.is_naive(fecha_salida):
            fecha_salida = make_aware(fecha_salida)

        if fecha_salida < now():
            messages.error(request, "No puedes establecer una fecha pasada para este vuelo.")
            return redirect('vuelos')

        vuelo.origen = request.POST['origen']
        vuelo.destino = request.POST['destino']
        vuelo.fecha_salida = fecha_salida
        vuelo.precio = request.POST['precio']
        vuelo.estado = request.POST.get('estado', '')
        vuelo.imagen_url = request.POST.get('imagen_url', '')
        vuelo.save()
        return redirect('vuelos')

    return render(request, 'crear.html', {'vuelo': vuelo})


def eliminar_vuelo(request, id_vuelo):
    vuelo = get_object_or_404(Vuelos, pk=id_vuelo)
    if request.method == 'POST':
        vuelo.delete()
    return redirect('vuelos')