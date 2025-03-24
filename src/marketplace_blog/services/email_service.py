import os
import logging
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr, SecretStr
from src.marketplace_blog.celery_worker import celery_app

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Конфигурация электронной почты
class EmailConfig(BaseModel):
    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    MAIL_FROM: EmailStr | None = None
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.mailtrap.io"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True


def load_email_config() -> EmailConfig:
    mail_from_env = os.getenv("MAIL_FROM")
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")

    if not mail_username or not mail_password:
        raise ValueError(
            "MAIL_USERNAME and MAIL_PASSWORD must be set in the environment."
        )

    return EmailConfig(
        MAIL_USERNAME=mail_username,
        MAIL_PASSWORD=SecretStr(mail_password),
        MAIL_FROM=mail_from_env,
    )


try:
    email_conf = load_email_config()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise


@celery_app.task(bind=True)
async def send_email(self, subject: str, recipient: EmailStr, body: str):
    conf = ConnectionConfig(
        MAIL_USERNAME=email_conf.MAIL_USERNAME,
        MAIL_PASSWORD=email_conf.MAIL_PASSWORD,
        MAIL_FROM=email_conf.MAIL_FROM,
        MAIL_PORT=email_conf.MAIL_PORT,
        MAIL_SERVER=email_conf.MAIL_SERVER,
        MAIL_STARTTLS=email_conf.MAIL_STARTTLS,
        MAIL_SSL_TLS=email_conf.MAIL_SSL_TLS,
        USE_CREDENTIALS=email_conf.USE_CREDENTIALS,
        VALIDATE_CERTS=email_conf.VALIDATE_CERTS,
    )

    message = MessageSchema(
        subject=subject, recipients=[recipient], body=body, subtype=MessageType.html
    )
    fm = FastMail(conf)
    try:
        await fm.send_message(message)
        self.update_state(
            state="SUCCESS", meta={"result": f"Email sent to {recipient}"}
        )
        logger.info(f"Email sent to {recipient}")
    except Exception as ex:
        self.update_state(
            state="FAILURE",
            meta={"exc_type": type(ex).__name__, "exc_message": str(ex)},
        )
        logger.error(f"Failed to send email to {recipient}: {ex}")
