#!/usr/bin/env python3
"""
Facility models for the MasterBus API.
"""
from typing import Dict, Optional, Literal
from pydantic import BaseModel, Field

from src.models.base import BaseModelWithTimestamps


class FacilityLocation(BaseModel):
    """Model representing a facility's physical location."""
    
    address: str = Field(
        ...,
        description="Physical address of the facility"
    )
    coordinates: Dict[str, float] = Field(
        ...,
        description="Geographic coordinates (latitude and longitude)"
    )


class RiskSummary(BaseModel):
    """Model representing a summary of risk for a facility."""
    
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall risk score for the facility (0-100)"
    )
    risk_level: Literal["Low", "Medium", "High", "Critical"] = Field(
        ...,
        description="Overall risk level classification"
    )
    high_risk_equipment_count: int = Field(
        0,
        ge=0,
        description="Number of equipment items with high risk"
    )
    medium_risk_equipment_count: int = Field(
        0,
        ge=0,
        description="Number of equipment items with medium risk"
    )
    low_risk_equipment_count: int = Field(
        0,
        ge=0,
        description="Number of equipment items with low risk"
    )
    critical_risk_equipment_count: int = Field(
        0,
        ge=0,
        description="Number of equipment items with critical risk"
    )


class Facility(BaseModelWithTimestamps):
    """Model representing a facility containing electrical equipment."""
    
    id: str = Field(
        ...,
        description="Unique identifier for the facility"
    )
    name: str = Field(
        ...,
        description="Name of the facility"
    )
    location: FacilityLocation = Field(
        ...,
        description="Physical location of the facility"
    )
    risk_summary: Optional[RiskSummary] = Field(
        None,
        description="Summary of risk factors for the facility"
    ) 