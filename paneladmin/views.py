# paneladmin/views.py
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect

def panel_admin_view(request):
    rol = request.session.get('usuario_rol')  
    if rol != 'Admin':
        return redirect('dashboard')
    return render(request, 'paneladmin/panel.html', {
        'usuario_nombre': request.session.get('usuario_nombre'),
        'titulo': 'Panel de Administración'
    })

def logout_view(request):
    request.session.flush()
    request.session.clear_expired()

    response = HttpResponseRedirect('/')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
