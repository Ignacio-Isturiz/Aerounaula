from django.urls import path

from flights.views.vuelos_views import VuelosListView
from flights.views.reserva_views import ReservarVueloView, MisReservasView, CancelarReservaView
from flights.views.asiento_views import (
    AsignarAsientosView,
    ConfirmarAsientosView,
    CancelarAsientoView,
    AsientosAjaxView,
    MisAsientosView
)
from flights.views.pdf_views import DescargarTiquetesPDFView
from flights.views.info_views import InfoEquipajeView, SobreNosotrosView, InfoMascotasView

urlpatterns = [
    path('vuelos/', VuelosListView.as_view(), name='vuelos'),
    path('reservar/<str:codigo>/', ReservarVueloView.as_view(), name='reservar_vuelo'),
    path('mis-reservas/', MisReservasView.as_view(), name='mis_reservas'),
    path('asientos/<str:codigo>/', AsignarAsientosView.as_view(), name='asignar_asientos'),
    path('confirmar-asientos/', ConfirmarAsientosView.as_view(), name='confirmar_asientos'),
    path('reservas/cancelar/<int:id_reserva>/', CancelarReservaView.as_view(), name='cancelar_reserva'),
    path('asiento/cancelar/<int:asiento_id>/', CancelarAsientoView.as_view(), name='cancelar_asiento'),
    path('descargar-tiquetes/', DescargarTiquetesPDFView.as_view(), name='descargar_tiquetes'),
    path('info/equipaje/', InfoEquipajeView.as_view(), name='info_equipaje'),
    path('mascotas/', InfoMascotasView.as_view(), name='info_mascotas'),
    path('sobre-nosotros/', SobreNosotrosView.as_view(), name='sobre_nosotros'),
    path('asientos_ajax/<str:vuelo_codigo>/<int:reserva_id>/', AsientosAjaxView.as_view(), name='asientos_ajax'),
    path('mis-asientos/', MisAsientosView.as_view(), name='mis_asientos'),
]
