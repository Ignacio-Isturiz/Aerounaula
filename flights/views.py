from django.shortcuts import render, redirect, get_object_or_404
from dbmodels.models.vuelos import Vuelos
from dbmodels.models.reserva import Reserva
from django.utils import timezone

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
def crear_vuelo(request):
    if request.method == 'POST':
        Vuelos.objects.create(
            origen=request.POST['origen'],
            destino=request.POST['destino'],
            fecha_salida=request.POST['fecha_salida'],
            precio=request.POST['precio'],
            estado=request.POST.get('estado', ''),
            imagen_url=request.POST.get('imagen_url', '')
        )
        return redirect('vuelos')
    return render(request, 'crear.html', {'vuelo': None})

def editar_vuelo(request, id_vuelo):
    vuelo = get_object_or_404(Vuelos, pk=id_vuelo)
    if request.method == 'POST':
        vuelo.origen = request.POST['origen']
        vuelo.destino = request.POST['destino']
        vuelo.fecha_salida = request.POST['fecha_salida']
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