from django.views.generic import TemplateView

class InfoEquipajeView(TemplateView):
    template_name = 'informacion/equipaje.html'

class SobreNosotrosView(TemplateView):
    template_name = 'usuarios/sobre_nosotros.html'

class InfoMascotasView(TemplateView):
    template_name = 'usuarios/mascotas.html'