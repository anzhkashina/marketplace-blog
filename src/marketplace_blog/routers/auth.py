from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette.responses import Response
from src.marketplace_blog.models import User
from src.marketplace_blog.schemas import UserRegistration, UserLogin
from src.marketplace_blog.database import get_db
import os
import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer
from src.marketplace_blog.celery_worker import send_email
from datetime import datetime, timedelta
import pytz

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/register")
async def register(user: UserRegistration, db: Session = Depends(get_db)):
    db_existing_user = db.query(User).filter(User.email == user.email).first()

    if db_existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    new_user = User(email=user.email, password=hashed_password.decode("utf-8"))

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Отправка электронного письма через Celery
    subject = "Registration Successful"
    recipient = user.email
    body = f"Welcome, {user.email}! Your registration was successful."
    # Вызов Celery задачи для отправки почты
    send_email.delay(subject, recipient, body)

    return {"message": "User registered successfully", "user_id": new_user.id}


@router.post("/login")
async def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user and bcrypt.checkpw(
        user.password.encode("utf-8"), db_user.password.encode("utf-8")
    ):
        # Устанавливаем срок действия токена (например, 1 час)
        token_data = {
            "email": user.email,
            "user_id": db_user.id,
            "exp": datetime.now(pytz.utc) + timedelta(hours=1),
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
        response.set_cookie(
            key="token", value=token, httponly=True
        )  # Сохранение Токена в cookie
        return {"token": token}

    raise HTTPException(status_code=400, detail="Invalid credentials")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=403, detail="Could not validate credentials")


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}"}
