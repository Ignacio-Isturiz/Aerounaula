from django.urls import path
from . import views

urlpatterns = [
    path('vuelos/', views.vuelos_view, name='vuelos'),
    path('vuelos/crear/', views.crear_vuelo, name='crear_vuelo'),
    path('vuelos/editar/<int:id_vuelo>/', views.editar_vuelo, name='editar_vuelo'),
    path('vuelos/eliminar/<int:id_vuelo>/', views.eliminar_vuelo, name='eliminar_vuelo'),
    path('reservar/<int:id_vuelo>/', views.reservar_vuelo, name='reservar_vuelo'),
    path('mis-reservas/', views.mis_reservas, name='mis_reservas'),
    path('asientos/<int:id_vuelo>/', views.asignar_asientos, name='asignar_asientos'),
    path('reservas/cancelar/<int:id_reserva>/', views.cancelar_reserva, name='cancelar_reserva'),

]
