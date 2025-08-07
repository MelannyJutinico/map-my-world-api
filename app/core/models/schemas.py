from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Union

class LocationBase(BaseModel):
    """
    Base schema for location input and output, containing geographic coordinates and 
    an optional description for classification or informational purposes.
    """
    latitude: float = Field(
        ..., ge=-90, le=90,
        description="Latitude of the location in degrees (-90 to 90)",
        example=40.7128
    )
    longitude: float = Field(
        ..., ge=-180, le=180,
        description="Longitude of the location in degrees (-180 to 180)",
        example=-74.0060
    )
    description: Optional[str] = Field(
        None,
        description="Text description used for AI-based category inference",
        example="Famous landmark"
    )

class LocationCreate(LocationBase):
    """
    Schema for creating a new location. Extends LocationBase with fields
    to associate categories or provide address details directly.
    """
    category_ids: Optional[List[int]] = Field(
        None,
        description="List of existing category IDs to associate with this location"
    )
    address: Optional[str] = Field(
        None,
        description="Formatted address of the location, if known"
    )
    city: Optional[str] = Field(
        None,
        description="City where the location is situated"
    )
    country: Optional[str] = Field(
        None,
        description="Country where the location is situated"
    )

class LocationUpdate(BaseModel):
    """
    Schema for updating mutable fields of an existing location.
    Only fields provided will be updated.
    """
    description: Optional[str] = Field(
        None,
        description="New description for AI categorization or informational update",
        example="Updated description"
    )

class Location(LocationBase):
    """
    Represents a location record as stored in the database, with 
    identifiers and enriched address metadata.
    """
    id: int = Field(..., description="Unique identifier of the location")
    address: Optional[str] = Field(
        None,
        description="Full formatted address"
    )
    city: Optional[str] = Field(
        None,
        description="City of the location"
    )
    country: Optional[str] = Field(
        None,
        description="Country of the location"
    )

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    """
    Base schema for category definitions, containing only the name.
    """
    name: str = Field(
        ..., min_length=2, max_length=50,
        description="Name of the category (2-50 characters)"
    )

class CategoryCreate(CategoryBase):
    """
    Schema for creating a new category. Inherits name validation.
    """
    pass

class CategoryUpdate(BaseModel):
    """
    Schema for updating an existing category's name.
    """
    name: Optional[str] = Field(
        None, min_length=2, max_length=50,
        description="New name for the category (leave empty to keep current)"
    )

class Category(CategoryBase):
    """
    Represents a category record as stored in the database.
    """
    id: int = Field(..., description="Unique identifier of the category")

    class Config:
        from_attributes = True

class LocationWithCategories(Location):
    """
    Extends the Location schema by including its associated categories.
    """
    categories: List[Category] = Field(
        default_factory=list,
        description="List of categories linked to this location"
    )

class LocationReviewStatus(BaseModel):
    """
    Summary of review status for a location, aggregating review dates and counts.
    """
    location_id: int = Field(..., description="Identifier of the location")
    last_reviewed: Optional[datetime] = Field(
        None, description="Timestamp of the most recent review"
    )
    review_count: int = Field(..., description="Total number of reviews recorded")

class LocationResponse(LocationBase):
    """
    Schema for API responses that return location data along with metadata and categories.
    """
    id: int = Field(..., description="Unique identifier of the location")
    address: Optional[str] = Field(None, description="Formatted address")
    city: Optional[str] = Field(None, description="City of the location")
    country: Optional[str] = Field(None, description="Country of the location")
    categories: List[Category] = Field(
        default_factory=list,
        description="List of categories associated with this location"
    )

    class Config:
        from_attributes = True

class LocationCategoryReview(BaseModel):
    """
    Schema for recording a review event on a location-category combination.
    """
    location_id: int = Field(..., description="Identifier of the location reviewed")
    category_id: int = Field(..., description="Identifier of the category reviewed")
    last_reviewed: datetime = Field(
        ..., description="Timestamp when the review occurred"
    )

class RecommendationScore(BaseModel):
    """
    Represents the priority score for a location-category pair needing review.
    """
    location_id: int = Field(..., description="ID of the location")
    category_id: int = Field(..., description="ID of the category")
    score: float = Field(..., description="Priority score for review (0-100 scale)")
    last_reviewed: Optional[datetime] = Field(
        None, description="Last reviewed timestamp, if any"
    )
    days_since_review: Optional[int] = Field(
        None, description="Number of days since last review"
    )
    location_name: str = Field(..., description="Name or address of the location")
    category_name: str = Field(..., description="Name of the category")
