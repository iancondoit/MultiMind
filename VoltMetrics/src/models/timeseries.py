"""
TimeSeries models for VoltMetrics.

This module defines the SQLAlchemy models for time-series data including
historical risk scores and metrics.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from src.db.database import Base


class EquipmentRiskHistory(Base):
    """
    SQLAlchemy model for equipment risk score history.
    
    Stores historical risk scores for equipment to enable trend analysis.
    Compatible with TimescaleDB for time-series optimization.
    """
    __tablename__ = "equipment_risk_history"
    
    # Primary key is composite of equipment_id and timestamp
    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(String, ForeignKey("equipment.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Risk metrics
    overall_risk = Column(Float, nullable=False)
    risk_category = Column(String, nullable=False)
    
    # Individual risk factors
    age_risk = Column(Float)
    material_risk = Column(Float)
    maintenance_risk = Column(Float)
    environmental_risk = Column(Float)
    operational_risk = Column(Float)
    
    # Algorithm version used
    algorithm_version = Column(String)
    
    # Relationships
    equipment = relationship("Equipment")
    
    # Create indexes for time-series queries
    __table_args__ = (
        # Index for equipment_id + timestamp for efficient time-based queries
        Index("ix_equipment_risk_history_equipment_id_timestamp", "equipment_id", "timestamp"),
        
        # Index for timestamp for time-based aggregation queries
        Index("ix_equipment_risk_history_timestamp", "timestamp"),
    )
    
    def __repr__(self):
        return f"<EquipmentRiskHistory: {self.equipment_id} @ {self.timestamp} = {self.overall_risk}>"


class FacilityRiskHistory(Base):
    """
    SQLAlchemy model for facility risk score history.
    
    Stores historical risk scores for facilities to enable trend analysis.
    Compatible with TimescaleDB for time-series optimization.
    """
    __tablename__ = "facility_risk_history"
    
    # Primary key is composite of facility_id and timestamp
    id = Column(Integer, primary_key=True, autoincrement=True)
    facility_id = Column(String, ForeignKey("facilities.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Risk metrics
    overall_risk = Column(Float, nullable=False)
    risk_category = Column(String, nullable=False)
    
    # Equipment counts by risk level
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    
    # Compliance scores
    nfpa70b_score = Column(Float)
    nfpa70e_score = Column(Float)
    
    # Total equipment count
    equipment_count = Column(Integer)
    
    # Algorithm version used
    algorithm_version = Column(String)
    
    # Relationships
    facility = relationship("Facility")
    
    # Create indexes for time-series queries
    __table_args__ = (
        # Index for facility_id + timestamp for efficient time-based queries
        Index("ix_facility_risk_history_facility_id_timestamp", "facility_id", "timestamp"),
        
        # Index for timestamp for time-based aggregation queries
        Index("ix_facility_risk_history_timestamp", "timestamp"),
    )
    
    def __repr__(self):
        return f"<FacilityRiskHistory: {self.facility_id} @ {self.timestamp} = {self.overall_risk}>" 