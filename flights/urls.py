from django.urls import path
from . import views

urlpatterns = [
    path('vuelos/', views.vuelos_view, name='vuelos'),
    path('reservar/<str:codigo>/', views.reservar_vuelo, name='reservar_vuelo'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('asientos/<str:codigo>/', views.asignar_asientos, name='asignar_asientos'),
    path('confirmar-asientos/', views.confirmar_asientos, name='confirmar_asientos'),
    path('reservas/cancelar/<int:id_reserva>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('asiento/cancelar/<int:asiento_id>/', views.cancelar_asiento, name='cancelar_asiento'),
    path('descargar-tiquetes/', views.descargar_tiquetes_pdf, name='descargar_tiquetes'),
    path('info/equipaje/', views.info_equipaje, name='info_equipaje'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('asientos_ajax/<str:vuelo_codigo>/<int:reserva_id>/', views.asientos_ajax, name='asientos_ajax'),

]
