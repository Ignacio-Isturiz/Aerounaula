from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal
from dbmodels.models.asiento import Asiento
from dbmodels.models.vuelos import Vuelos
from dbmodels.models.reserva import Reserva
from dbmodels.models.usuario import Usuario
from django.core.mail import send_mail

class MisAsientosView(View):
    def get(self, request):
        if not request.session.get('usuario_id'):
            return redirect('login')

        usuario = get_object_or_404(Usuario, id_usuario=request.session['usuario_id'])
        asientos = Asiento.objects.select_related('codigo').filter(usuario_reservado=usuario).order_by('codigo__codigo', 'asiento_numero')

        return render(request, 'mis_asientos.html', {
            'asientos': asientos,
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol': request.session.get('usuario_rol'),
            'ocultar_navbar': False
        })

class AsientosAjaxView(View):
    def get(self, request, vuelo_codigo, reserva_id):
        vuelo = get_object_or_404(Vuelos, codigo=vuelo_codigo)
        reserva = get_object_or_404(Reserva, id_reserva=reserva_id, vuelo=vuelo)
        usuario = reserva.id_usuario

        asientos_reservados = Asiento.objects.filter(
            codigo=vuelo,
            usuario_reservado=usuario,
            reservado=True
        ).order_by('asiento_numero')

        html = render_to_string('asientos_modal.html', {
            'asientos': asientos_reservados,
            'reserva': reserva,
            'vuelo': vuelo,
        })

        return HttpResponse(html)

class CancelarAsientoView(View):
    def post(self, request, asiento_id):
        if not request.session.get('usuario_id'):
            return redirect('login')

        usuario_id = request.session['usuario_id']
        asiento = get_object_or_404(Asiento, pk=asiento_id, usuario_reservado__id_usuario=usuario_id)

        asiento.reservado = False
        asiento.usuario_reservado = None
        asiento.save()

        try:
            send_mail(
                subject="Cancelación de asiento confirmada",
                message=f"Hola {request.session.get('usuario_nombre')},\n\nHas cancelado tu asiento {asiento.asiento_numero} en el vuelo {asiento.codigo.origen} → {asiento.codigo.destino} (Código: {asiento.codigo.codigo}).\n\n¡Esperamos verte pronto!",
                from_email=None,
                recipient_list=[request.session.get('usuario_correo')],
                fail_silently=False
            )
        except Exception as e:
            print(f"Error al enviar correo de cancelación: {e}")
            messages.warning(request, "El asiento fue cancelado, pero no se pudo enviar el correo de confirmación.")

        messages.success(request, "El asiento fue cancelado correctamente.")
        return HttpResponseRedirect(reverse('mis_asientos'))

class AsignarAsientosView(View):
    def get(self, request, codigo):
        return self.mostrar_formulario(request, codigo)

    def post(self, request, codigo):
        return self.procesar_seleccion(request, codigo)

    def mostrar_formulario(self, request, codigo):
        if not request.session.get('usuario_id'):
            return redirect('login')

        usuario_id = request.session['usuario_id']
        vuelo = get_object_or_404(Vuelos, codigo=codigo)

        if not Reserva.objects.filter(id_usuario=usuario_id, vuelo=vuelo).exists():
            messages.error(request, "No tienes una reserva activa para este vuelo.")
            return redirect('mis_reservas')

        usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
        asientos = Asiento.objects.filter(codigo=vuelo).order_by('asiento_numero')

        asientos_en_filas = [asientos[i:i+4] for i in range(0, len(asientos), 4)]

        return render(request, 'asignar_asientos.html', {
            'vuelo': vuelo,
            'asientos_en_filas': asientos_en_filas,
            'asientos_usuario': asientos.filter(usuario_reservado=usuario),
        })

    def procesar_seleccion(self, request, codigo):
        usuario_id = request.session['usuario_id']
        vuelo = get_object_or_404(Vuelos, codigo=codigo)
        asientos_str = request.POST.get('asientos_seleccionados', '')

        if not asientos_str:
            messages.error(request, "No se seleccionaron asientos.")
            return redirect('asignar_asientos', codigo=vuelo.codigo)

        seleccionados = {}
        for item in asientos_str.split(','):
            if ':' in item:
                asiento_id_str, tipo_pasajero = item.split(':', 1)
                try:
                    asiento_id = int(asiento_id_str)
                    seleccionados[asiento_id] = tipo_pasajero
                except ValueError:
                    messages.error(request, "Datos de asientos inválidos.")
                    return redirect('asignar_asientos', codigo=vuelo.codigo)

        nuevos = Asiento.objects.filter(id__in=seleccionados.keys(), reservado=False, codigo=vuelo)
        if nuevos.count() != len(seleccionados):
            messages.error(request, "Uno o más asientos seleccionados no están disponibles.")
            return redirect('asignar_asientos', codigo=vuelo.codigo)

        resumen = []
        for asiento in nuevos:
            tipo = seleccionados[asiento.id]
            if tipo not in ['nino', 'persona_mayor', 'adulto']:
                messages.error(request, "Tipo de pasajero inválido.")
                return redirect('asignar_asientos', codigo=vuelo.codigo)

            precio = Decimal(vuelo.precio)
            descuento = Decimal('0.20') if tipo == 'nino' else Decimal('0.15') if tipo == 'persona_mayor' else Decimal('0.00')
            precio_final = precio - (precio * descuento)

            resumen.append({
                'asiento_id': asiento.id,
                'asiento': asiento.asiento_numero,
                'tipo_pasajero': tipo,
                'precio': float(precio_final)
            })

        request.session['resumen_asientos'] = resumen
        request.session['seleccionados_ids'] = list(seleccionados.keys())
        request.session['vuelo_codigo'] = vuelo.codigo

        return redirect('confirmar_asientos')

class ConfirmarAsientosView(View):
    def get(self, request):
        if not request.session.get('usuario_id'):
            return redirect('login')

        resumen = request.session.get('resumen_asientos')
        seleccionados_ids = request.session.get('seleccionados_ids')
        vuelo_codigo = request.session.get('vuelo_codigo')

        if not (resumen and seleccionados_ids and vuelo_codigo):
            messages.error(request, "Tu sesión de selección de asientos ha expirado.")
            return redirect('mis_reservas')

        vuelo = get_object_or_404(Vuelos, codigo=vuelo_codigo)
        total = sum(item['precio'] for item in resumen)

        return render(request, 'confirmar_asientos.html', {
            'vuelo': vuelo,
            'resumen_asientos': resumen,
            'precio_total': total,
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol': request.session.get('usuario_rol'),
        })

    def post(self, request):
        usuario_id = request.session['usuario_id']
        usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
        vuelo_codigo = request.session.get('vuelo_codigo')
        resumen = request.session.get('resumen_asientos')
        seleccionados_ids = request.session.get('seleccionados_ids')

        vuelo = get_object_or_404(Vuelos, codigo=vuelo_codigo)
        nuevos = Asiento.objects.filter(id__in=seleccionados_ids, reservado=False, codigo=vuelo)

        if nuevos.count() != len(seleccionados_ids):
            messages.error(request, "Algunos asientos ya no están disponibles.")
            request.session.flush()
            return redirect('asignar_asientos', codigo=vuelo.codigo)

        for asiento in nuevos:
            asiento.reservado = True
            asiento.usuario_reservado = usuario
            asiento.save()

        Reserva.objects.get_or_create(id_usuario=usuario, vuelo=vuelo, defaults={'fecha_reserva': timezone.now()})

        try:
            asientos_txt = ', '.join(str(item['asiento']) for item in resumen)
            total = sum(item['precio'] for item in resumen)
            send_mail(
                subject="Confirmación de reserva de asientos",
                message=f"Hola {usuario.nombre},\n\nHas reservado los asientos: {asientos_txt} en el vuelo {vuelo.origen} → {vuelo.destino} ({vuelo.codigo}).\nTotal: ${total:.2f}\n\nGracias por tu reserva!",
                from_email=None,
                recipient_list=[usuario.correo],
                fail_silently=False
            )
        except Exception as e:
            print(f"Error al enviar correo de confirmación: {e}")
            messages.warning(request, "Reservado con éxito, pero no se envió el correo.")

        request.session.pop('resumen_asientos', None)
        request.session.pop('seleccionados_ids', None)
        request.session.pop('vuelo_codigo', None)

        messages.success(request, "Tus asientos han sido reservados correctamente.")
        return redirect('mis_asientos')