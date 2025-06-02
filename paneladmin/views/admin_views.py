from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from dbmodels.models import Usuario

class PanelAdminView(TemplateView):
    template_name = 'paneladmin/panel.html'

    def dispatch(self, request, *args, **kwargs):
        if request.session.get('usuario_rol') != 'Admin':
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario_nombre'] = self.request.session.get('usuario_nombre')
        context['titulo'] = 'Panel de Administración'
        return context

class LogoutView(View):
    def get(self, request):
        request.session.flush()
        request.session.clear_expired()
        response = HttpResponseRedirect('/')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

class MyProfileView(View):
    def get(self, request):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('login')

        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado")
            return redirect('login')

        context = {
            'usuario': usuario,
            'usuario_nombre': request.session.get('usuario_nombre'),
            'usuario_rol': request.session.get('usuario_rol'),
            'titulo': 'Mi Perfil'
        }
        return render(request, 'paneladmin/my_profile.html', context)

    def post(self, request):
        if 'delete_account' in request.POST:
            usuario_id = request.session.get('usuario_id')
            usuario = Usuario.objects.get(id_usuario=usuario_id)
            usuario.estado = False
            usuario.save()
            messages.success(request, "Cuenta desactivada exitosamente")
            request.session.flush()
            return redirect('login')
        return redirect('my_profile')