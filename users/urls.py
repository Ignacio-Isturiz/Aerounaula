from django.urls import path

from users.views.auth_views import login_view, logout_view, registro_view, confirmar_cuenta
from users.views.profile_views import mi_cuenta, cambiar_contraseña
from users.views.password_views import recuperar_clave, restablecer_clave
from users.views.dashboard_views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro_view, name='registro'),
    path('recuperar/',  recuperar_clave, name='recuperar_clave'),
    path('restablecer/<str:token>/', restablecer_clave, name='restablecer_clave'),
    path('confirmar/<str:token>/', confirmar_cuenta, name='confirmar_cuenta'),
    path('mi-cuenta/', mi_cuenta, name='mi_cuenta'),
    path('mi-cuenta/cambiar-clave/', cambiar_contraseña, name='cambiar_contraseña'),
        
]
