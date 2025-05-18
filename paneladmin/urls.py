# urls.py
from django.urls import path
from paneladmin.views import panel_admin_view, logout_view

urlpatterns = [
    # otras rutas...
    path('', panel_admin_view, name='panel_admin'), 
    path('logout/', logout_view, name='logout'),
]
