from typing import List
from sqlalchemy.orm import Session
from app.db.repositories.location_repository import LocationRepository
from app.core.models.schemas import RecommendationScore

class RecommendationService:
    """
    Handles fetching and formatting of location-category review recommendations.
    """

    def __init__(self, db: Session):
        """
        Initialize the recommendation service with a database session.

        :param db: Active SQLAlchemy Session for repository access.
        """
        self.repo = LocationRepository(db)

    def get_recommendations(self, limit: int) -> List[RecommendationScore]:
        """
        Retrieve a list of top location-category pairs that require review.

        This method calls the repository to obtain raw recommendation data,
        then converts each dictionary into a RecommendationScore model for
        consistent API responses.

        :param limit: Maximum number of recommendations to return.
        :return: List of RecommendationScore instances.
        """
        raw_data = self.repo.get_review_recommendations(limit)
        return [RecommendationScore(**item) for item in raw_data]
