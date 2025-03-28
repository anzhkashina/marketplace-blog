from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Article, Category
from src.schemas import (
    ArticleCreate,
    ArticleResponse,
    ArticlesListResponse,
    ArticleUpdate,
    ArticleDelete,
)
from src.database import get_db
from src.crud import (
    create_article as crud_create_article,
    update_article as crud_update_article,
    delete_article as crud_delete_article,
    get_filtered_articles,
    move_article_to_deleted,
)

router = APIRouter()


@router.post(
    "/articles", status_code=status.HTTP_201_CREATED, response_model=ArticleResponse
)
async def create_article(article: ArticleCreate, db: AsyncSession = Depends(get_db)):
    new_article = await crud_create_article(db, article)
    return ArticleResponse.model_validate(new_article)


@router.get(
    "/articles", status_code=status.HTTP_200_OK, response_model=ArticlesListResponse
)
async def get_articles(
    search: str = None,
    category_id: int = None,
    page_number: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    db: AsyncSession = Depends(get_db),
):
    articles = await get_filtered_articles(
        db, search, category_id, skip=(page_number - 1) * page_size, limit=page_size
    )

    total_count = await db.execute(
        Article.__table__.select()
        .join(Category)
        .where(
            (Article.title.ilike(f"%{search}%") if search else True)
            & (Article.category_id == category_id if category_id is not None else True)
        )
    )
    total_count = total_count.scalar()

    if not articles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No articles found"
        )

    articles_response = [
        ArticleResponse.model_validate(article) for article in articles
    ]
    return ArticlesListResponse(total_count=total_count, articles=articles_response)


@router.put(
    "/articles/{article_id}",
    status_code=status.HTTP_200_OK,
    response_model=ArticleResponse,
)
async def update_article(
    article_id: int, article: ArticleUpdate, db: AsyncSession = Depends(get_db)
):
    updated_article = await crud_update_article(db, article_id, article)
    return ArticleResponse.model_validate(updated_article)


@router.delete(
    "/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=ArticleDelete,
)
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    db_article = await crud_delete_article(db, article_id)
    if db_article is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Article not found"
        )

    # Перемещение удаленной статьи в отдельную таблицу
    deleted_article = await move_article_to_deleted(db, db_article)

    return deleted_article
