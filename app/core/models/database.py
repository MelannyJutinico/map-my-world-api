"""
Database models and association table definitions for Map My World application.

This module defines the ORM mappings using SQLAlchemy for Location and Category
entities, as well as the many-to-many relationship table `location_category` which
tracks review metadata.
"""

from sqlalchemy import Column, Integer, Float, String, Text, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base

# Association table linking locations and categories.
# Tracks when a combination was last reviewed and total review count.
location_category = Table(
    'location_category',
    Base.metadata,
    Column('location_id', Integer, ForeignKey('locations.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True),
    Column('last_reviewed', DateTime, nullable=True),
    Column('review_count', Integer, default=0)
)

class Location(Base):
    """
    Represents a geographical point of interest.

    Attributes:
        id (int): Primary key for the location.
        latitude (float): Latitude coordinate in degrees.
        longitude (float): Longitude coordinate in degrees.
        description (str|None): Optional text for AI-based categorization or notes.
        address (str|None): Full formatted address from reverse geocoding.
        city (str|None): City name extracted from geocoding.
        country (str|None): Country name extracted from geocoding.
        categories (List[Category]): List of associated Category instances.
    """
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Establish many-to-many relationship via location_category table.
    categories = relationship(
        "Category",
        secondary=location_category,
        back_populates="locations"
    )

class Category(Base):
    """
    Represents a classification label for locations.

    Attributes:
        id (int): Primary key for the category.
        name (str): Unique name of the category (e.g., "Park").
        locations (List[Location]): List of associated Location instances.
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    # Establish many-to-many relationship via location_category table.
    locations = relationship(
        "Location",
        secondary=location_category,
        back_populates="categories"
    )
