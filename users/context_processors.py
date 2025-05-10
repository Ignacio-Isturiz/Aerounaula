def datos_sesion(request):
    return {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'usuario_rol': request.session.get('usuario_rol'),
        'usuario_id': request.session.get('usuario_id'),
    }
