"""
Maintenance record model for VoltMetrics.

This module defines the SQLAlchemy model for maintenance records.
"""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.db.database import Base


class MaintenanceRecord(Base):
    """
    SQLAlchemy model for equipment maintenance records.
    
    Represents a maintenance activity performed on a piece of equipment.
    """
    __tablename__ = "maintenance_records"
    
    id = Column(String, primary_key=True)
    equipment_id = Column(String, ForeignKey("equipment.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    type = Column(String, nullable=False)  # Type of maintenance (Routine, Repair, etc.)
    technician = Column(String, nullable=False)
    findings = Column(Text, nullable=True)
    
    # Relationships
    equipment = relationship("Equipment", back_populates="maintenance_records")
    
    def __repr__(self):
        return f"<MaintenanceRecord {self.id}: {self.type} on {self.equipment_id}>" 