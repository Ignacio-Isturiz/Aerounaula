from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from dbmodels.models import Asiento, Vuelos, Usuario
from Aerounaula import settings

class ManageSeatsView(View):
    def get(self, request):
        if request.session.get('usuario_rol') != 'Admin':
            return redirect('dashboard')

        vuelo_codigo = request.GET.get('vuelo')
        usuario_id = request.GET.get('usuario')

        asientos = Asiento.objects.select_related('codigo', 'usuario_reservado').all()

        if vuelo_codigo:
            asientos = asientos.filter(codigo__codigo__icontains=vuelo_codigo)
        if usuario_id:
            asientos = asientos.filter(usuario_reservado__id_usuario=usuario_id)

        asientos = asientos.order_by('-reservado', 'codigo__codigo', 'asiento_numero')

        vuelos = Vuelos.objects.all()
        usuarios = Usuario.objects.all()

        context = {
            'asientos': asientos,
            'vuelos': vuelos,
            'usuarios': usuarios,
            'titulo': 'Gestión de Asientos',
            'vuelo_codigo': vuelo_codigo or '',
            'usuario_id': usuario_id or ''
        }
        return render(request, 'paneladmin/manage_seats.html', context)

class CreateSeatView(View):
    def post(self, request):
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
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        return redirect('manage_seats')

class EditSeatView(View):
    def get(self, request, seat_id):
        asiento = get_object_or_404(Asiento, id=seat_id)
        vuelos = Vuelos.objects.all()
        usuarios = Usuario.objects.all()
        return render(request, 'paneladmin/edit_seat.html', {
            'asiento': asiento,
            'vuelos': vuelos,
            'usuarios': usuarios,
            'titulo': 'Editar Asiento'
        })

    def post(self, request, seat_id):
        asiento = get_object_or_404(Asiento, id=seat_id)
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
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        return redirect('manage_seats')

class DeleteSeatView(View):
    def post(self, request, seat_id):
        asiento = get_object_or_404(Asiento, id=seat_id)
        usuario = asiento.usuario_reservado
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
        return redirect('manage_seats')
