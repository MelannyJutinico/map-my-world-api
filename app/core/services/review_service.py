from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.db.repositories.location_repository import LocationRepository
from app.core.models.schemas import LocationCategoryReview

class ReviewService:
    """
    Provides operations related to reviewing location-category combinations.
    """

    def __init__(self, db: Session):
        """
        Initialize the review service with a database session.

        :param db: Active SQLAlchemy Session for repository access.
        """
        self.repo = LocationRepository(db)

    def record_review(self, review: LocationCategoryReview) -> None:
        """
        Record that a specific location-category pair was reviewed.

        Updates the last_reviewed timestamp and increments the review count.
        Raises an HTTPException if the pair does not exist in the database.

        :param review: Model containing location_id and category_id.
        :raises HTTPException: 404 error when the combination is not found.
        """
        success = self.repo.record_review(review.location_id, review.category_id, review.last_reviewed)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Location or category combination not found"
            )
        # Successful review recorded; endpoint will return 204 No Content.
        return None
