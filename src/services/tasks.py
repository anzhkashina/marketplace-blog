import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from src.celery_worker import celery_app

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM") or MAIL_USERNAME
MAIL_SERVER = os.getenv("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "true").lower() == "true"


@celery_app.task(bind=True)
def send_email(self, email: str, subject: str, body: str):
    try:
        # Создание email
        msg = MIMEMultipart()
        msg["From"] = MAIL_FROM
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.set_debuglevel(1)
            if MAIL_STARTTLS:
                server.starttls()

            try:
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
            except smtplib.SMTPAuthenticationError as e:
                logger.info(f"Ошибка аутентификации: {e}")
                raise

            server.send_message(msg)
            logger.info(f"Email sent to {email} using smtplib")

    except (smtplib.SMTPException, smtplib.socket.gaierror) as e:
        logger.error(f"Error sending email to {email} using smtplib: {e}")
