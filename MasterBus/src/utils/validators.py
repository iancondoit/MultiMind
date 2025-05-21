"""
Data validation utilities for MasterBus API.

Provides functions to validate incoming data from external systems.
"""
import logging
from typing import Any, Dict, List, Optional, Union, Tuple, cast
from pydantic import ValidationError

from src.models.facility import Facility
from src.models.equipment import Equipment
from src.utils.errors import ValidationException

logger = logging.getLogger(__name__)

def validate_facility_data(data: Dict[str, Any]) -> Tuple[Facility, List[str]]:
    """
    Validate facility data against the Facility model.
    
    Args:
        data: Dictionary containing facility data
        
    Returns:
        Tuple of (validated Facility object, list of warnings)
        
    Raises:
        ValidationException: If validation fails
    """
    warnings = []
    
    try:
        # Validate against model
        facility = Facility(**data)
        
        # Check for additional warning conditions
        if not facility.address:
            warnings.append("Facility is missing address information")
            
        if not facility.contact_info:
            warnings.append("Facility is missing contact information")
            
        # Warn about missing equipment data
        if not facility.equipment_count:
            warnings.append("Facility has no equipment records")
            
        return facility, warnings
        
    except ValidationError as e:
        # Convert validation error to our standard format
        details = {}
        for error in e.errors():
            loc = ".".join(str(item) for item in error.get("loc", []))
            if loc:
                details[loc] = error.get("msg", "Invalid value")
                
        raise ValidationException(
            message="Invalid facility data",
            details=details
        )


def validate_equipment_data(data: Dict[str, Any]) -> Tuple[Equipment, List[str]]:
    """
    Validate equipment data against the Equipment model.
    
    Args:
        data: Dictionary containing equipment data
        
    Returns:
        Tuple of (validated Equipment object, list of warnings)
        
    Raises:
        ValidationException: If validation fails
    """
    warnings = []
    
    try:
        # Validate against model
        equipment = Equipment(**data)
        
        # Check for additional warning conditions
        if not equipment.model:
            warnings.append("Equipment is missing model information")
            
        if not equipment.manufacturer:
            warnings.append("Equipment is missing manufacturer information")
            
        if not equipment.installation_date:
            warnings.append("Equipment is missing installation date")
        
        # Check for maintenance records
        if not equipment.last_maintenance_date:
            warnings.append("Equipment has no maintenance records")
            
        return equipment, warnings
        
    except ValidationError as e:
        # Convert validation error to our standard format
        details = {}
        for error in e.errors():
            loc = ".".join(str(item) for item in error.get("loc", []))
            if loc:
                details[loc] = error.get("msg", "Invalid value")
                
        raise ValidationException(
            message="Invalid equipment data",
            details=details
        ) 