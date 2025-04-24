# utils/axes_utils.py
from django.shortcuts import render

def custom_lockout_response(request, credentials, *args, **kwargs):
    return render(request, 'usuarios/cuenta_bloqueada.html', status=403)

