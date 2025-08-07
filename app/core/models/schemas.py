from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Union

class LocationBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, example=40.7128)
    longitude: float = Field(..., ge=-180, le=180, example=-74.0060)
    description: Optional[str] = Field(None, example="Famous landmark")

class LocationCreate(LocationBase):
    category_ids: Optional[List[int]] = Field(
        None, 
        description="IDs of existing categories to associate"
    )
    description: Optional[str] = Field(
        None, 
        description="Description for AI automatic categorization"
    )

class LocationUpdate(BaseModel):
    description: Optional[str] = Field(None, example="Updated description")

class Location(LocationBase):
    id: int
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    
    class Config:
        from_attributes = True  

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)

class Category(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

class LocationWithCategories(Location):
    categories: List[Category] = []

class LocationReviewStatus(BaseModel):
    location_id: int
    last_reviewed: Optional[datetime]
    review_count: int


class LocationResponse(LocationBase):
    id: int
    categories: List[Category] = []
    
    class Config:
        from_attributes = True

class LocationCategoryReview(BaseModel):
    location_id: int
    category_id: int
    last_reviewed: datetime 

class RecommendationScore(BaseModel):
    location_id: int
    category_id: int
    score: float
    last_reviewed: Optional[datetime] = None
    days_since_review: Optional[int] = None
    location_name: str
    category_name: str
        