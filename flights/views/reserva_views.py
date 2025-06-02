from django.views import View
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from dbmodels.models.vuelos import Vuelos
from dbmodels.models.reserva import Reserva
from dbmodels.models.usuario import Usuario
from django.utils import timezone

class ReservarVueloView(View):
    def get(self, request, codigo):
        if not request.session.get('usuario_id'):
            return redirect('login')

        usuario_id = request.session['usuario_id']
        vuelo = get_object_or_404(Vuelos, codigo=codigo)

        if Reserva.objects.filter(id_usuario=usuario_id, vuelo=vuelo).exists():
            messages.warning(request, 'Ya tienes una reserva para este vuelo.')
        else:
            Reserva.objects.create(id_usuario_id=usuario_id, vuelo=vuelo, fecha_reserva=timezone.now())
            messages.success(request, '¡Vuelo reservado con éxito!')

        return redirect('vuelos')

class MisReservasView(View):
    def get(self, request):
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

class CancelarReservaView(View):
    def post(self, request, id_reserva):
        if not request.session.get('usuario_id'):
            return redirect('login')

        usuario_id = request.session['usuario_id']
        reserva = get_object_or_404(Reserva, pk=id_reserva, id_usuario=usuario_id)
        reserva.delete()
        messages.success(request, "La reserva fue cancelada correctamente.")
        return redirect('mis_reservas')
