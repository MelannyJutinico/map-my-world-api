from pydantic import BaseModel, Field, field_validator
from typing import Optional

class LocationBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, example=40.7128)
    longitude: float = Field(..., ge=-180, le=180, example=-74.0060)
    description: Optional[str] = None


class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    
    class Config:
        from_attributes = True  