from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_async_engine(url=os.getenv("DATABASE_URL"), echo=True)
SessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


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
