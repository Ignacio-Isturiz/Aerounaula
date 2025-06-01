from django.shortcuts import render
from dbmodels.models.vuelos import Vuelos

def dashboard(request):
    usuario_id = request.session.get('usuario_id')
    usuario_nombre = request.session.get('usuario_nombre')
    usuario_rol = request.session.get('usuario_rol')

    origenes = Vuelos.objects.values_list('origen', flat=True).distinct()
    destinos = Vuelos.objects.values_list('destino', flat=True).distinct()

    return render(request, 'usuarios/dashboard.html', {
        'logueado': bool(usuario_id),
        'usuario_nombre': usuario_nombre,
        'usuario_rol': usuario_rol,
        'origenes': origenes,
        'destinos': destinos,
        'ocultar_navbar': False
    })
