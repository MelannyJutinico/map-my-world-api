"""
Module: locations_endpoint

Defines the HTTP routes for managing locations, delegating request validation and
routing to LocationService for business logic. Routes include creation, retrieval,
listing, update, deletion, and review status summary.
"""
from fastapi import APIRouter, Depends, status, Query
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
) -> LocationResponse:
    """
    Create a new location, enriched with optional category association or AI-based
    classification, and automated reverse geocoding for address details.

    :param payload: Data schema for Location creation.
    :param db: Database session injected by dependency.
    :return: The newly created Location including address and associated categories.
    :raises HTTPException: 400 if required data is missing, 404 if provided categories are invalid.
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
) -> List[LocationReviewStatus]:
    """
    Provide a summary of the most recent review and total review count for each location.

    :param db: Active database session.
    :return: List of LocationReviewStatus models containing review summaries.
    """
    # Direct SQL query for aggregation
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
) -> LocationResponse:
    """
    Fetch a single location by its ID, including associated category data.

    :param location_id: Unique identifier of the location.
    :param db: Database session.
    :return: Location data with categories.
    :raises HTTPException: 404 if the location does not exist.
    """
    service = LocationService(db)
    return service.get_location(location_id)

@router.get(
    "/",
    response_model=List[LocationResponse],
    summary="List all locations",
    response_description="List of locations with their categories"
)
async def list_locations(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=200, description="Pagination limit"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
) -> List[LocationResponse]:
    """
    Retrieve a paginated list of locations, optionally filtered by category.

    :param skip: Number of records to skip.
    :param limit: Maximum number of records to return.
    :param category_id: Optional category filter.
    :param db: Database session.
    :return: List of LocationResponse models.
    """
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
) -> LocationResponse:
    """
    Update basic fields of an existing location (description only).

    :param location_id: Identifier of the location to update.
    :param payload: Schema containing fields to change.
    :param db: Database session.
    :return: Updated Location model.
    :raises HTTPException: 404 if the location is not found.
    """
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
    """
    Remove a location record from the database by its ID.

    :param location_id: Identifier of the location to delete.
    :param db: Database session.
    :raises HTTPException: 404 if the location does not exist.
    """
    service = LocationService(db)
    return service.delete_location(location_id)
