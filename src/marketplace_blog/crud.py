import pytz
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from src.marketplace_blog.models import Article, Category, ArticleDelete
from src.marketplace_blog.schemas import ArticleCreate, ArticleUpdate
from datetime import datetime

# Установите временную зону UTC
UTC = pytz.UTC


def create_article(db: Session, article: ArticleCreate) -> Article:
    db_article = Article(
        title=article.title,
        content=article.content,
        category_id=article.category_id,
        image_url=article.image_url,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def get_articles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Article).offset(skip).limit(limit).all()


def get_filtered_articles(
    db: Session,
    search: str = None,
    category_id: int = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(Article).join(Category)

    # Фильтрация по заголовку статьи
    if search:
        query = query.filter(Article.title.ilike(f"%{search}%"))

    # Фильтрация по категории
    if category_id is not None:
        query = query.filter(Article.category_id == category_id)

    return query.offset(skip).limit(limit).all()


def get_article(db: Session, article_id: int) -> Article:
    article = db.query(Article).filter(Article.id == article_id).first()
    if article is None:
        raise NoResultFound(f"Article with ID {article_id} not found.")
    return article


def update_article(
    db: Session, article_id: int, article_update: ArticleUpdate
) -> Article | None:
    db_article = get_article(db, article_id)
    if not db_article:
        return None

    for key, value in article_update.model_dump(exclude_unset=True).items():
        setattr(db_article, key, value)  # Обновляем каждое поле
    db_article.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(db_article)
    return db_article


def delete_article(db: Session, article_id: int) -> Article | None:
    db_article = get_article(db, article_id)
    if not db_article:
        return None

    db_article.deleted_at = datetime.now(UTC)
    db_article.is_deleted = True
    db.commit()
    return db_article


def move_article_to_deleted(db: Session, article: Article) -> ArticleDelete:
    deleted_article = ArticleDelete(
        id=article.id,
        title=article.title,
        content=article.content,
        category_id=article.category_id,
        image_url=article.image_url,
        deleted_at=datetime.now(UTC),
    )

    db.add(deleted_article)
    db.delete(article)
    db.commit()

    return deleted_article
