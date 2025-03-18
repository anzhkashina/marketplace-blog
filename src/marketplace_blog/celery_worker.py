from celery import Celery
from src.marketplace_blog.services import email_service
from src.marketplace_blog.services.email_service import broker_url

celery_app = Celery(__name__, broker=broker_url)


@celery_app.task
def send_registration_email(email: str):
    subject = "Welcome to our service!"
    body = "Thank you for registering!"
    email_service.send_email(subject, email, body)
