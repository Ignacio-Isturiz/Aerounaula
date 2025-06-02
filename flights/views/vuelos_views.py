from django.views.generic import ListView
from dbmodels.models.vuelos import Vuelos

class VuelosListView(ListView):
    model = Vuelos
    template_name = 'vuelos.html'
    context_object_name = 'vuelos'
    paginate_by = 10  # Ahora mostrará 10 vuelos por página

    def get_queryset(self):
        request = self.request
        qs = Vuelos.objects.filter(estado='Disponible')  # <-- Esto estaba en tu versión anterior y es clave

        if origen := request.GET.get('origen'):
            qs = qs.filter(origen=origen)
        if destino := request.GET.get('destino'):
            qs = qs.filter(destino=destino)
        if codigo := request.GET.get('codigo'):
            qs = qs.filter(codigo=codigo)
        if fecha_ida := request.GET.get('fecha_ida'):
            qs = qs.filter(fecha_salida__date=fecha_ida)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['origenes'] = Vuelos.objects.values_list('origen', flat=True).distinct()
        context['destinos'] = Vuelos.objects.values_list('destino', flat=True).distinct()
        context['codigos'] = Vuelos.objects.values_list('codigo', flat=True).distinct()
        context['usuario_nombre'] = self.request.session.get('usuario_nombre')
        context['usuario_rol'] = self.request.session.get('usuario_rol')
        context['ocultar_navbar'] = False

        return context
