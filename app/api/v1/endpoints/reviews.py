from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.models.schemas import LocationCategoryReview
from app.db.repositories.location_repository import LocationRepository
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
    repo = LocationRepository(db)
    if not repo.record_review(review.location_id, review.category_id, review.last_reviewed):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Location or category not found"
        )