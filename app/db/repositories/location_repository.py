from sqlalchemy.orm import Session
from app.core.models.database import Location
from app.core.models.schemas import LocationCreate

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_location(self, location: LocationCreate):
        location_data = location.model_dump(exclude_unset=True)
        db_location = Location(**location_data)
        self.db.add(db_location)
        self.db.commit()
        self.db.refresh(db_location)
        return db_location

    def get_location(self, location_id: int):
        return self.db.query(Location).filter(Location.id == location_id).first()