from django.shortcuts import render
from .services.procesador_mensajes import ProcesadorMensajes

procesador = ProcesadorMensajes()

def chat_view(request):
    historial = request.session.get("chat_historial", [])
    nombre_usuario = request.user.first_name if request.user.is_authenticated else None

    if request.method == "POST":
        mensaje = request.POST.get("mensaje", "")
        respuesta = procesador.procesar(mensaje)
        historial.append({"user": mensaje, "bot": respuesta})
        request.session["chat_historial"] = historial

    return render(request, "asistente/chat.html", {
        "nombre_usuario": nombre_usuario,
        "historial": historial
    })
