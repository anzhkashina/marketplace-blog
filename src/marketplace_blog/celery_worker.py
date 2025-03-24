from celery import Celery
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()


def create_celery_app():
    broker_url = os.getenv(
        "CELERY_BROKER_URL",
        "pyamqp://${RABBITMQ_DEFAULT_USER}:${RABBITMQ_DEFAULT_PASS}@rabbitmq:5672//",
    )

    if not broker_url:
        raise ValueError("CELERY_BROKER_URL must be set in the environment.")

    return Celery(__name__, broker=broker_url)


celery_app = create_celery_app()
