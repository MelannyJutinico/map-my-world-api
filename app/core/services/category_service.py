from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.repositories.category_repository import CategoryRepository
from app.core.models.schemas import CategoryCreate, CategoryUpdate

class CategoryService:
    def __init__(self, db: Session):
        self.repo = CategoryRepository(db)

    def create_category(self, payload: CategoryCreate):
        # Ensure unique category name
        if self.repo.get_category_by_name(payload.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        return self.repo.create_category(payload)

    def list_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List:
        # Paginated retrieval with optional search
        return self.repo.get_categories(skip=skip, limit=limit, search=search)

    def update_category(self, category_id: int, payload: CategoryUpdate):
        # Verify existence
        existing = self.repo.get_category(category_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        # Check for name conflict
        if payload.name and self.repo.get_category_by_name(payload.name, exclude_id=category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        return self.repo.update_category(category_id, payload)

    def delete_category(self, category_id: int):
        # Verify existence with related locations
        existing = self.repo.get_category_with_locations(category_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        # Prevent deletion if in use
        if existing.locations:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete category with associated locations"
            )
        self.repo.delete_category(category_id)
        return None
