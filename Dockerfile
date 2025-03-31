FROM python:3.11-slim
     WORKDIR /app

     COPY pyproject.toml poetry.lock . /app

     RUN pip install poetry
     RUN poetry config virtualenvs.create false
     RUN poetry install --only main --no-root

     RUN adduser --disabled-password --gecos '' celeryuser
     RUN chown -R celeryuser:celeryuser /app

     USER celeryuser

     ENV PYTHONPATH=/app:/app/src

     CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
