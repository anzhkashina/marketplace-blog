from fastapi import FastAPI, Request, HTTPException, status
from dotenv import load_dotenv
import os
import jwt
from src.routers import categories
from src.routers import articles, auth, images

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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token"
            )

    response = await call_next(request)
    return response
