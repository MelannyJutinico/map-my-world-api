"""
Module: category_repository

Provides data access methods for Category entities using SQLAlchemy.
Includes operations to create, retrieve, update, and delete categories,
as well as queries filtered by related location data.
"""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.core.models.database import Category
from app.core.models.schemas import CategoryCreate, CategoryUpdate

class CategoryRepository:
    """
    Repository for CRUD operations on Category model.
    """
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        :param db: Active SQLAlchemy Session
        """
        self.db = db

    def create_category(self, category: CategoryCreate) -> Category:
        """
        Create and persist a new Category record.

        :param category: Pydantic schema with name attribute
        :return: The newly created Category instance
        """
        db_category = Category(**category.model_dump())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def get_category(self, category_id: int) -> Optional[Category]:
        """
        Retrieve a Category by its primary key.

        :param category_id: Identifier of the category
        :return: Category instance or None if not found
        """
        return self.db.query(Category).get(category_id)

    def get_category_with_locations(self, category_id: int) -> Optional[Category]:
        """
        Fetch a Category along with its associated locations.

        :param category_id: Identifier of the category
        :return: Category instance with populated locations, or None
        """
        return self.db.query(Category).options(
            joinedload(Category.locations)
        ).get(category_id)

    def get_category_by_name(
        self,
        name: str,
        exclude_id: Optional[int] = None
    ) -> Optional[Category]:
        """
        Find a Category by name, optionally excluding a specific ID.

        :param name: Name to search for
        :param exclude_id: Category ID to exclude from search
        :return: First matching Category or None
        """
        query = self.db.query(Category).filter(Category.name == name)
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        return query.first()

    def get_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Category]:
        """
        List categories with pagination and optional search by name.

        :param skip: Number of records to skip
        :param limit: Maximum records to return
        :param search: Optional substring to filter category names
        :return: List of Category instances
        """
        query = self.db.query(Category)
        if search:
            query = query.filter(Category.name.ilike(f"%{search}%"))
        return query.offset(skip).limit(limit).all()

    def update_category(
        self,
        category_id: int,
        category: CategoryUpdate
    ) -> Optional[Category]:
        """
        Update fields of an existing Category.

        :param category_id: Identifier of the category to update
        :param category: Pydantic schema with update data
        :return: Updated Category or None if not found
        """
        db_category = self.get_category(category_id)
        if not db_category:
            return None
        update_data = category.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def get_categories_by_ids(self, category_ids: List[int]) -> List[Category]:
        """
        Retrieve multiple Category records by a list of IDs.

        :param category_ids: List of category IDs
        :return: List of matching Category instances
        """
        return self.db.query(Category).filter(
            Category.id.in_(category_ids)
        ).all()

    def delete_category(self, category_id: int) -> bool:
        """
        Remove a Category by its ID.

        :param category_id: Identifier of the category to delete
        :return: True if deletion succeeded, False if not found
        """
        db_category = self.get_category(category_id)
        if not db_category:
            return False
        self.db.delete(db_category)
        self.db.commit()
        return True
