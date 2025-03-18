from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import pytz
from sqlalchemy.orm import relationship

# Установите временную зону UTC
UTC = pytz.UTC

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, index=True)
    password = Column(String)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), index=True)
    content = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))  # Связь с категорией
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    category = relationship("Category", back_populates="articles")


class ArticleDelete(Base):
    __tablename__ = "deleted_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category_id = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)
    deleted_at = Column(DateTime, nullable=False)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), unique=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    articles = relationship("Article", back_populates="category")
