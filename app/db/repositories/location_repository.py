from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.core.models.database import Category, Location
from app.core.models.schemas import LocationCreate, LocationUpdate

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_location_with_categories(self, location_data: dict, category_ids: List[int] = None):
        location = Location(**location_data)
        self.db.add(location)
        self.db.flush()  
        
        if category_ids:
            categories = self.db.query(Category).filter(Category.id.in_(category_ids)).all()
            location.categories.extend(categories)
        
        self.db.commit()
        self.db.refresh(location)
        return location

    def get_location_with_categories(self, location_id: int):
        return self.db.query(Location).options(
            joinedload(Location.categories)
        ).get(location_id)

    def get_locations_with_categories(self, skip: int = 0, limit: int = 100, category_id: int = None):
        query = self.db.query(Location).options(
            joinedload(Location.categories)
        )
        
        if category_id:
            query = query.join(Location.categories).filter(Category.id == category_id)
            
        return query.offset(skip).limit(limit).all()

    def update_location(self, location_id: int, location: LocationUpdate):
        db_location = self.get_location_with_categories(location_id)
        if not db_location:
            return None
        
        update_data = location.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_location, field, value)
        
        self.db.commit()
        self.db.refresh(db_location)
        return db_location

    def delete_location(self, location_id: int):
        if location := self.db.query(Location).get(location_id):
            self.db.delete(location)
            self.db.commit()
            return True
        return False