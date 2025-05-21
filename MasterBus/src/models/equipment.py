#!/usr/bin/env python3
"""
Equipment models for the MasterBus API.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from src.models.base import BaseModelWithTimestamps
from src.models.risk import RiskAssessment
from src.models.compliance import Compliance


class EquipmentLocation(BaseModel):
    """Model representing an equipment's physical location within a facility."""
    
    facility_id: str = Field(
        ...,
        description="ID of the facility containing this equipment"
    )
    facility_name: str = Field(
        ...,
        description="Name of the facility containing this equipment"
    )
    building: Optional[str] = Field(
        None,
        description="Building within the facility"
    )
    room: Optional[str] = Field(
        None,
        description="Room or specific location within the building"
    )
    coordinates: Optional[Dict[str, float]] = Field(
        None,
        description="Precise geographic coordinates if available"
    )


class EquipmentSpecifications(BaseModel):
    """Model representing technical specifications for equipment."""
    
    voltage: Optional[str] = Field(
        None,
        description="Voltage rating (e.g., '208/120V')"
    )
    amperage: Optional[int] = Field(
        None,
        description="Current rating in amperes"
    )
    phases: Optional[int] = Field(
        None,
        description="Number of phases (1, 2, or 3)"
    )
    mount_type: Optional[str] = Field(
        None,
        description="Mounting type (e.g., 'surface', 'flush')"
    )
    enclosure_type: Optional[str] = Field(
        None,
        description="Enclosure type (e.g., 'NEMA 1', 'NEMA 3R')"
    )


class Photo(BaseModel):
    """Model representing a photo of equipment."""
    
    id: str = Field(
        ...,
        description="Unique identifier for the photo"
    )
    url: str = Field(
        ...,
        description="URL to access the full photo"
    )
    thumbnail_url: str = Field(
        ...,
        description="URL to access a thumbnail version of the photo"
    )
    caption: Optional[str] = Field(
        None,
        description="Caption or description of the photo"
    )
    taken_at: Optional[datetime] = Field(
        None,
        description="When the photo was taken"
    )


class Equipment(BaseModelWithTimestamps):
    """Model representing an electrical equipment item."""
    
    id: str = Field(
        ...,
        description="Unique identifier for the equipment"
    )
    name: str = Field(
        ...,
        description="Name or identifier of the equipment"
    )
    type: str = Field(
        ...,
        description="Type of equipment (panel, transformer, etc.)"
    )
    manufacturer: Optional[str] = Field(
        None,
        description="Equipment manufacturer"
    )
    model: Optional[str] = Field(
        None,
        description="Equipment model number or name"
    )
    serial_number: Optional[str] = Field(
        None,
        description="Serial number if available"
    )
    installation_date: Optional[datetime] = Field(
        None,
        description="When the equipment was installed"
    )
    location: EquipmentLocation = Field(
        ...,
        description="Physical location of the equipment"
    )
    specifications: Optional[EquipmentSpecifications] = Field(
        None,
        description="Technical specifications"
    )
    photos: List[Photo] = Field(
        default_factory=list,
        description="Photos of the equipment"
    )
    risk_assessment: Optional[RiskAssessment] = Field(
        None,
        description="Risk assessment information"
    )
    compliance: Optional[Compliance] = Field(
        None,
        description="Compliance information"
    ) 