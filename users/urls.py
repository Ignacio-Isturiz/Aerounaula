from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('registro/', views.registro_view, name='registro'),
    path('recuperar/', views.recuperar_clave, name='recuperar_clave'),
    path('restablecer/<str:token>/', views.restablecer_clave, name='restablecer_clave'),
    path('confirmar/<str:token>/', views.confirmar_cuenta, name='confirmar_cuenta'),
]
