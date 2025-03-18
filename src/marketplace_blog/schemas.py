from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# Схема для пользователя
class UserBase(BaseModel):
    email: EmailStr  # Используем EmailStr для более строгой проверки формата email


class UserRegistration(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


# Схема для статьи
class ArticleBase(BaseModel):
    title: str
    content: str
    category_id: int
    image_url: Optional[str] = None


class ArticleCreate(ArticleBase):
    pass


class Article(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category_id: Optional[int] = None

    class Config:
        from_attributes = True


class ArticleResponse(ArticleBase):  # Схема для отображения статьи
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticlesListResponse(BaseModel):  # Схема для ответа с множеством статей
    total_count: int  # Общее количество статей
    articles: List[ArticleResponse]


class ArticleDelete(ArticleBase):
    id: int
    deleted_at: datetime


# Схема для категории
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True
