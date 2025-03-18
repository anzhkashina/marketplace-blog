from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.marketplace_blog.models import Article, Category
from src.marketplace_blog.schemas import (
    ArticleCreate,
    ArticleResponse,
    ArticlesListResponse,
    ArticleUpdate,
)
from src.marketplace_blog.database import get_db
from src.marketplace_blog.crud import (
    create_article as crud_create_article,
    get_article as crud_get_article,
    update_article as crud_update_article,
    delete_article as crud_delete_article,
    get_filtered_articles,
    move_article_to_deleted,
)

router = APIRouter()


@router.post("/articles", response_model=ArticleResponse)
async def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    new_article = crud_create_article(db, article)
    return ArticleResponse.model_validate(new_article)


@router.get("/articles", response_model=ArticlesListResponse)
async def get_articles(
    search: str = None,
    category_id: int = None,
    page_number: int = Query(1, ge=1),
    page_size: int = Query(10, le=100),
    db: Session = Depends(get_db),
):
    # Используем функцию get_filtered_articles для получения отфильтрованных статей
    articles = get_filtered_articles(
        db, search, category_id, skip=(page_number - 1) * page_size, limit=page_size
    )

    # Получаем общее количество статей с теми же фильтрами
    total_count = (
        db.query(Article)
        .join(Category)
        .filter(
            (Article.title.ilike(f"%{search}%") if search else True)
            & (Article.category_id == category_id if category_id is not None else True)
        )
        .count()
    )

    if not articles:
        raise HTTPException(status_code=404, detail="No articles found")

    articles_response = [
        ArticleResponse.model_validate(article) for article in articles
    ]
    return ArticlesListResponse(total_count=total_count, articles=articles_response)


@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: int, article: ArticleUpdate, db: Session = Depends(get_db)
):
    # Получаем статью из базы данных
    db_article = crud_get_article(db, article_id)
    # Проверка, существует ли статья
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    updated_article = crud_update_article(db, article_id, article)
    return ArticleResponse.model_validate(updated_article)


@router.delete("/articles/{article_id}", response_model=dict)
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    db_article = crud_delete_article(db, article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")

    # Перемещение удаленной статьи в отдельную таблицу
    deleted_article = move_article_to_deleted(db, db_article)

    return {
        "message": "Article deleted successfully",
        "deleted_article_id": deleted_article.id,
    }
