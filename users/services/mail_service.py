from django.core.mail import send_mail
from django.conf import settings

class MailService:
    @staticmethod
    def enviar_html(destinatario, asunto, html):
        send_mail(
            subject=asunto,
            message="",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinatario],
            html_message=html
        )

