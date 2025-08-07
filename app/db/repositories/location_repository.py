
from typing import List
from sqlalchemy import  func, or_, select
from sqlalchemy.orm import Session, joinedload
from app.core.models.database import Category, Location, location_category
from app.core.models.schemas import LocationUpdate
from datetime import datetime, timedelta
from sqlalchemy import func, select

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_location_with_categories(self, location_data: dict, category_ids: List[int] = None):
        location = Location(**location_data)
        self.db.add(location)
        self.db.flush()  
        
        if category_ids:
            categories = self.db.query(Category).filter(Category.id.in_(category_ids)).all()
            location.categories.extend(categories)
        
        self.db.commit()
        self.db.refresh(location)
        return location

    def get_location_with_categories(self, location_id: int):
        return self.db.query(Location).options(
            joinedload(Location.categories)
        ).get(location_id)

    def get_locations_with_categories(self, skip: int = 0, limit: int = 100, category_id: int = None):
        query = self.db.query(Location).options(
            joinedload(Location.categories)
        )
        
        if category_id:
            query = query.join(Location.categories).filter(Category.id == category_id)
            
        return query.offset(skip).limit(limit).all()

    def update_location(self, location_id: int, location: LocationUpdate):
        db_location = self.get_location_with_categories(location_id)
        if not db_location:
            return None
        
        update_data = location.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_location, field, value)
        
        self.db.commit()
        self.db.refresh(db_location)
        return db_location

    def delete_location(self, location_id: int):
        if location := self.db.query(Location).get(location_id):
            self.db.delete(location)
            self.db.commit()
            return True
        return False
        
    def record_review(self, location_id: int, category_id: int, last_reviewed_: datetime) -> bool:
        """Record a review for a location-category pair"""
        relation = self.db.execute(
            select(location_category)
            .where(location_category.c.location_id == location_id)
            .where(location_category.c.category_id == category_id)
        ).first()
        
        if not relation:
            return False
        
        self.db.execute(
            location_category.update()
            .where(location_category.c.location_id == location_id)
            .where(location_category.c.category_id == category_id)
            .values(
                last_reviewed=last_reviewed_,
                review_count=location_category.c.review_count + 1
            )
        )
        self.db.commit()
        return True

    def get_review_recommendations(self, limit: int = 10) -> List[dict]:
        """Get top location-category pairs not reviewed in the last 30 days, prioritized by a score."""
        # Define cutoff datetime
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        # Select pairs never reviewed or reviewed before the cutoff
        stmt = select(
            location_category.c.location_id,
            location_category.c.category_id,
            location_category.c.last_reviewed,
            Location.address.label("location_name"),
            Category.name.label("category_name")
        ).join(
            Location, Location.id == location_category.c.location_id
        ).join(
            Category, Category.id == location_category.c.category_id
        ).where(
            or_(
                location_category.c.last_reviewed.is_(None),
                location_category.c.last_reviewed < thirty_days_ago
            )
        )

        rows = self.db.execute(stmt).all()
        recommendations = []

        for location_id, category_id, last_reviewed, location_name, category_name in rows:
            if last_reviewed is None:
                days_since = None
                score = 100.0
            else:
                days_since = (datetime.utcnow() - last_reviewed).days
                score = min(100.0, days_since * 2)

            recommendations.append({
                "location_id": location_id,
                "category_id": category_id,
                "score": round(score, 2),
                "last_reviewed": last_reviewed,
                "days_since_review": days_since,
                "location_name": location_name or f"Location {location_id}",
                "category_name": category_name
            })

        recommendations.sort(
            key=lambda x: (-x["score"], x["last_reviewed"] or datetime.min)
        )

        return recommendations[:limit]