from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.models.schemas import (
    Location,
    LocationCreate,
    LocationWithCategories,
    Category
)
from app.db.repositories.location_repository import LocationRepository
from app.db.repositories.category_repository import CategoryRepository
from app.db.session import get_db

router = APIRouter(tags=["locations"])

@router.post(
    "/",
    response_model=LocationWithCategories,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new location"
)
async def create_location(
    location: LocationCreate, 
    db: Session = Depends(get_db)
):
   
    repo = LocationRepository(db)
    category_repo = CategoryRepository(db)
    

    if not location.category_ids and not location.description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either category_ids or description must be provided"
        )
    

    if location.category_ids:
        existing_categories = category_repo.get_categories_by_ids(location.category_ids)
        if len(existing_categories) != len(set(location.category_ids)):
            missing_ids = set(location.category_ids) - {c.id for c in existing_categories}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categories not found: {missing_ids}"
            )
    
   
    location_data = location.model_dump(exclude={"category_ids"})
    created_location = repo.create_location_with_categories(
        location_data=location_data,
        category_ids=location.category_ids
    )
    
    return created_location

@router.get(
    "/{location_id}",
    response_model=LocationWithCategories,
    summary="Get location details"
)
async def get_location(
    location_id: int, 
    db: Session = Depends(get_db)
):
    """
    Get complete details for a specific location including its categories.
    """
    repo = LocationRepository(db)
    db_location = repo.get_location_with_categories(location_id)
    if not db_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return db_location
