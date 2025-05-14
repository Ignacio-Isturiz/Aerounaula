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
    path('reservas/cancelar/<int:id_reserva>/', views.cancelar_reserva, name='cancelar_reserva'),
]
