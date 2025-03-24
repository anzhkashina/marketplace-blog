from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os

# Загрузка переменных окружения из файла .env
load_dotenv()
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/marketplace"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Функция для получения сессии базы данных, обрабатывающая ошибки."""
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        # Откат всех изменений при возникновении ошибки
        print(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        # Закрываем сессию, чтобы освободить ресурсы
        db.close()
