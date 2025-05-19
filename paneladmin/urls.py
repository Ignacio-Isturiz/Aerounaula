# urls.py
from django.urls import path
from paneladmin.views import manage_flights_view, create_flight_view, edit_flight_view, delete_flight_view,panel_admin_view, logout_view, my_profile_view,manage_users_view, create_user_view, edit_user_view, delete_user_view

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
]