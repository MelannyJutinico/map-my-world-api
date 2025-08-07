from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.models.schemas import Category, CategoryCreate
from app.db.repositories.category_repository import CategoryRepository
from app.db.session import get_db

router = APIRouter(tags=["categories"])

@router.post("/", response_model=Category)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)

    if repo.get_category_by_name(category.name):
        raise HTTPException(status_code=400, detail="Category already exists")
    return repo.create_category(category)

@router.get("/{category_id}", response_model=Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    db_category = repo.get_category(category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category