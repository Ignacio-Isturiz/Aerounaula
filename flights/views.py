from django.shortcuts import render, redirect, get_object_or_404
from dbmodels.models.vuelos import Vuelos
from dbmodels.models.reserva import Reserva
from dbmodels.models.asiento import Asiento
from dbmodels.models.usuario import Usuario
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware, now
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib import messages


def vuelos_view(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    origenes = Vuelos.objects.values_list('origen', flat=True).distinct()
    destinos = Vuelos.objects.values_list('destino', flat=True).distinct()
    codigos = Vuelos.objects.values_list('codigo', flat=True).distinct()

    origen = request.GET.get('origen')
    destino = request.GET.get('destino')
    codigo = request.GET.get('codigo')
    fecha_salida = request.GET.get('fecha_salida')

    vuelos = Vuelos.objects.filter(estado='Disponible')
    if origen:
        vuelos = vuelos.filter(origen=origen)
    if destino:
        vuelos = vuelos.filter(destino=destino)
    if codigo:
        vuelos = vuelos.filter(codigo=codigo)
    if fecha_salida:
        vuelos = vuelos.filter(fecha_salida__date=fecha_salida)

    return render(request, 'vuelos.html', {
        'vuelos': vuelos,
        'origenes': origenes,
        'destinos': destinos,
        'codigos': codigos,
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'ocultar_navbar': False
    })

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

def editar_vuelo(request, codigo):
    vuelo = get_object_or_404(Vuelos, codigo=codigo)

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

def eliminar_vuelo(request, codigo):
    vuelo = get_object_or_404(Vuelos, codigo=codigo)
    if request.method == 'POST':
        vuelo.delete()
    return redirect('vuelos')

def reservar_vuelo(request, codigo):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    vuelo = get_object_or_404(Vuelos, codigo=codigo)

    ya_reservado = Reserva.objects.filter(id_usuario=usuario_id, vuelo=vuelo).exists()
    if not ya_reservado:
        Reserva.objects.create(id_usuario_id=usuario_id, vuelo=vuelo, fecha_reserva=timezone.now())

    return redirect('vuelos')

def mis_reservas(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    reservas = Reserva.objects.filter(id_usuario=usuario_id).select_related('vuelo')

    return render(request, 'mis_reservas.html', {
        'reservas': reservas,
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'ocultar_navbar': False
    })

@require_POST
def cancelar_reserva(request, id_reserva):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    reserva = get_object_or_404(Reserva, pk=id_reserva, id_usuario=usuario_id)
    reserva.delete()
    messages.success(request, "La reserva fue cancelada correctamente.")
    return redirect('mis_reservas')

def asignar_asientos(request, codigo):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    vuelo = get_object_or_404(Vuelos, codigo=codigo)

    if not Reserva.objects.filter(id_usuario=usuario_id, vuelo=vuelo).exists():
        return redirect('mis_reservas')

    asientos = Asiento.objects.filter(codigo=vuelo).order_by('asiento_numero')
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    asientos_usuario = asientos.filter(usuario_reservado=usuario)
    disponibles = asientos.filter(reservado=False)

    if request.method == 'POST':
        seleccionados_ids = list(map(int, request.POST.getlist('asientos')))
        nuevos = asientos.filter(id__in=seleccionados_ids, reservado=False)
        nuevos.update(reservado=True, usuario_reservado=usuario)
        desasignar = asientos_usuario.exclude(id__in=seleccionados_ids)
        desasignar_ids = list(desasignar.values_list('asiento_numero', flat=True))
        desasignar.update(reservado=False, usuario_reservado=None)
        nuevos_asientos = asientos.filter(id__in=seleccionados_ids, usuario_reservado=usuario).values_list('asiento_numero', flat=True)

        if nuevos_asientos:
            send_mail(
                subject='Asignación de asientos actualizada',
                message=f'Hola {usuario.nombre}, tus asientos para el vuelo {vuelo.origen} → {vuelo.destino} del {vuelo.fecha_salida.strftime("%d/%m/%Y %H:%M")} han sido actualizados. Nuevos asientos: {", ".join(nuevos_asientos)}.',
                from_email=None,
                recipient_list=[usuario.correo],
                fail_silently=False
            )

        if desasignar_ids:
            send_mail(
                subject='Cancelación de asientos',
                message=f'Hola {usuario.nombre}, has cancelado la reserva de los siguientes asientos para el vuelo {vuelo.origen} → {vuelo.destino} del {vuelo.fecha_salida.strftime("%d/%m/%Y %H:%M")}: {", ".join(desasignar_ids)}.',
                from_email=None,
                recipient_list=[usuario.correo],
                fail_silently=False
            )

        return redirect('mis_reservas')

    return render(request, 'asignar_asientos.html', {
        'vuelo': vuelo,
        'asientos': asientos,
        'disponibles': disponibles,
        'asientos_usuario': asientos_usuario
    })
