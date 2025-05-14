from django.urls import path
from . import views

urlpatterns = [
    path('vuelos/', views.vuelos_view, name='vuelos'),
    path('vuelos/crear/', views.crear_vuelo, name='crear_vuelo'),
    path('vuelos/editar/<str:codigo>/', views.editar_vuelo, name='editar_vuelo'),
    path('vuelos/eliminar/<str:codigo>/', views.eliminar_vuelo, name='eliminar_vuelo'),
    path('reservar/<str:codigo>/', views.reservar_vuelo, name='reservar_vuelo'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('asientos/<str:codigo>/', views.asignar_asientos, name='asignar_asientos'),
    path('confirmar-asientos/', views.confirmar_asientos, name='confirmar_asientos'),
    path('reservas/cancelar/<int:id_reserva>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('mis-asientos/', views.mis_asientos, name='mis_asientos'),
    path('asiento/cancelar/<int:asiento_id>/', views.cancelar_asiento, name='cancelar_asiento'),
    path('descargar-tiquetes/', views.descargar_tiquetes_pdf, name='descargar_tiquetes'),
    
]
