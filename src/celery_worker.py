from celery import Celery
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

celery_app = Celery(
    "marketplace-blog",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("BACKEND_URL"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    broker_connection_retry_on_startup=True,
)

celery_app.autodiscover_tasks(["src.services"])
