from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.services.recommendation_service import RecommendationService
from app.core.models.schemas import RecommendationScore
from app.db.session import get_db

router = APIRouter(
    tags=["recommendations"],
    prefix="/recommendations"
)

@router.get(
    "/",
    response_model=List[RecommendationScore],
    summary="Get prioritized review recommendations",
    response_description="List of location-category pairs needing review",
    responses={200: {"description": "Successfully retrieved recommendations"}}
)
async def get_recommendations(
    limit: int = Query(
        10,
        description="Number of recommendations to return (max 20)",
        ge=1,
        le=20
    ),
    db: Session = Depends(get_db)
):
    """
    Retrieve location-category combinations that need review, prioritized by:

    - **Never reviewed**: Highest priority (score = 100)
    - **Reviewed >30 days ago**: Priority proportional to days since review (score = days * 2, capped at 100)

    Returns top recommendations sorted by score.
    """
    service = RecommendationService(db)
    return service.get_recommendations(limit)
