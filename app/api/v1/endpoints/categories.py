"""
Module: categories_endpoint

Defines HTTP routes for managing categories, delegating business logic to CategoryService.
Includes endpoints for creating, listing, updating, and deleting categories.
"""
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
) -> Category:
    """
    Register a new category with a unique name.

    :param payload: CategoryCreate schema containing the category name.
    :param db: Database session dependency.
    :return: The created Category model.
    :raises HTTPException: 400 if a category with the same name exists.
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
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Optional substring to filter category names"),
    db: Session = Depends(get_db)
) -> List[Category]:
    """
    Retrieve a paginated list of categories, optionally filtering by name.

    :param skip: Pagination offset.
    :param limit: Pagination limit.
    :param search: Optional search term to filter category names.
    :param db: Database session.
    :return: List of Category models matching criteria.
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
) -> Category:
    """
    Modify the name of an existing category.

    :param category_id: ID of the category to update.
    :param payload: CategoryUpdate schema with the new name.
    :param db: Database session.
    :return: Updated Category model.
    :raises HTTPException: 404 if category not found, 400 if name conflict.
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
) -> None:
    """
    Remove a category if it has no associated locations.

    :param category_id: ID of the category to delete.
    :param db: Database session.
    :raises HTTPException: 404 if not found, 409 if locations are linked.
    """
    service = CategoryService(db)
    return service.delete_category(category_id)
