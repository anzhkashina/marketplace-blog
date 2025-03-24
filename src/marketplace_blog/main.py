from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
import os
import sys
import jwt
from pydantic import BaseModel
from src.marketplace_blog.routers import auth, articles, categories, images

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

# Загрузка переменных окружения из файла .env
load_dotenv()

app = FastAPI()
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")

# Регистрация маршрутов
app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(categories.router)
app.include_router(images.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Marketplace Blog API"}


# Middleware для проверки токена
@app.middleware("http")
async def jwt_middleware(request: Request, call_next):
    token = request.cookies.get("token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.state.user = (
                payload  # Сохранение данных пользователя в объектах запроса
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Token has expired")
        except jwt.PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid token")

    response = await call_next(request)
    return response


# Модели для сериализации данных
class UserRegistration(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class ArticleCreate(BaseModel):
    title: str
    content: str
    category_id: int
    image_url: str


class CategoriesCreate(BaseModel):
    name: str
