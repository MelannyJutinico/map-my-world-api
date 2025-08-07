from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.repositories.location_repository import LocationRepository
from app.db.repositories.category_repository import CategoryRepository
from app.core.models.schemas import LocationCreate, LocationUpdate
from app.core.utils.geocoding import reverse_geocode
from app.core.utils.nlp import classify_description

class LocationService:
    """
    Manages operations related to locations, including creation, retrieval, update, and deletion.

    This service handles:
    - Validation of input data
    - Category association and zero-shot classification
    - Reverse geocoding for missing address details
    - Delegation to the LocationRepository for database interactions
    """

    def __init__(self, db: Session):
        """
        Initialize the service with a database session.

        :param db: SQLAlchemy Session instance for data access
        """
        self.db = db
        self.repo = LocationRepository(db)
        self.cat_repo = CategoryRepository(db)

    async def create_location(self, payload: LocationCreate):
        """
        Create a new location record with associated categories or inferred category.

        Steps:
        1. Validate that either category_ids or description is provided.
        2. If category_ids are given, verify they exist; otherwise infer via NLP.
        3. Fetch address, city, and country via reverse geocoding if missing.
        4. Delegate to repository to persist the new location and associations.

        :param payload: LocationCreate schema containing input data
        :return: The created Location model instance
        :raises HTTPException: 400 for missing data, 404 for invalid categories
        """
        if not payload.category_ids and not payload.description:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either category_ids or description must be provided"
            )

        if payload.category_ids:
            existing = self.cat_repo.get_categories_by_ids(payload.category_ids)
            if len(existing) != len(set(payload.category_ids)):
                missing = set(payload.category_ids) - {c.id for c in existing}
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Categories not found: {sorted(missing)}"
                )
            chosen_ids = payload.category_ids
        else:
            categories = self.cat_repo.get_categories()
            labels = [c.name for c in categories]
            predicted = classify_description(payload.description, labels)
            matched = self.cat_repo.get_category_by_name(predicted) if predicted else None
            chosen_ids = [matched.id] if matched else []

        geo_data = {}
        if not payload.address or not payload.city or not payload.country:
            geo_data = await reverse_geocode(payload.latitude, payload.longitude) or {}

        loc_data = payload.model_dump(exclude={"category_ids"})
        loc_data["address"] = loc_data.get("address") or geo_data.get("address")
        loc_data["city"] = loc_data.get("city") or geo_data.get("city")
        loc_data["country"] = loc_data.get("country") or geo_data.get("country")

        return self.repo.create_location_with_categories(
            location_data=loc_data,
            category_ids=chosen_ids
        )

    def get_location(self, location_id: int):
        """
        Retrieve a single location by its ID, including associated categories.

        :param location_id: Identifier of the location to fetch
        :return: Location model instance
        :raises HTTPException: 404 if no such location exists
        """
        loc = self.repo.get_location_with_categories(location_id)
        if not loc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )
        return loc

    def list_locations(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None
    ) -> List:
        """
        List locations with optional pagination and category filter.

        :param skip: Number of records to skip for pagination
        :param limit: Maximum number of records to return
        :param category_id: Optional category ID to filter by
        :return: List of Location model instances
        """
        return self.repo.get_locations_with_categories(skip, limit, category_id)

    def update_location(self, location_id: int, payload: LocationUpdate):
        """
        Update basic information of an existing location.

        :param location_id: Identifier of the location to update
        :param payload: LocationUpdate schema with fields to modify
        :return: Updated Location model instance
        :raises HTTPException: 404 if no such location exists
        """
        updated = self.repo.update_location(location_id, payload)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )
        return updated

    def delete_location(self, location_id: int):
        """
        Remove a location record by its ID.

        :param location_id: Identifier of the location to delete
        :return: None
        :raises HTTPException: 404 if no such location exists
        """
        if not self.repo.delete_location(location_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )
        return None
