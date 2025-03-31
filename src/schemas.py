from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
from datetime import datetime


class UserRegistration(BaseModel):
    email: EmailStr
    password: constr(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


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


class ArticleResponse(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ArticlesListResponse(BaseModel):
    total_count: int  # Общее количество статей
    articles: List[ArticleResponse]


class ArticleDelete(ArticleBase):
    id: int
    deleted_at: datetime


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True
