from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from dbmodels.models import Vuelos
from unidecode import unidecode


def normalize(texto):
    return unidecode(texto).lower()

class ManageFlightsView(View):
    def get(self, request):
        if request.session.get('usuario_rol') != 'Admin':
            return redirect('dashboard')

        vuelos = Vuelos.objects.all()
        origenes = sorted(set(vuelos.values_list('origen', flat=True)))
        destinos = sorted(set(vuelos.values_list('destino', flat=True)))

        origen = request.GET.get('origen')
        destino = request.GET.get('destino')
        estado = request.GET.get('estado')

        if origen:
            vuelos = [v for v in vuelos if normalize(v.origen) == normalize(origen)]
        if destino:
            vuelos = [v for v in vuelos if normalize(v.destino) == normalize(destino)]
        if estado:
            vuelos = [v for v in vuelos if v.estado == estado]

        context = {
            'vuelos': vuelos,
            'titulo': 'Gestión de Vuelos',
            'filtros': {
                'origen': origen or '',
                'destino': destino or '',
                'estado': estado or '',
            },
            'origenes': origenes,
            'destinos': destinos,
        }
        return render(request, 'paneladmin/manage_flights.html', context)

class CreateFlightView(View):
    def post(self, request):
        try:
            Vuelos.objects.create(
                origen=request.POST.get('origen'),
                destino=request.POST.get('destino'),
                fecha_salida=request.POST.get('fecha_salida'),
                precio=request.POST.get('precio'),
                estado=request.POST.get('estado'),
                imagen_url=request.POST.get('imagen_url')
            )
        except Exception as e:
            messages.error(request, f'Error al crear vuelo: {str(e)}')
        return redirect('manage_flights')

class EditFlightView(View):
    def post(self, request, flight_code):
        vuelo = get_object_or_404(Vuelos, codigo=flight_code)
        try:
            vuelo.origen = request.POST.get('origen')
            vuelo.destino = request.POST.get('destino')
            vuelo.fecha_salida = request.POST.get('fecha_salida')
            vuelo.precio = request.POST.get('precio')
            vuelo.estado = request.POST.get('estado')
            vuelo.imagen_url = request.POST.get('imagen_url')
            vuelo.save()
        except Exception as e:
            messages.error(request, f'Error al actualizar vuelo: {str(e)}')
        return redirect('manage_flights')

class DeleteFlightView(View):
    def post(self, request, flight_code):
        vuelo = get_object_or_404(Vuelos, codigo=flight_code)
        try:
            vuelo.delete()
        except Exception as e:
            messages.error(request, f'Error al eliminar vuelo: {str(e)}')
        return redirect('manage_flights')
