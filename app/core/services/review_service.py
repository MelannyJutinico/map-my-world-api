from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.repositories.location_repository import LocationRepository
from app.core.models.schemas import LocationCategoryReview

class ReviewService:
    def __init__(self, db: Session):
        self.repo = LocationRepository(db)

    def record_review(self, review: LocationCategoryReview) -> None:
        """
        Record that a specific location-category combination was reviewed.
        Raises HTTPException if the combination does not exist.
        """
        success = self.repo.record_review(review.location_id, review.category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location or category not found"
            )
        return None
