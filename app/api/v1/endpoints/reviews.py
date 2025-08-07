from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.models.schemas import LocationCategoryReview
from app.core.services.review_service import ReviewService
from app.db.session import get_db

router = APIRouter(
    tags=["reviews"],   
    prefix="/reviews"
)

@router.post(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Record a location-category review",
    responses={
        204: {"description": "Review recorded successfully"},
        404: {"description": "Location or category not found"}
    }
)
async def record_review(
    review: LocationCategoryReview,
    db: Session = Depends(get_db)
):
    """
    Record that a specific location-category combination was reviewed.
    Updates the last_reviewed timestamp and increments review_count.
    """
    service = ReviewService(db)
    return service.record_review(review)
