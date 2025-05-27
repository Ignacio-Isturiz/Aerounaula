from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from dbmodels.models.vuelos import Vuelos
from dbmodels.models.reserva import Reserva
from dbmodels.models.asiento import Asiento
from dbmodels.models.usuario import Usuario
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal
from io import BytesIO
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from django.core.paginator import Paginator
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generar_pdf_tiquetes(usuario, vuelo, resumen_asientos):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="TitleBig", fontSize=18, leading=22, spaceAfter=10, alignment=1))
    styles.add(ParagraphStyle(name="BoldSmall", fontSize=10, leading=12, spaceAfter=2, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="NormalSmall", fontSize=10, leading=12))

    elementos = []

    elementos.append(Image("static/sneat/assets/img/favicon/favicon.png", width=1.5*inch, height=1.5*inch))
    elementos.append(Paragraph("Tiquetes de Vuelo - Confirmación de Reserva", styles["TitleBig"]))
    elementos.append(Spacer(1, 12))

    info_data = [
        [Paragraph("<b>Pasajero:</b>", styles["BoldSmall"]), usuario.nombre],
        [Paragraph("<b>Correo:</b>", styles["BoldSmall"]), usuario.correo],
        [Paragraph("<b>Ruta:</b>", styles["BoldSmall"]), f"{vuelo.origen} → {vuelo.destino}"],
        [Paragraph("<b>Fecha de salida:</b>", styles["BoldSmall"]), vuelo.fecha_salida.strftime('%d/%m/%Y %H:%M')],
        [Paragraph("<b>Código de vuelo:</b>", styles["BoldSmall"]), vuelo.codigo],
    ]
    table_info = Table(info_data, colWidths=[120, 350])
    table_info.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elementos.append(table_info)
    elementos.append(Spacer(1, 20))

    # Tabla de asientos
    table_data = [[
        Paragraph("<b>Asiento</b>", styles["BoldSmall"]),
        Paragraph("<b>Tipo de Pasajero</b>", styles["BoldSmall"]),
        Paragraph("<b>Precio</b>", styles["BoldSmall"])
    ]]

    for item in resumen_asientos:
        tipo = {
            "nino": "Niño",
            "persona_mayor": "Persona Mayor",
            "adulto": "Adulto"
        }.get(item["tipo_pasajero"], "Desconocido")

        table_data.append([
            item["asiento"],
            tipo,
            f"${item['precio']:.2f}"
        ])

    table_asientos = Table(table_data, colWidths=[100, 200, 100])
    table_asientos.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    elementos.append(Paragraph("Detalle de Asientos", styles["BoldSmall"]))
    elementos.append(Spacer(1, 6))
    elementos.append(table_asientos)
    elementos.append(Spacer(1, 20))

    # Notas o agradecimiento
    elementos.append(Paragraph("Gracias por su reserva. ¡Le deseamos un excelente viaje! ✈️", styles["NormalSmall"]))

    doc.build(elementos)
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
    if ya_reservado:
        messages.warning(request, 'Ya tienes una reserva para este vuelo.')
    else:
        Reserva.objects.create(id_usuario_id=usuario_id, vuelo=vuelo, fecha_reserva=timezone.now())
        messages.success(request, '¡Vuelo reservado con éxito!')

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
def asientos_ajax(request, vuelo_codigo, reserva_id):
    vuelo = get_object_or_404(Vuelos, codigo=vuelo_codigo)
    reserva = get_object_or_404(Reserva, id_reserva=reserva_id, vuelo=vuelo)

    usuario = reserva.id_usuario

    asientos_reservados = Asiento.objects.filter(
        codigo=vuelo,
        usuario_reservado=usuario,
        reservado=True
    ).order_by('asiento_numero')

    # Siempre renderizamos la plantilla para manejar la lógica en el template
    html = render_to_string('asientos_modal.html', {
        'asientos': asientos_reservados,
        'reserva': reserva,
        'vuelo': vuelo,
    })

    return HttpResponse(html)


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
        messages.error(request, "No tienes una reserva activa para este vuelo.")
        return redirect('mis_reservas')

    # Obtener datos del usuario y asientos
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    # Filtrar asientos por el código del vuelo asociado al asiento
    asientos = Asiento.objects.filter(codigo=vuelo).order_by('asiento_numero')

    asientos_en_filas = []
    # Iteramos de 4 en 4 para formar las filas del avión
    for i in range(0, len(asientos), 4):
        # Cada 'fila_asientos' contendrá hasta 4 asientos (ej: [A1, A2, A3, A4])
        fila_asientos = asientos[i:i+4]
        # Almacenamos esta lista de 4 asientos en nuestra lista principal
        asientos_en_filas.append(fila_asientos)

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
        nuevos = Asiento.objects.filter(id__in=seleccionados.keys(), reservado=False, codigo=vuelo) # Asegura que los asientos sean de este vuelo
        if nuevos.count() != len(seleccionados):
            messages.error(request, "Uno o más asientos seleccionados no están disponibles o pertenecen a otro vuelo.")
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
                'asiento_id': asiento.id, # Agrega el ID para fácil acceso si necesitas
                'asiento': asiento.asiento_numero,
                'tipo_pasajero': tipo_pasajero,
                'precio': float(precio_final) # Convertir a float si lo usarás en un template o JSON
            })

        # Guardar en sesión
        request.session['resumen_asientos'] = resumen_asientos
        request.session['seleccionados_ids'] = list(seleccionados.keys())
        request.session['vuelo_codigo'] = vuelo.codigo

        return redirect('confirmar_asientos')

    # GET: Mostrar la plantilla
    return render(request, 'asignar_asientos.html', {
        'vuelo': vuelo,
        'asientos_en_filas': asientos_en_filas, # <-- ¡Este es el cambio clave para el front!
        'asientos_usuario': asientos.filter(usuario_reservado=usuario), # Asientos ya reservados por el usuario
        # 'disponibles': asientos.filter(reservado=False), # Ya no necesitas 'disponibles' por separado si manejas el estado en el template
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
    # Asegúrate de configurar las credenciales de email en settings.py
    try:
        send_mail(
            subject="Cancelación de asiento confirmada",
            message=f"Hola {request.session.get('usuario_nombre')},\n\n"
                    f"Has cancelado tu asiento {asiento.asiento_numero} "
                    f"en el vuelo {asiento.codigo.origen} → {asiento.codigo.destino} (Código: {asiento.codigo.codigo}).\n\n"
                    "¡Esperamos verte pronto!",
            from_email=None, # Usará DEFAULT_FROM_EMAIL de settings.py si no se especifica
            recipient_list=[request.session.get('usuario_correo')],
            fail_silently=False # Cambia a True en producción si no quieres que falle la vista por error de email
        )
    except Exception as e:
        # Esto es útil para depurar si el correo no se envía
        print(f"Error al enviar correo de cancelación: {e}")
        messages.warning(request, "El asiento fue cancelado, pero no se pudo enviar el correo de confirmación.")


    messages.success(request, "El asiento fue cancelado correctamente.")
    return HttpResponseRedirect(reverse('mis_asientos'))

def confirmar_asientos(request):
    if not request.session.get('usuario_id'):
        return redirect('login')

    usuario_id = request.session['usuario_id']
    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    vuelo_codigo = request.session.get('vuelo_codigo')

    # Redirigir si no hay un vuelo_codigo en sesión (ej. acceso directo)
    if not vuelo_codigo:
        messages.error(request, "No hay una selección de asientos pendiente para confirmar.")
        return redirect('mis_reservas') # O a la página de selección de vuelos

    vuelo = get_object_or_404(Vuelos, codigo=vuelo_codigo)

    # Obtener el resumen de los asientos desde la sesión
    resumen_asientos = request.session.get('resumen_asientos')
    seleccionados_ids = request.session.get('seleccionados_ids')

    # Si no hay datos en sesión, significa que la sesión expiró o se accedió directamente
    if not resumen_asientos or not seleccionados_ids:
        messages.error(request, "Tu sesión de selección de asientos ha expirado o es inválida. Por favor, selecciona tus asientos nuevamente.")
        return redirect('asignar_asientos', codigo=vuelo_codigo) # Redirige para seleccionar de nuevo

    # Si el usuario aún no ha confirmado, mostrar el resumen para revisión
    if request.method == 'GET':
        # Calcular el precio total aquí para mostrarlo en el template de confirmación
        precio_total = sum(item['precio'] for item in resumen_asientos)

        return render(request, 'confirmar_asientos.html', {
            'vuelo': vuelo,
            'resumen_asientos': resumen_asientos,
            'precio_total': precio_total, # Agregado para mostrar el total
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol': request.session.get('usuario_rol'),
        })

    # POST: Confirmar los asientos seleccionados
    # Es crucial re-verificar la disponibilidad aquí para evitar ataques de carrera
    asientos_a_reservar = Asiento.objects.filter(id__in=seleccionados_ids, reservado=False, codigo=vuelo)

    # Si la cantidad de asientos a reservar no coincide con los que se intentaron seleccionar
    # significa que algunos ya fueron reservados por otra persona.
    if asientos_a_reservar.count() != len(seleccionados_ids):
        messages.error(request, "Algunos de los asientos que seleccionaste ya no están disponibles. Por favor, revisa tu selección.")
        # Limpia sesión para forzar una nueva selección
        del request.session['resumen_asientos']
        del request.session['seleccionados_ids']
        del request.session['vuelo_codigo']
        return redirect('asignar_asientos', codigo=vuelo_codigo)


    for asiento in asientos_a_reservar:
        asiento.reservado = True
        asiento.usuario_reservado = usuario
        asiento.save()

    # Actualizar o crear la Reserva.
    # Si una reserva ya existe para el usuario y el vuelo, se actualiza; si no, se crea.
    reserva, created = Reserva.objects.get_or_create(
        id_usuario=usuario,
        vuelo=vuelo,
        defaults={'fecha_reserva': timezone.now()} # Solo se usa si se crea la reserva
    )
    # Si la reserva ya existía, puedes actualizar su fecha_reserva si lo deseas:
    # if not created:
    #     reserva.fecha_reserva = timezone.now()
    #     reserva.save()


    # Enviar el correo de confirmación
    asientos_numeros = [str(item['asiento']) for item in resumen_asientos]
    try:
        send_mail(
            subject="Confirmación de reserva de asientos",
            message=f"Hola {usuario.nombre},\n\n"
                    f"Has reservado los siguientes asientos en el vuelo {vuelo.origen} ({vuelo.codigo}) → {vuelo.destino}:\n"
                    f"Asientos: {', '.join(asientos_numeros)}\n\n"
                    f"El total a pagar es: ${sum(item['precio'] for item in resumen_asientos):.2f}\n\n"
                    "¡Gracias por tu reserva!",
            from_email=None,
            recipient_list=[usuario.correo],
            fail_silently=False
        )
    except Exception as e:
        print(f"Error al enviar correo de confirmación: {e}")
        messages.warning(request, "Tus asientos han sido reservados, pero no se pudo enviar el correo de confirmación.")


    # Limpiar la sesión después de la confirmación exitosa
    if 'resumen_asientos' in request.session:
        del request.session['resumen_asientos']
    if 'seleccionados_ids' in request.session:
        del request.session['seleccionados_ids']
    if 'vuelo_codigo' in request.session:
        del request.session['vuelo_codigo']

    messages.success(request, "Tus asientos han sido reservados correctamente.")
    return redirect('mis_asientos')

def info_equipaje(request):
    return render(request, 'informacion/equipaje.html')

def sobre_nosotros(request):
    return render(request, 'usuarios/sobre_nosotros.html')
