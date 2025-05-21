"""
Equipment model for VoltMetrics.

This module defines the SQLAlchemy model for electrical equipment.
"""

import enum
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from src.db.database import Base


class EquipmentType(enum.Enum):
    """
    Enumeration of equipment types supported in the system.
    """
    PANEL = "PANEL"
    TRANSFORMER = "TRANSFORMER"
    SWITCHGEAR = "SWITCHGEAR"
    BREAKER = "BREAKER"
    OTHER = "OTHER"


class Equipment(Base):
    """
    SQLAlchemy model for electrical equipment.
    
    Represents a piece of electrical equipment that will be analyzed for risk.
    """
    __tablename__ = "equipment"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(Enum(EquipmentType), nullable=False)
    facility_id = Column(String, ForeignKey("facilities.id"), nullable=False)
    installation_date = Column(DateTime, nullable=False)
    location = Column(String, nullable=False)
    manufacturer = Column(String, nullable=False)
    model = Column(String, nullable=False)
    is_aluminum_conductor = Column(Boolean, default=False)
    humidity_exposure = Column(Float)
    temperature_exposure = Column(Float)
    loading_percentage = Column(Integer)
    last_maintenance_date = Column(DateTime, nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # Relationships
    facility = relationship("Facility", back_populates="equipment")
    maintenance_records = relationship("MaintenanceRecord", back_populates="equipment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Equipment {self.id}: {self.type.value} in {self.facility_id}>" 