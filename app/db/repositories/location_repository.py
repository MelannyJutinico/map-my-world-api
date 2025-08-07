from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.models.database import Location, Category

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_location_with_categories(
        self, 
        location_data: dict,
        category_ids: Optional[List[int]] = None
    ):
        db_location = Location(**location_data)
        self.db.add(db_location)
        self.db.flush()
        
        if category_ids:
            categories = self.db.query(Category).filter(
                Category.id.in_(category_ids)
            ).all()
            db_location.categories = categories
        
        self.db.commit()
        self.db.refresh(db_location)
        return db_location