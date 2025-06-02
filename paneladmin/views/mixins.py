from django.shortcuts import redirect

class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.session.get('usuario_rol') != 'Admin':
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

class LoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('usuario_id'):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)
