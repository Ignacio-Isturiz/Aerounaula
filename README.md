# Aerounaula

Aerounaula es una plataforma web para gestión de vuelos, reservas de asientos, perfiles de usuario y asistencia virtual con IA, desarrollada con Django. Pensada para simular el funcionamiento de una aerolínea moderna, permite manejar usuarios, vuelos y reservas con funcionalidades intuitivas y diseño visual atractivo.

## Capturas de pantalla

- Vista principal del panel usuario:
> ![image](https://github.com/user-attachments/assets/fc0e7460-9f23-4181-8d74-108ffb3f4b91)

- Vista principal del panel administrativo:
> ![image](https://github.com/user-attachments/assets/b1e9153b-c20f-4b06-8ad3-011cb5d514ed)

- Vista del chatbot asistente:
> ![image](https://github.com/user-attachments/assets/018eb35e-9bf9-409c-993e-cf47543967a7)
> ![image](https://github.com/user-attachments/assets/0125d88f-3190-4277-9413-a0484939021e)

## Funcionalidades principales

-  Registro e inicio de sesión de usuarios
-  Gestión de perfiles y cambio de contraseña
-  Administración de vuelos (crear, editar, eliminar)
-  Reserva y cancelación de asientos
-  Asistente IA integrado para consultas de vuelos
-  Panel administrativo con gestión de usuarios

## Tecnologías utilizadas

- **Backend:** Python, Django
- **Base de datos:** PostgreSQL
- **Frontend:** HTML, CSS, Bootstrap
- **IA:** geopy, rapidfuzz, Nominatim (geolocalización)
- **Otros:** Render (deploy web),NeonTech (deploy DB)

## Arquitectura y diseño

Este proyecto sigue el patrón MVC de Django. Las vistas están divididas en archivos modulares:
- `auth_views.py`, `profile_views.py`, etc., para mantener la organización.
- Aplicaciones desacopladas para asistentes, panel y usuarios.
- Se siguen principios de diseño limpio (Single Responsibility, modularidad, reutilización).

## Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un fork del repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -m 'feat: nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## Autores

- **Ignacio Istúriz y Juliana Loaiza** – Desarrolladores del proyecto  
- GitHub: [@Ignacio-Isturiz](https://github.com/Ignacio-Isturiz)
- GitHub: [@juliloa](https://github.com/juliloa)



