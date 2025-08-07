from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.repositories.category_repository import CategoryRepository
from app.core.models.schemas import CategoryCreate, CategoryUpdate

class CategoryService:
    """
    Encapsulates business logic for category management, including creation, listing,
    updating and deletion of categories.
    """

    def __init__(self, db: Session):
        """
        Initialize the service with a database session.

        :param db: SQLAlchemy Session for interacting with repositories
        """
        self.repo = CategoryRepository(db)

    def create_category(self, payload: CategoryCreate):
        """
        Create a new category with a unique name.

        Validates that no other category shares the same name before persisting.

        :param payload: CategoryCreate schema containing the name to register
        :return: Newly created Category model
        :raises HTTPException: 400 if the category name already exists
        """
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
        """
        Retrieve a paginated list of categories, with optional name-based search.

        :param skip: Number of records to skip for pagination
        :param limit: Maximum number of records to return
        :param search: Optional substring to filter category names
        :return: List of Category models matching criteria
        """
        return self.repo.get_categories(skip=skip, limit=limit, search=search)

    def update_category(self, category_id: int, payload: CategoryUpdate):
        """
        Update the name of an existing category.

        Ensures the category exists and that the new name does not conflict with
        another category.

        :param category_id: Identifier of the category to update
        :param payload: CategoryUpdate schema containing the new name
        :return: Updated Category model
        :raises HTTPException: 404 if category not found, 400 if name conflict
        """
        existing = self.repo.get_category(category_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        if payload.name and self.repo.get_category_by_name(payload.name, exclude_id=category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
        return self.repo.update_category(category_id, payload)

    def delete_category(self, category_id: int):
        """
        Remove a category by its ID, if it has no associated locations.

        Prevents deletion when the category is still in use by any location.

        :param category_id: Identifier of the category to delete
        :return: None
        :raises HTTPException: 404 if category not found, 409 if still in use
        """
        existing = self.repo.get_category_with_locations(category_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        if existing.locations:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete category with associated locations"
            )
        self.repo.delete_category(category_id)
        return None
