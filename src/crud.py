import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from src.models import User, Article, Category, ArticleDelete
from src.schemas import ArticleCreate, ArticleUpdate
from datetime import datetime
from typing import Optional
from sqlalchemy import bindparam, Integer, cast, select
from sqlalchemy.orm import selectinload

UTC = pytz.UTC


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_article(db: AsyncSession, article: ArticleCreate) -> Article:
    db_article = Article(
        title=article.title,
        content=article.content,
        category_id=article.category_id,
        image_url=article.image_url,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(db_article)
    await db.commit()
    await db.refresh(db_article)
    return db_article


async def get_filtered_articles(
    db: AsyncSession,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
):
    query = select(Article).join(Category).options(selectinload(Article.category))
    params = {}

    if search:
        query = query.filter(Article.title.ilike(f"%{search}%"))

    if category_id is not None:
        query = query.filter(
            Article.category_id == cast(bindparam("category_id"), Integer)
        )
        params["category_id"] = category_id

    result = await db.execute(query.offset(skip).limit(limit), params)
    articles = result.scalars().all()
    return articles


async def get_article(db: AsyncSession, article_id: int) -> Article:
    query = (
        select(Article)
        .options(selectinload(Article.category))
        .filter(Article.id == cast(bindparam("article_id"), Integer))
    )
    result = await db.execute(query, {"article_id": article_id})
    article = result.scalar_one_or_none()
    if article is None:
        raise NoResultFound(f"Article with ID {article_id} not found.")
    return article


async def update_article(
    db: AsyncSession, article_id: int, article_update: ArticleUpdate
) -> Article | None:
    db_article = await get_article(db, article_id)

    for key, value in article_update.model_dump(exclude_unset=True).items():
        setattr(db_article, key, value)  # Обновляем каждое поле

    db_article.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(db_article)
    return db_article


async def delete_article(db: AsyncSession, article_id: int) -> Article | None:
    db_article = await get_article(db, article_id)
    if not db_article:
        return None

    return db_article


async def move_article_to_deleted(db: AsyncSession, article: Article) -> None:
    deleted_article = ArticleDelete(
        id=article.id,
        title=article.title,
        content=article.content,
        category_id=article.category_id,
        image_url=article.image_url,
        deleted_at=datetime.now(UTC),
    )

    db.add(deleted_article)
    await db.delete(article)
    await db.commit()
