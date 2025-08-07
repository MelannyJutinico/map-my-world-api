from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.models.schemas import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
    LocationReviewStatus
)
from app.core.services.location_service import LocationService
from app.db.session import get_db

router = APIRouter(
    tags=["locations"],
    prefix="/locations"
)

@router.post(
    "/",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new location",
    responses={
        400: {"description": "Missing required data"},
        404: {"description": "Category not found"},
        422: {"description": "Validation error"}
    }
)
async def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new location with optional categories or description.

    - **latitude**: Required (-90 to 90)
    - **longitude**: Required (-180 to 180)
    - **description**: Optional text for NLP-based classification
    - **category_ids**: Optional list of existing category IDs
    """
    service = LocationService(db)
    return await service.create_location(payload)

@router.get(
    "/review-statuses",
    response_model=List[LocationReviewStatus],
    summary="Get last reviewed date and review count per location"
)
async def get_locations_review_status(
    db: Session = Depends(get_db)
):
    from sqlalchemy import func, select
    from app.core.models.database import location_category

    stmt = select(
        location_category.c.location_id,
        func.max(location_category.c.last_reviewed).label("last_reviewed"),
        func.sum(location_category.c.review_count).label("review_count")
    ).group_by(location_category.c.location_id)

    results = db.execute(stmt).all()

    return [
        LocationReviewStatus(
            location_id=row.location_id,
            last_reviewed=row.last_reviewed,
            review_count=row.review_count
        )
        for row in results
    ]

@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Get location details",
    responses={404: {"description": "Location not found"}}
)
async def get_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    service = LocationService(db)
    return service.get_location(location_id)

@router.get(
    "/",
    response_model=List[LocationResponse],
    summary="List all locations",
    response_description="List of locations with their categories"
)
async def list_locations(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    service = LocationService(db)
    return service.list_locations(skip, limit, category_id)

@router.put(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Update location details",
    responses={404: {"description": "Location not found"}}
)
async def update_location(
    location_id: int,
    payload: LocationUpdate,
    db: Session = Depends(get_db)
):
    service = LocationService(db)
    return service.update_location(location_id, payload)

@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a location",
    responses={404: {"description": "Location not found"}}
)
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    service = LocationService(db)
    return service.delete_location(location_id)
