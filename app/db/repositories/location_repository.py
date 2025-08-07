"""
Module: location_repository

Provides data access methods for Location entities and related review metadata
using SQLAlchemy. Supports CRUD operations, association with categories, and
specialized queries for review recommendation logic.
"""
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, select, or_
from app.core.models.database import Category, Location, location_category
from app.core.models.schemas import LocationUpdate

class LocationRepository:
    """
    Repository handling persistence and retrieval for Location and its
    relationships, including review tracking and recommendation queries.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.

        :param db: Active SQLAlchemy Session instance
        """
        self.db = db

    def create_location_with_categories(
        self,
        location_data: dict,
        category_ids: Optional[List[int]] = None
    ) -> Location:
        """
        Create a new Location record and associate it with existing categories.

        :param location_data: Dictionary of Location fields (latitude, longitude,
                              description, address, city, country)
        :param category_ids: Optional list of category IDs to link
        :return: The newly created Location instance with categories loaded
        """
        location = Location(**location_data)
        self.db.add(location)
        self.db.flush()

        if category_ids:
            categories = (
                self.db.query(Category)
                .filter(Category.id.in_(category_ids))
                .all()
            )
            location.categories.extend(categories)

        self.db.commit()
        self.db.refresh(location)
        return location

    def get_location_with_categories(self, location_id: int) -> Optional[Location]:
        """
        Retrieve a Location by ID, including its associated categories.

        :param location_id: Identifier of the Location
        :return: Location instance with categories or None if not found
        """
        return (
            self.db.query(Location)
            .options(joinedload(Location.categories))
            .get(location_id)
        )

    def get_locations_with_categories(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None
    ) -> List[Location]:
        """
        List Location records with optional filtering by category and pagination.

        :param skip: Number of records to skip for paging
        :param limit: Maximum number of records to return
        :param category_id: Optional category ID to filter locations
        :return: List of Location instances with categories loaded
        """
        query = self.db.query(Location).options(joinedload(Location.categories))

        if category_id:
            query = (
                query
                .join(Location.categories)
                .filter(Category.id == category_id)
            )

        return query.offset(skip).limit(limit).all()

    def update_location(
        self,
        location_id: int,
        location_update: LocationUpdate
    ) -> Optional[Location]:
        """
        Update mutable fields of an existing Location.

        :param location_id: Identifier of the Location
        :param location_update: Pydantic schema with fields to change
        :return: Updated Location instance or None if not found
        """
        loc = self.get_location_with_categories(location_id)
        if not loc:
            return None

        changes = location_update.model_dump(exclude_unset=True)
        for field, value in changes.items():
            setattr(loc, field, value)

        self.db.commit()
        self.db.refresh(loc)
        return loc

    def delete_location(self, location_id: int) -> bool:
        """
        Delete a Location record by its ID.

        :param location_id: Identifier of the Location to remove
        :return: True if deletion succeeded, False otherwise
        """
        loc = self.db.query(Location).get(location_id)
        if not loc:
            return False

        self.db.delete(loc)
        self.db.commit()
        return True

    def record_review(
        self,
        location_id: int,
        category_id: int,
        last_reviewed : datetime
    ) -> bool:
        """
        Update review metadata for a specific location-category pair.

        Sets the last_reviewed timestamp to now and increments review_count.

        :param location_id: Identifier of the Location
        :param category_id: Identifier of the Category
        :param last_reviewed: Last reviewed time
        :return: True if the pair exists and update succeeded, False otherwise
        """
        relation = (
            self.db.execute(
                select(location_category)
                .where(location_category.c.location_id == location_id)
                .where(location_category.c.category_id == category_id)
            )
            .first()
        )

        if not relation:
            return False

        self.db.execute(
            location_category.update()
            .where(location_category.c.location_id == location_id)
            .where(location_category.c.category_id == category_id)
            .values(
                last_reviewed=last_reviewed,
                review_count=location_category.c.review_count + 1
            )
        )
        self.db.commit()
        return True

    def get_review_recommendations(
        self,
        limit: int = 10
    ) -> List[dict]:
        """
        Fetch top location-category combinations needing review,
        prioritizing pairs never reviewed or not reviewed in the last 30 days.

        Scores are calculated as:
          - 100 for never-reviewed items
          - days since last review * 2 (capped at 100) for others

        :param limit: Maximum number of recommendation entries to return
        :return: List of dictionaries with recommendation details
        """
        cutoff = datetime.utcnow() - timedelta(days=30)

        stmt = (
            select(
                location_category.c.location_id,
                location_category.c.category_id,
                location_category.c.last_reviewed,
                Location.address.label("location_name"),
                Category.name.label("category_name")
            )
            .join(Location, Location.id == location_category.c.location_id)
            .join(Category, Category.id == location_category.c.category_id)
            .where(
                or_(
                    location_category.c.last_reviewed.is_(None),
                    location_category.c.last_reviewed < cutoff
                )
            )
        )

        rows = self.db.execute(stmt).all()
        result = []

        for loc_id, cat_id, last_rev, loc_name, cat_name in rows:
            if last_rev is None:
                score = 100.0
                days = None
            else:
                days = (datetime.utcnow() - last_rev).days
                score = min(100.0, days * 2)

            result.append({
                "location_id": loc_id,
                "category_id": cat_id,
                "score": round(score, 2),
                "last_reviewed": last_rev,
                "days_since_review": days,
                "location_name": loc_name or f"Location {loc_id}",
                "category_name": cat_name
            })

        # Sort by score descending, then by earliest review if tied
        result.sort(key=lambda x: (-x["score"], x["last_reviewed"] or datetime.min))
        return result[:limit]
