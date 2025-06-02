from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from dbmodels.models import Reserva, Usuario, Vuelos
from Aerounaula import settings

class ManageReservationsView(View):
    def get(self, request):
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

class CreateReservationView(View):
    def post(self, request):
        try:
            usuario = get_object_or_404(Usuario, id_usuario=request.POST.get('id_usuario'))
            vuelo = get_object_or_404(Vuelos, codigo=request.POST.get('vuelo_codigo'))
            Reserva.objects.create(id_usuario=usuario, vuelo=vuelo)
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Error al crear reserva: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

class EditReservationView(View):
    def post(self, request, reservation_id):
        reserva = get_object_or_404(Reserva, id_reserva=reservation_id)
        try:
            vuelo = get_object_or_404(Vuelos, codigo=request.POST.get('vuelo_codigo'))
            reserva.vuelo = vuelo
            reserva.save()
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Error al actualizar reserva: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

class CancelReservationView(View):
    def post(self, request, reservation_id):
        reserva = get_object_or_404(Reserva, id_reserva=reservation_id)
        try:
            motivo = request.POST.get('motivo', 'Cancelación administrativa')
            reserva.estado = 'cancelada'
            reserva.motivo_cancelacion = motivo
            reserva.save()

            send_mail(
                'Cancelación de tu reserva',
                f'Hola {reserva.id_usuario.nombre},\n\nTu reserva #{reserva.id_reserva} ha sido cancelada.\nMotivo: {motivo}\n\nEquipo de Aerolínea',
                settings.DEFAULT_FROM_EMAIL,
                [reserva.id_usuario.correo],
                fail_silently=False,
            )
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Error al cancelar reserva: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

class DeleteReservationView(View):
    def post(self, request, reservation_id):
        reserva = get_object_or_404(Reserva, id_reserva=reservation_id)
        try:
            reserva.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request, f'Error al eliminar reserva: {str(e)}')
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
