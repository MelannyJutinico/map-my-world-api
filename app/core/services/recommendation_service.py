from typing import List
from sqlalchemy.orm import Session
from app.db.repositories.location_repository import LocationRepository
from app.core.models.schemas import RecommendationScore

class RecommendationService:
    def __init__(self, db: Session):
        self.repo = LocationRepository(db)

    def get_recommendations(self, limit: int) -> List[RecommendationScore]:
        """
        Retrieve prioritized review recommendations transformed into Pydantic models.

        - **limit**: number of recommendations to return.
        """
        raw = self.repo.get_review_recommendations(limit)
        # Convert each dict to RecommendationScore
        return [RecommendationScore(**item) for item in raw]
