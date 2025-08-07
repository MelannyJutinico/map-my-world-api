from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.models.schemas import (
    Category,
    CategoryCreate,
    CategoryUpdate
)
from app.core.services.category_service import CategoryService
from app.db.session import get_db

router = APIRouter(
    tags=["categories"],
    prefix="/categories"
)

@router.post(
    "/",
    response_model=Category,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    responses={
        400: {"description": "Category already exists"},
        422: {"description": "Validation error"}
    }
)
async def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new category.
    """
    service = CategoryService(db)
    return service.create_category(payload)

@router.get(
    "/",
    response_model=List[Category],
    summary="List all categories",
    response_description="List of categories"
)
async def list_categories(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=200, description="Pagination limit"),
    search: Optional[str] = Query(None, description="Search by name"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a paginated list of categories.
    """
    service = CategoryService(db)
    return service.list_categories(skip, limit, search)

@router.put(
    "/{category_id}",
    response_model=Category,
    summary="Update a category",
    responses={
        404: {"description": "Category not found"},
        400: {"description": "Category name already exists"},
        422: {"description": "Validation error"}
    }
)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing category.
    """
    service = CategoryService(db)
    return service.update_category(category_id, payload)

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
    responses={
        404: {"description": "Category not found"},
        409: {"description": "Category has associated locations"}
    }
)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a category by its ID.
    """
    service = CategoryService(db)
    return service.delete_category(category_id)
