from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.models.schemas import Location, LocationCreate
from app.db.repositories.location_repository import LocationRepository
from app.db.session import get_db

router = APIRouter()

@router.post("/locations/", response_model=Location)
def create_location(
    location: LocationCreate, 
    db: Session = Depends(get_db)
):
    repo = LocationRepository(db)
    return repo.create_location(location)

@router.get("/locations/{location_id}", response_model=Location)
def read_location(
    location_id: int, 
    db: Session = Depends(get_db)
):
    repo = LocationRepository(db)
    db_location = repo.get_location(location_id)
    if not db_location:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location