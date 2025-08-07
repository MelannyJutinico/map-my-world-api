from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.repositories.location_repository import LocationRepository
from app.db.repositories.category_repository import CategoryRepository
from app.core.models.schemas import LocationCreate, LocationUpdate
from app.core.utils.geocoding import reverse_geocode
from app.core.utils.nlp import classify_description

class LocationService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = LocationRepository(db)
        self.cat_repo = CategoryRepository(db)

    async def create_location(self, payload: LocationCreate):
   
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
        return self.repo.get_locations_with_categories(skip, limit, category_id)

    def update_location(self, location_id: int, payload: LocationUpdate):
        updated = self.repo.update_location(location_id, payload)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )
        return updated

    def delete_location(self, location_id: int):
        if not self.repo.delete_location(location_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location not found"
            )
        return None
