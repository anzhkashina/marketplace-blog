import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.marketplace_blog.main import app  # Импортируйте ваше FastAPI приложение

client = TestClient(app)


@pytest.fixture
def mock_send_email():
    with patch("src.marketplace_blog.services.email_service.send_email.delay") as mock:
        yield mock


def test_register_sends_email(mock_send_email):
    # Данные для регистрации
    user_data = {"email": "test@example.com", "password": "password123"}

    # Отправка POST-запроса на регистрацию
    response = client.post("/register", json=user_data)

    # Проверка, что ответ имеет статус 200
    assert response.status_code == 200

    # Проверка, что задача send_email была вызвана
    mock_send_email.assert_called_once()

    # Проверка, что ответ содержит ожидаемое сообщение
    assert response.json() == {
        "message": "User registered successfully",
        "user_id": response.json()["user_id"],
    }


def test_register_email_already_exists(mock_send_email):
    # Данные для регистрации
    user_data = {"email": "existing@example.com", "password": "password123"}

    # Сначала зарегистрируем пользователя
    client.post("/register", json=user_data)

    # Попробуем зарегистрировать того же пользователя снова
    response = client.post("/register", json=user_data)

    # Проверка, что ответ имеет статус 400
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}
