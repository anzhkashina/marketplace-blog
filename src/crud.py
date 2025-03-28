import pytz
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from src.models import Article, Category, ArticleDelete
from src.schemas import ArticleCreate, ArticleUpdate
from datetime import datetime

# Установите временную зону UTC
UTC = pytz.UTC


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
    search: str = None,
    category_id: int = None,
    skip: int = 0,
    limit: int = 10,
):
    query = select(Article).join(Category)

    if search:
        query = query.filter(Article.title.ilike(f"%{search}%"))

    if category_id is not None:
        query = query.filter(Article.category_id == category_id)

    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


async def get_article(db: AsyncSession, article_id: int) -> Article:
    result = await db.execute(select(Article).filter(Article.id == article_id))
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
        raise NoResultFound(f"Article with ID {article_id} not found.")

    db_article.deleted_at = datetime.now(UTC)
    db_article.is_deleted = True
    await db.commit()
    return db_article


async def move_article_to_deleted(db: AsyncSession, article: Article) -> ArticleDelete:
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

    return deleted_article
