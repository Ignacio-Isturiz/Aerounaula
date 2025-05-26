from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
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
from django.urls import reverse
from decimal import Decimal
from io import BytesIO
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.core.paginator import Paginator

def generar_pdf_tiquetes(usuario, vuelo, resumen_asientos):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "Tiquetes de Vuelo - Confirmación de Reserva")
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 90, f"Pasajero: {usuario.nombre} ")
    p.drawString(50, height - 110, f"Correo: {usuario.correo}")
    p.drawString(50, height - 130, f"Ruta: {vuelo.origen} → {vuelo.destino}")
    p.drawString(50, height - 150, f"Fecha de salida: {vuelo.fecha_salida.strftime('%d/%m/%Y %H:%M')}")
    p.drawString(50, height - 170, f"Código de vuelo: {vuelo.codigo}")

    p.drawString(50, height - 200, "Detalle de Asientos:")
    y = height - 220
    for item in resumen_asientos:
        tipo = {
            "nino": "Niño",
            "persona_mayor": "Persona Mayor",
            "adulto": "Adulto"
        }.get(item["tipo_pasajero"], "Desconocido")
        p.drawString(60, y, f"Asiento {item['asiento']} - Tipo: {tipo} - Precio: ${item['precio']:.2f}")
        y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def descargar_tiquetes_pdf(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    vuelo_codigo = request.session.get('vuelo_codigo')
    vuelo = get_object_or_404(Vuelos, codigo=vuelo_codigo)
    resumen_asientos = request.session.get('resumen_asientos')

    if not resumen_asientos:
        messages.error(request, "No hay datos disponibles para generar el PDF.")
        return redirect('mis_asientos')

    pdf_file = generar_pdf_tiquetes(usuario, vuelo, resumen_asientos)
    return FileResponse(pdf_file, as_attachment=True, filename='tiquetes_reserva.pdf')


def vuelos_view(request):
    origenes = Vuelos.objects.values_list('origen', flat=True).distinct()
    destinos = Vuelos.objects.values_list('destino', flat=True).distinct()
    codigos = Vuelos.objects.values_list('codigo', flat=True).distinct()

    origen = request.GET.get('origen')
    destino = request.GET.get('destino')
    codigo = request.GET.get('codigo')
    fecha_ida = request.GET.get('fecha_ida')

    vuelos = Vuelos.objects.filter(estado='Disponible')
    if origen:
        vuelos = vuelos.filter(origen=origen)
    if destino:
        vuelos = vuelos.filter(destino=destino)
    if codigo:
        vuelos = vuelos.filter(codigo=codigo)
    if fecha_ida:
        vuelos = vuelos.filter(fecha_salida__date=fecha_ida)
        
    paginator = Paginator(vuelos, 5)
    page_number = request.GET.get('page')
    vuelos_paginados = paginator.get_page(page_number)

    # Determinar si el usuario está logueado
    usuario_rol = request.session.get('usuario_rol') 
    usuario_nombre = request.session.get('usuario_nombre', '')

    return render(request, 'vuelos.html', {
        'vuelos': vuelos_paginados,
        'origenes': origenes,
        'destinos': destinos,
        'codigos': codigos,
        'usuario_nombre': usuario_nombre,
        'usuario_rol': usuario_rol,
        'ocultar_navbar': False
    })

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

    # Verificar si el usuario tiene una reserva en el vuelo
    if not Reserva.objects.filter(id_usuario=usuario_id, vuelo=vuelo).exists():
        return redirect('mis_reservas')

    # Obtener datos del usuario y asientos
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    asientos = Asiento.objects.filter(codigo=vuelo).order_by('asiento_numero')
    asientos_usuario = asientos.filter(usuario_reservado=usuario)  # Asientos ya reservados por el usuario
    disponibles = asientos.filter(reservado=False)  # Asientos disponibles

    if request.method == 'POST':
        asientos_seleccionados_str = request.POST.get('asientos_seleccionados', '')
        if not asientos_seleccionados_str:
            messages.error(request, "No se seleccionaron asientos.")
            return redirect('asignar_asientos', codigo=vuelo.codigo)

        # Parsear el string "id:tipo,id:tipo,..."
        seleccionados = {}
        for item in asientos_seleccionados_str.split(','):
            if ':' in item:
                asiento_id_str, tipo_pasajero = item.split(':', 1)
                try:
                    asiento_id = int(asiento_id_str)
                except ValueError:
                    messages.error(request, "Datos de asientos inválidos.")
                    return redirect('asignar_asientos', codigo=vuelo.codigo)
                seleccionados[asiento_id] = tipo_pasajero
            else:
                messages.error(request, "Formato de asientos inválido.")
                return redirect('asignar_asientos', codigo=vuelo.codigo)

        # Filtrar los asientos seleccionados y verificar disponibilidad
        nuevos = Asiento.objects.filter(id__in=seleccionados.keys(), reservado=False)
        if nuevos.count() != len(seleccionados):
            messages.error(request, "Uno o más asientos seleccionados no están disponibles.")
            return redirect('asignar_asientos', codigo=vuelo.codigo)

        # Crear resumen de precios
        resumen_asientos = []
        for asiento in nuevos:
            tipo_pasajero = seleccionados.get(asiento.id)
            if tipo_pasajero not in ['nino', 'persona_mayor', 'adulto']:
                messages.error(request, "Tipo de pasajero inválido.")
                return redirect('asignar_asientos', codigo=vuelo.codigo)

            precio = Decimal(vuelo.precio)
            if tipo_pasajero == 'nino':
                descuento = Decimal('0.20')
            elif tipo_pasajero == 'persona_mayor':
                descuento = Decimal('0.15')
            else:
                descuento = Decimal('0.00')

            precio_final = precio - (precio * descuento)

            resumen_asientos.append({
                'asiento': asiento.asiento_numero,
                'tipo_pasajero': tipo_pasajero,
                'precio': float(precio_final)
            })

        # Guardar en sesión
        request.session['resumen_asientos'] = resumen_asientos
        request.session['seleccionados_ids'] = list(seleccionados.keys())
        request.session['vuelo_codigo'] = vuelo.codigo

        return redirect('confirmar_asientos')

    # GET: Mostrar la plantilla
    return render(request, 'asignar_asientos.html', {
        'vuelo': vuelo,
        'asientos': asientos,
        'disponibles': disponibles,
        'asientos_usuario': asientos_usuario,
    })


def mis_asientos(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)

    # Filtrar los asientos asignados al usuario
    asientos = Asiento.objects.select_related('codigo').filter(usuario_reservado=usuario)

    return render(request, 'mis_asientos.html', {
        'asientos': asientos,  # 👈 esto era lo que faltaba
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'ocultar_navbar': False
    })


@require_POST
def cancelar_asiento(request, asiento_id):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    asiento = get_object_or_404(Asiento, pk=asiento_id, usuario_reservado__id_usuario=usuario_id)

    asiento.reservado = False
    asiento.usuario_reservado = None
    asiento.save()

    # Enviar correo si quieres notificar
    send_mail(
        subject="Cancelación de asiento",
        message=f"Has cancelado tu asiento {asiento.asiento_numero} en el vuelo {asiento.codigo.origen} → {asiento.codigo.destino}.",
        from_email=None,
        recipient_list=[request.session.get('usuario_correo')],
        fail_silently=True
    )

    messages.success(request, "El asiento fue cancelado correctamente.")
    return HttpResponseRedirect(reverse('mis_asientos'))

def confirmar_asientos(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    vuelo_codigo = request.session.get('vuelo_codigo')
    vuelo = get_object_or_404(Vuelos, codigo=vuelo_codigo)

    # Obtener el resumen de los asientos desde la sesión
    resumen_asientos = request.session.get('resumen_asientos')
    seleccionados_ids = request.session.get('seleccionados_ids')

    # Si el usuario aún no ha confirmado, mostrar el resumen para revisión
    if request.method == 'GET':
        return render(request, 'confirmar_asientos.html', {
            'vuelo': vuelo,
            'resumen_asientos': resumen_asientos,
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol': request.session.get('usuario_rol'),
        })

    # POST: Confirmar los asientos seleccionados
    asientos_seleccionados = Asiento.objects.filter(id__in=seleccionados_ids)
    for asiento in asientos_seleccionados:
        asiento.reservado = True
        asiento.usuario_reservado = usuario
        asiento.save()

    reserva, created = Reserva.objects.get_or_create(
    id_usuario=usuario,
    vuelo=vuelo,
    defaults={'fecha_reserva': timezone.now()}
)


    # Enviar el correo de confirmación
    send_mail(
        subject="Confirmación de reserva de asientos",
        message=f"Has reservado los siguientes asientos en el vuelo {vuelo.origen} → {vuelo.destino}.\nAsientos: {', '.join([str(item['asiento']) for item in resumen_asientos])}",
        from_email=None,
        recipient_list=[usuario.correo],
        fail_silently=False
    )

    # Limpiar la sesión
    del request.session['resumen_asientos']
    del request.session['seleccionados_ids']
    del request.session['vuelo_codigo']

    messages.success(request, "Tus asientos han sido reservados correctamente.")
    return redirect('mis_asientos')

def info_equipaje(request):
    return render(request, 'informacion/equipaje.html')
