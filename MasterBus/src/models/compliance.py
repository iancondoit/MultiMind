#!/usr/bin/env python3
"""
Compliance models for the MasterBus API.
"""
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, validator

from src.models.base import BaseModelWithTimestamps


class NFPA70B(BaseModel):
    """Model representing NFPA 70B (maintenance) compliance."""
    
    compliant: bool = Field(
        ...,
        description="Whether the equipment is compliant with NFPA 70B standards"
    )
    compliance_percentage: int = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of compliance with NFPA 70B requirements"
    )
    next_inspection_due: Optional[datetime] = Field(
        None,
        description="When the next inspection is due"
    )
    maintenance_status: Literal["up_to_date", "due_soon", "overdue"] = Field(
        ...,
        description="Current maintenance status"
    )
    last_inspection: Optional[datetime] = Field(
        None,
        description="When the last inspection was performed"
    )
    
    @validator('compliance_percentage')
    def validate_compliance_percentage(cls, v):
        """Validate that compliance percentage is within range."""
        if v < 0 or v > 100:
            raise ValueError('Compliance percentage must be between 0 and 100')
        return v


class NFPA70E(BaseModel):
    """Model representing NFPA 70E (electrical safety) compliance."""
    
    compliant: bool = Field(
        ...,
        description="Whether the equipment is compliant with NFPA 70E standards"
    )
    compliance_percentage: int = Field(
        ...,
        ge=0,
        le=100,
        description="Percentage of compliance with NFPA 70E requirements"
    )
    arc_flash_label_present: bool = Field(
        ...,
        description="Whether an arc flash label is present"
    )
    ppe_requirements: Optional[str] = Field(
        None,
        description="Personal Protective Equipment requirements"
    )
    incident_energy: Optional[float] = Field(
        None,
        description="Incident energy at working distance (cal/cm²)"
    )
    last_assessment: Optional[datetime] = Field(
        None,
        description="When the last arc flash assessment was performed"
    )
    
    @validator('compliance_percentage')
    def validate_compliance_percentage(cls, v):
        """Validate that compliance percentage is within range."""
        if v < 0 or v > 100:
            raise ValueError('Compliance percentage must be between 0 and 100')
        return v


class Compliance(BaseModelWithTimestamps):
    """Model representing overall compliance for equipment or a facility."""
    
    nfpa_70b: NFPA70B = Field(
        ...,
        description="NFPA 70B (maintenance) compliance information"
    )
    nfpa_70e: NFPA70E = Field(
        ...,
        description="NFPA 70E (electrical safety) compliance information"
    )
    last_assessed: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="When compliance was last assessed"
    ) 