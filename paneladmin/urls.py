from django.urls import path

# Admin panel views
from paneladmin.views.admin_views import PanelAdminView, LogoutView, MyProfileView

# Users
from paneladmin.views.user_views import (
    ManageUsersView, CreateUserView, EditUserView, DeleteUserView
)

# Flights
from paneladmin.views.flight_views import (
    ManageFlightsView, CreateFlightView, EditFlightView, DeleteFlightView
)

# Reservations
from paneladmin.views.reservation_views import (
    ManageReservationsView, CreateReservationView, EditReservationView,
    CancelReservationView, DeleteReservationView
)

# Seats
from paneladmin.views.seat_views import (
    ManageSeatsView, CreateSeatView, EditSeatView, DeleteSeatView
)

urlpatterns = [
    # Panel y perfil
    path('', PanelAdminView.as_view(), name='panel_admin'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('my-profile/', MyProfileView.as_view(), name='my_profile'),

    # Usuarios
    path('gestion-usuarios/', ManageUsersView.as_view(), name='manage_users'),
    path('crear-usuario/', CreateUserView.as_view(), name='create_user'),
    path('editar-usuario/<int:user_id>/', EditUserView.as_view(), name='edit_user'),
    path('eliminar-usuario/<int:user_id>/', DeleteUserView.as_view(), name='delete_user'),

    # Vuelos
    path('gestion-vuelos/', ManageFlightsView.as_view(), name='manage_flights'),
    path('crear-vuelo/', CreateFlightView.as_view(), name='create_flight'),
    path('editar-vuelo/<str:flight_code>/', EditFlightView.as_view(), name='edit_flight'),
    path('eliminar-vuelo/<str:flight_code>/', DeleteFlightView.as_view(), name='delete_flight'),

    # Reservas
    path('gestion-reservas/', ManageReservationsView.as_view(), name='manage_reservations'),
    path('reservas/crear/', CreateReservationView.as_view(), name='create_reservation'),
    path('reservas/editar/<int:reservation_id>/', EditReservationView.as_view(), name='edit_reservation'),
    path('reservas/cancelar/<int:reservation_id>/', CancelReservationView.as_view(), name='cancel_reservation'),
    path('reservas/eliminar/<int:reservation_id>/', DeleteReservationView.as_view(), name='delete_reservation'),

    # Asientos
    path('asientos/', ManageSeatsView.as_view(), name='manage_seats'),
    path('asientos/crear/', CreateSeatView.as_view(), name='create_seat'),
    path('asientos/editar/<int:seat_id>/', EditSeatView.as_view(), name='edit_seat'),
    path('asientos/eliminar/<int:seat_id>/', DeleteSeatView.as_view(), name='delete_seat'),
]
