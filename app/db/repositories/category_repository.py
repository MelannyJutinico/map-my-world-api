from typing import List
from sqlalchemy.orm import Session
from app.core.models.database import Category
from app.core.models.schemas import CategoryCreate

class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, category: CategoryCreate):
        db_category = Category(**category.model_dump())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def get_category(self, category_id: int):
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def get_category_by_name(self, name: str):
        return self.db.query(Category).filter(Category.name == name).first()
    
    def get_categories_by_ids(self, category_ids: List[int]):
        return self.db.query(Category).filter(
            Category.id.in_(category_ids)
        ).all()