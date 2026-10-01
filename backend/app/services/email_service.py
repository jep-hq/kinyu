import smtplib
from email.message import EmailMessage
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.user = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD

    async def send_email(self, to_email: str, subject: str, content: str, is_html: bool = False):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg['To'] = to_email
        msg.set_content(content)

        if is_html:
            msg.add_alternative(content, subtype='html')

        if not self.smtp_host:
             logger.warning("SMTP Host not set. Email would have been sent: %s", subject)
             return

        try:
            # Note: smtplib is blocking. In production/Async environment,
            # use aiosmtplib or background worker (Celery/RabbitMQ).
            # For simplicity in this scaffold, we wrap or assume low volume.
            # Ideally: await run_in_executor(...)
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if self.user:
                    server.login(self.user, self.password)
                server.send_message(msg)
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")

# singleton instance
email_service = EmailService()

def get_email_service() -> EmailService:
    return email_service
