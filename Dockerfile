FROM python:3.11-slim
     WORKDIR /app
     COPY pyproject.toml poetry.lock ./
     RUN pip install poetry && poetry install --only main --no-root
     COPY ./src /app
     CMD ["poetry", "run", "uvicorn", "src.marketplace_blog.main:app", "--host", "0.0.0.0", "--port", "8000"]
