# API Блога Маркетплейса

Этот проект представляет собой API для реализации функциональности блога маркетплейса, разработанное на основе дизайн-макетов Figma: [https://www.figma.com/design/0iOMBzhZVXTebSCdh5ZkAG/Маркетплейс-(Copy)?node-id=0-1&p=f&t=hdkkJcXhqylwjRsR-0](https://www.figma.com/design/0iOMBzhZVXTebSCdh5ZkAG/Маркетплейс-(Copy)?node-id=0-1&p=f&t=hdkkJcXhqylwjRsR-0).

## Технологический стек

*   Python 3.11+
*   FastAPI
*   PostgreSQL
*   Poetry
*   Ruff
*   Pydantic Settings
*   pre-commit
*   RabbitMQ
*   Celery
*   Docker, Docker Compose
*   pytest
*   Minio

## Ключевые особенности

*   **Аутентификация и авторизация:** Реализована на основе JWT токенов, хранящихся в cookie.
*   **Асинхронная отправка email:** Используется RabbitMQ и Celery для отправки приветственных писем после регистрации.
*   **CRUD для статей:**  Предоставляет API для создания, чтения, обновления и (фейкового) удаления статей.
*   **Постраничная пагинация, поиск и фильтрация:** Эндпоинт списка статей поддерживает пагинацию, полнотекстовый поиск и фильтрацию по категориям.
*   **Хранение изображений:** Используется Minio (S3-совместимое хранилище) для хранения изображений статей.

## Установка и запуск

1.  **Клонируйте репозиторий:** `git clone <repository_url>`
2.  **Перейдите в директорию проекта:** `cd <project_directory>`
3.  **Создайте и активируйте виртуальное окружение:** `python3 -m venv .venv && source .venv/bin/activate`
4.  **Установите зависимости:** `poetry install`
5.  **Настройте переменные окружения:**  Создайте файл `.env` на основе примера, представленного в файле `.env.example`.  Замените заполнители на ваши фактические значения.
6.  **Запустите Docker Compose:** `docker-compose up -d`

## Документация API

После запуска приложения, документация API будет доступна по адресу:

*   [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)
*   [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc)

## Переменные окружения

Необходимые переменные окружения описаны в файле `.env.example` в корне репозитория.  Файл `.env` следует создать на основе этого примера, заполнив актуальными значениями для вашей среды.  Не забудьте исключить файл `.env` из системы контроля версий (Git).


**Помните:** Содержимое `.env.example` служит только для примера!

## Тестирование

Запустите модульные тесты с помощью команды `pytest`.

## Полезные ссылки

*   [Figma Design](https://www.figma.com/design/0iOMBzhZVXTebSCdh5ZkAG/Маркетплейс-(Copy)?node-id=0-1&p=f&t=hdkkJcXhqylwjRsR-0)
*   [FastAPI](https://fastapi.tiangolo.com/)
*   [Poetry](https://python-poetry.org/)
*   [RabbitMQ](https://www.rabbitmq.com/)
*   [Celery](http://www.celeryproject.org/)
*   [Minio](https://min.io/)

---

**Более подробная информация об API, эндпоинтах и схемах данных доступна в Swagger UI (http://localhost:8000/docs).**