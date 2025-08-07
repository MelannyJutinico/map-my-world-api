from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.models.schemas import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
    Category
)
from app.db.repositories.location_repository import LocationRepository
from app.db.repositories.category_repository import CategoryRepository
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
        201: {"description": "Location created successfully"},
        400: {"description": "Missing required data"},
        404: {"description": "Category not found"},
        422: {"description": "Validation error"}
    }
)
async def create_location(
    location: LocationCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new location with optional categories.

    Requires either:
    - Existing category IDs (category_ids)
    - Or a description for AI categorization
    
    Parameters:
    - **latitude**: Required (-90 to 90)
    - **longitude**: Required (-180 to 180)
    - **description**: Optional text description
    - **category_ids**: Optional list of existing category IDs
    """
    repo = LocationRepository(db)
    category_repo = CategoryRepository(db)
    
    if not location.category_ids and not location.description:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either category_ids or description must be provided"
        )
    
    if location.category_ids:
        existing_cats = category_repo.get_categories_by_ids(location.category_ids)
        if len(existing_cats) != len(set(location.category_ids)):
            missing = set(location.category_ids) - {c.id for c in existing_cats}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categories not found: {sorted(missing)}"
            )
    
    # Crear la ubicación
    location_data = location.model_dump(exclude={"category_ids"})
    return repo.create_location_with_categories(
        location_data=location_data,
        category_ids=location.category_ids
    )

@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Get location details",
    responses={
        200: {"description": "Location details"},
        404: {"description": "Location not found"}
    }
)
async def get_location(
    location_id: int, 
    db: Session = Depends(get_db)
):
    """
    Get complete details for a specific location by ID.
    
    Includes:
    - Basic location info
    - Associated categories
    """
    repo = LocationRepository(db)
    if not (location := repo.get_location_with_categories(location_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return location

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
):
    """
    Retrieve paginated list of locations.
    
    Optional filters:
    - category_id: Filter by category
    """
    repo = LocationRepository(db)
    return repo.get_locations_with_categories(
        skip=skip,
        limit=limit,
        category_id=category_id
    )

@router.put(
    "/{location_id}",
    response_model=LocationResponse,
    summary="Update location details",
    responses={
        200: {"description": "Location updated"},
        400: {"description": "Invalid data"},
        404: {"description": "Location not found"}
    }
)
async def update_location(
    location_id: int,
    location: LocationUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update location basic information.
    
    Note: Does not update categories (use separate endpoint)
    """
    repo = LocationRepository(db)
    if not (updated := repo.update_location(location_id, location)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )
    return updated

@router.delete(
    "/{location_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a location",
    responses={
        204: {"description": "Location deleted"},
        404: {"description": "Location not found"}
    }
)
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a location by ID.
    """
    repo = LocationRepository(db)
    if not repo.delete_location(location_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location not found"
        )