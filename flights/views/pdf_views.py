from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import FileResponse
from dbmodels.models.usuario import Usuario
from dbmodels.models.vuelos import Vuelos
from flights.utils.pdf import generar_pdf_tiquetes

class DescargarTiquetesPDFView(View):
    def get(self, request):
        if not request.session.get('usuario_id'):
            return redirect('login')

        usuario = get_object_or_404(Usuario, id_usuario=request.session['usuario_id'])
        vuelo = get_object_or_404(Vuelos, codigo=request.session.get('vuelo_codigo'))
        resumen_asientos = request.session.get('resumen_asientos')

        if not resumen_asientos:
            messages.error(request, "No hay datos disponibles para generar el PDF.")
            return redirect('mis_asientos')

        pdf_file = generar_pdf_tiquetes(usuario, vuelo, resumen_asientos)
        return FileResponse(pdf_file, as_attachment=True, filename='tiquetes_reserva.pdf')