from celery import Celery
import os
import logging
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import BaseModel, EmailStr, SecretStr, field_validator, PydanticUserError
import asyncio

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка данных для RabbitMQ
broker_url = f"pyamqp://{os.getenv('RABBITMQ_DEFAULT_USER')}:{os.getenv('RABBITMQ_DEFAULT_PASS')}@rabbitmq//"


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


# Получаем EMAIL_FROM из переменных окружения
mail_from_env = os.getenv("MAIL_FROM")

# Загрузка конфигурации из окружения с обработкой ошибок
try:
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    if not MAIL_USERNAME:
        raise ValueError("MAIL_USERNAME must be set in the environment.")

    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    if not MAIL_PASSWORD:
        raise ValueError("MAIL_PASSWORD must be set in the environment.")

    email_conf = EmailConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=SecretStr(os.getenv("MAIL_PASSWORD")),
        MAIL_FROM=mail_from_env,
    )

    @field_validator("MAIL_FROM", mode="before")
    def validate_mail_from(v):
        if v is None or not isinstance(v, str) or "@" not in v:
            raise ValueError("Invalid email")
        return v

except PydanticUserError as e:
    logger.error(f"Error loading email configuration: {e}")
except ValueError as e:
    logger.error(f"Configuration error: {e}")

# Инициализация Celery
celery = Celery("tasks", broker=broker_url)


@celery.task(bind=True)
def send_email(self, subject: str, recipient: EmailStr, body: str):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    async def send():
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
        except Exception as ex:
            self.update_state(
                state="FAILURE",
                meta={"exc_type": type(ex).__name__, "exc_message": str(ex)},
            )
            print(f"Failed to send email to {recipient}: {ex}")

    # Запускаем асинхронную функцию
    future = asyncio.create_task(send())
    loop.run_until_complete(future)
