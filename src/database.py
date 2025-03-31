from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

logger.debug(f"Connecting to database with URL: {DATABASE_URL}")

engine = create_async_engine(url=DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await db.rollback()
            raise
        finally:
            await db.close()
