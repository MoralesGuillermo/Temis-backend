import os
from email.message import EmailMessage
from dotenv import load_dotenv
from aiosmtplib import SMTP
from app.services.utils.email.HtmlTemplate import HtmlTemplate

load_dotenv()

class EmailService:
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        template_name: str,
        data: dict,
        from_name: str = "Temis"
    ):
        """
        Envía un correo HTML basado en una plantilla.
        - `to_email`: destinatario
        - `subject`: asunto
        - `template_name`: nombre del archivo .html
        - `data`: diccionario para reemplazar en plantilla
        - `from_name`: nombre del remitente (opcional)
        """

        html_content = HtmlTemplate.render(template_name, data)

        msg = EmailMessage()
        msg["From"] = f"{from_name} <{os.getenv('SMTP_USER')}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content("Este correo requiere un cliente compatible con HTML.")
        msg.add_alternative(html_content, subtype="html")

        smtp_host = os.getenv("EMAIL_HOST")
        smtp_port = os.getenv("EMAIL_PORT")
        smtp_user = os.getenv("EMAIL_USER")
        smtp_pass = os.getenv("EMAIL_PASSWORD")
        use_tls = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "yes")
        
        # Validación básica
        if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
            raise ValueError("Faltan variables de entorno para la configuración SMTP")

        smtp_port = int(smtp_port)

        try:
            smtp = SMTP(hostname=smtp_host, port=smtp_port, start_tls=True)
            await smtp.connect()
            await smtp.login(smtp_user, smtp_pass)
            await smtp.send_message(msg)
            await smtp.quit()
            return True

        except Exception as e:
            # Podés loggear el error o levantar una excepción custom
            print(f"Error al enviar correo: {e}")
            return False