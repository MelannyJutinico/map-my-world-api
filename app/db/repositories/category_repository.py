from typing import List
from sqlalchemy.orm import Session, joinedload
from app.core.models.database import Category
from app.core.models.schemas import CategoryCreate, CategoryUpdate

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
        return self.db.query(Category).get(category_id)

    def get_category_with_locations(self, category_id: int):
        return self.db.query(Category).options(
            joinedload(Category.locations)
        ).get(category_id)

    def get_category_by_name(self, name: str, exclude_id: int = None):
        query = self.db.query(Category).filter(Category.name == name)
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        return query.first()

    def get_categories(self, skip: int = 0, limit: int = 100, search: str = None):
        query = self.db.query(Category)
        
        if search:
            query = query.filter(Category.name.ilike(f"%{search}%"))
            
        return query.offset(skip).limit(limit).all()

    def update_category(self, category_id: int, category: CategoryUpdate):
        db_category = self.get_category(category_id)
        if not db_category:
            return None
        
        update_data = category.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def get_categories_by_ids(self, category_ids: List[int]):
        return self.db.query(Category).filter(
            Category.id.in_(category_ids)
        ).all()

    def delete_category(self, category_id: int):
        db_category = self.get_category(category_id)
        if not db_category:
            return False
        
        self.db.delete(db_category)
        self.db.commit()
        return True