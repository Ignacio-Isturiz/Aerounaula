# urls.py
from django.urls import path
from paneladmin.views import create_seat_view,edit_seat_view,delete_seat_view,manage_seats_view,manage_reservations_view,create_reservation_view,cancel_reservation_view,edit_reservation_view,delete_reservation_view,manage_flights_view, create_flight_view, edit_flight_view, delete_flight_view,panel_admin_view, logout_view, my_profile_view,manage_users_view, create_user_view, edit_user_view, delete_user_view

urlpatterns = [
    # otras rutas...
    path('', panel_admin_view, name='panel_admin'), 
    path('logout/', logout_view, name='logout'),
    path('my-profile/', my_profile_view, name='my_profile'),
    path('gestion-usuarios/', manage_users_view, name='manage_users'),
    path('crear-usuario/', create_user_view, name='create_user'),
    path('editar-usuario/<int:user_id>/', edit_user_view, name='edit_user'),
    path('eliminar-usuario/<int:user_id>/', delete_user_view, name='delete_user'),
    path('gestion-vuelos/', manage_flights_view, name='manage_flights'),
    path('crear-vuelo/', create_flight_view, name='create_flight'),
    path('editar-vuelo/<str:flight_code>/', edit_flight_view, name='edit_flight'),
    path('eliminar-vuelo/<str:flight_code>/', delete_flight_view, name='delete_flight'),
    path('paneladmin/gestion-reservas/', manage_reservations_view, name='manage_reservations'),
    path('paneladmin/reservas/crear/', create_reservation_view, name='create_reservation'),
    path('paneladmin/reservas/editar/<int:reservation_id>/', edit_reservation_view, name='edit_reservation'),
    path('paneladmin/reservas/cancelar/<int:reservation_id>/', cancel_reservation_view, name='cancel_reservation'),
    path('paneladmin/reservas/eliminar/<int:reservation_id>/', delete_reservation_view, name='delete_reservation'),
    path('admin/asientos/', manage_seats_view, name='manage_seats'),
    path('admin/asientos/crear/', create_seat_view, name='create_seat'),
    path('admin/asientos/editar/<int:seat_id>/', edit_seat_view, name='edit_seat'),
    path('admin/asientos/eliminar/<int:seat_id>/', delete_seat_view, name='delete_seat'),

]