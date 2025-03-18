from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.marketplace_blog.models import Category
from src.marketplace_blog.schemas import CategoryCreate
from src.marketplace_blog.database import get_db

router = APIRouter()


@router.post("/categories")
async def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    new_category = Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return {"message": "Category created successfully", "category": new_category}


@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories


@router.get("/categories/{category_id}")
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
