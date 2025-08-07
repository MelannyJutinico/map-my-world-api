from sqlalchemy import Column, Integer, Float, String, Text, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.session import Base

location_category = Table(
    'location_category',
    Base.metadata,
    Column('location_id', Integer, ForeignKey('locations.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True),
    Column('last_reviewed', DateTime, nullable=True),
    Column('review_count', Integer, default=0)
)

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    categories = relationship("Category", secondary=location_category, back_populates="locations")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    locations = relationship("Location", secondary=location_category, back_populates="categories")