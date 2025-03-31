from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import Response
from src.models import User
from src.schemas import UserRegistration, UserLogin
from src.database import get_db
import os
import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer
from src.services.tasks import send_email
from src.crud import get_user_by_email
from datetime import datetime, timedelta
import pytz
import logging

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserRegistration, db: AsyncSession = Depends(get_db)):
    db_existing_user = await db.execute(
        User.__table__.select().where(User.email == user.email)
    )
    if db_existing_user.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    new_user = User(email=user.email, password=hashed_password.decode("utf-8"))

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    subject = "Registration Successful"
    body = f"Welcome, {user.email}! Your registration was successful."
    send_email.delay(user.email, subject, body)

    return {"message": "User registered successfully", "user_id": new_user.id}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    user: UserLogin, response: Response, db: AsyncSession = Depends(get_db)
):
    db_user = await get_user_by_email(db, user.email)
    logger.debug(f"Тип db_user: {type(db_user)}")
    logger.debug(f"Значение db_user: {db_user}")

    if db_user and bcrypt.checkpw(
        user.password.encode("utf-8"), db_user.password.encode("utf-8")
    ):
        token_data = {
            "email": user.email,
            "user_id": db_user.id,
            "exp": datetime.now(pytz.utc) + timedelta(hours=1),
        }
        token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
        response.set_cookie(key="token", value=token, httponly=True)
        return {"token": token}

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials"
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        db_user = await db.execute(
            User.__table__.select().where(User.id == payload["user_id"])
        )
        user = db_user.scalars().first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}"}
