from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

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

    elementos.append(Paragraph("Gracias por su reserva. ¡Le deseamos un excelente viaje! ✈️", styles["NormalSmall"]))
    doc.build(elementos)
    buffer.seek(0)
    return buffer
