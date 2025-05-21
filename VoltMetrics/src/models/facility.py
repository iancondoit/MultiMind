"""
Facility model for VoltMetrics.

This module defines the SQLAlchemy model for electrical facilities.
"""

from sqlalchemy import Column, String, Integer, Float, JSON
from sqlalchemy.orm import relationship

from src.db.database import Base


class Facility(Base):
    """
    SQLAlchemy model for electrical facilities.
    
    Represents a physical facility or building containing electrical equipment.
    """
    __tablename__ = "facilities"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    coordinates = Column(JSON)  # Stores lat/lng as JSON
    year_built = Column(Integer, nullable=False)
    size_sqft = Column(Integer, nullable=False)
    building_type = Column(String, nullable=False)
    environment = Column(JSON)  # Stores humidity, temperature, exposure as JSON
    
    # Relationship to equipment
    equipment = relationship("Equipment", back_populates="facility", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Facility {self.id}: {self.name}>" 