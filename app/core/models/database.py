from sqlalchemy import Column, Integer, Float, String, Text
from app.db.session import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True) 
    country = Column(String, nullable=True)  
    city = Column(String, nullable=True)  
    adress = Column(String, nullable=True)  