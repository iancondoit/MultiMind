#!/usr/bin/env python3
"""
Risk assessment models for the MasterBus API.
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator

from src.models.base import BaseModelWithTimestamps


class RiskFactor(BaseModel):
    """Model representing a specific risk factor for equipment."""
    
    factor: str = Field(
        ...,
        description="The type of risk factor (e.g., age, maintenance, etc.)"
    )
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Risk score for this factor (0-100)"
    )
    description: str = Field(
        ...,
        description="Detailed description of the risk factor"
    )


class RiskAssessment(BaseModelWithTimestamps):
    """Model representing a risk assessment for equipment or a facility."""
    
    risk_level: Literal["Low", "Medium", "High", "Critical"] = Field(
        ...,
        description="Overall risk level classification"
    )
    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Overall risk score (0-100)"
    )
    condition: Optional[Literal["Excellent", "Good", "Fair", "Poor", "Critical"]] = Field(
        None,
        description="Physical condition assessment"
    )
    risk_factors: Optional[List[RiskFactor]] = Field(
        default_factory=list,
        description="Specific factors contributing to the risk score"
    )
    temperature: Optional[str] = Field(
        None,
        description="Temperature reading if available"
    )
    rust_level: Optional[Literal["None", "Minimal", "Moderate", "Severe"]] = Field(
        None,
        description="Level of rust observed"
    )
    corrosion_level: Optional[Literal["None", "Minimal", "Moderate", "Severe"]] = Field(
        None,
        description="Level of corrosion observed"
    )
    last_assessed: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="When the risk was last assessed"
    )
    
    @validator('risk_score')
    def validate_risk_score(cls, v):
        """Validate that risk score is within range."""
        if v < 0 or v > 100:
            raise ValueError('Risk score must be between 0 and 100')
        return v 