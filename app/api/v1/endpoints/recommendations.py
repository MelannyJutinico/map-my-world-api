"""
Module: recommendations_endpoint

Defines the HTTP route for retrieving location-category review recommendations.
Delegates scoring and sorting logic to RecommendationService to maintain thin controllers.
"""
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
    Fetch top location-category combinations requiring review.

    - Never reviewed combinations receive the highest priority (score = 100).
    - Those not reviewed in over 30 days are scored by days_since_review * 2, capped at 100.

    :param limit: Maximum number of recommendations to return
    :type limit: int
    :param db: Database session dependency
    :return: List of RecommendationScore models
    """
    service = RecommendationService(db)
    return service.get_recommendations(limit)
