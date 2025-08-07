from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.models.schemas import (
    Category,
    CategoryCreate,
    CategoryUpdate
)
from app.db.repositories.category_repository import CategoryRepository
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
        201: {"description": "Category created successfully"},
        400: {"description": "Category already exists"},
        422: {"description": "Validation error"}
    }
)
async def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new category with the following properties:
    
    - **name**: Required (2-50 characters, unique)
    """
    repo = CategoryRepository(db)
    
    if repo.get_category_by_name(category.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    return repo.create_category(category)


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
    Retrieve a paginated list of all categories.
    
    Supports basic search by name and pagination controls.
    """
    repo = CategoryRepository(db)
    return repo.get_categories(skip=skip, limit=limit, search=search)

@router.put(
    "/{category_id}",
    response_model=Category,
    summary="Update a category",
    responses={
        200: {"description": "Category updated successfully"},
        400: {"description": "Category name already exists"},
        404: {"description": "Category not found"}
    }
)
async def update_category(
    category_id: int,
    category: CategoryUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update an existing category.
    
    - All fields are optional
    - At least one field must be provided
    """
    repo = CategoryRepository(db)
    
    db_category = repo.get_category(category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    if category.name and repo.get_category_by_name(category.name, exclude_id=category_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    return repo.update_category(category_id, category)

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category",
    responses={
        204: {"description": "Category deleted successfully"},
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
    
    Note: Cannot delete categories that have associated locations.
    """
    repo = CategoryRepository(db)
    
    db_category = repo.get_category_with_locations(category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    if db_category.locations:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category with associated locations"
        )
    
    repo.delete_category(category_id)
    return None