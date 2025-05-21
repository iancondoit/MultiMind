"""
Data access API endpoints for VoltMetrics.

This module defines FastAPI endpoints for accessing facility and equipment data.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.repositories.facility_repository import FacilityRepository
from src.db.repositories.equipment_repository import EquipmentRepository
from src.db.repositories.maintenance_repository import MaintenanceRepository
from src.models.equipment import EquipmentType

# Create router for data endpoints
router = APIRouter(
    prefix="/api/data",
    tags=["data"],
    responses={404: {"description": "Not found"}},
)


@router.get("/facilities")
def get_facilities(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get list of all facilities.
    
    Args:
        db: Database session
        
    Returns:
        List of facilities with basic information
    """
    facility_repo = FacilityRepository(db)
    facilities = facility_repo.get_all()
    
    return [
        {
            "id": facility.id,
            "name": facility.name,
            "location": facility.location,
            "building_type": facility.building_type,
            "year_built": facility.year_built,
            "size_sqft": facility.size_sqft
        }
        for facility in facilities
    ]


@router.get("/facility/{facility_id}")
def get_facility(facility_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get detailed information about a specific facility.
    
    Args:
        facility_id: ID of the facility to retrieve
        db: Database session
        
    Returns:
        Facility details
    """
    facility_repo = FacilityRepository(db)
    facility = facility_repo.get_with_equipment(facility_id)
    
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility not found with ID: {facility_id}")
    
    # Get equipment counts by type
    equipment_counts = {}
    for equipment in facility.equipment:
        equipment_type = equipment.type.value
        equipment_counts[equipment_type] = equipment_counts.get(equipment_type, 0) + 1
    
    return {
        "id": facility.id,
        "name": facility.name,
        "location": facility.location,
        "coordinates": facility.coordinates,
        "building_type": facility.building_type,
        "year_built": facility.year_built,
        "size_sqft": facility.size_sqft,
        "environment": facility.environment,
        "equipment_count": len(facility.equipment),
        "equipment_counts_by_type": equipment_counts
    }


@router.get("/facility/{facility_id}/equipment")
def get_facility_equipment(
    facility_id: str,
    equipment_type: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all equipment in a facility.
    
    Args:
        facility_id: ID of the facility
        equipment_type: Optional type filter
        db: Database session
        
    Returns:
        List of equipment items
    """
    facility_repo = FacilityRepository(db)
    equipment_repo = EquipmentRepository(db)
    
    # Check if facility exists
    facility = facility_repo.get_by_id(facility_id)
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility not found with ID: {facility_id}")
    
    # Get equipment
    equipment_list = equipment_repo.get_by_facility(facility_id)
    
    # Filter by type if specified
    if equipment_type:
        try:
            eq_type = EquipmentType[equipment_type.upper()]
            equipment_list = [eq for eq in equipment_list if eq.type == eq_type]
        except KeyError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid equipment type: {equipment_type}. Valid types are: "
                     f"{', '.join(t.name.lower() for t in EquipmentType)}"
            )
    
    # Convert to dict for response
    return [
        {
            "id": eq.id,
            "name": eq.name,
            "type": eq.type.value,
            "installation_date": eq.installation_date.isoformat(),
            "last_maintenance_date": eq.last_maintenance_date.isoformat() if eq.last_maintenance_date else None,
            "manufacturer": eq.manufacturer,
            "model": eq.model,
            "is_aluminum_conductor": eq.is_aluminum_conductor,
            "loading_percentage": eq.loading_percentage
        }
        for eq in equipment_list
    ]


@router.get("/equipment/{equipment_id}")
def get_equipment(equipment_id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Get detailed information about specific equipment.
    
    Args:
        equipment_id: ID of the equipment to retrieve
        db: Database session
        
    Returns:
        Equipment details
    """
    equipment_repo = EquipmentRepository(db)
    equipment = equipment_repo.get_with_maintenance(equipment_id)
    
    if not equipment:
        raise HTTPException(status_code=404, detail=f"Equipment not found with ID: {equipment_id}")
    
    # Format maintenance records
    maintenance_records = []
    for record in equipment.maintenance_records:
        maintenance_records.append({
            "id": record.id,
            "date": record.date.isoformat(),
            "type": record.type,
            "technician": record.technician,
            "findings": record.findings
        })
    
    # Sort by date (newest first)
    maintenance_records.sort(key=lambda x: x["date"], reverse=True)
    
    # Calculate age
    from datetime import datetime
    age_days = (datetime.now() - equipment.installation_date).days
    age_years = age_days / 365.25
    
    return {
        "id": equipment.id,
        "name": equipment.name,
        "type": equipment.type.value,
        "facility_id": equipment.facility_id,
        "installation_date": equipment.installation_date.isoformat(),
        "age_years": round(age_years, 1),
        "location": equipment.location,
        "manufacturer": equipment.manufacturer,
        "model": equipment.model,
        "is_aluminum_conductor": equipment.is_aluminum_conductor,
        "humidity_exposure": equipment.humidity_exposure,
        "temperature_exposure": equipment.temperature_exposure,
        "loading_percentage": equipment.loading_percentage,
        "last_maintenance_date": equipment.last_maintenance_date.isoformat() if equipment.last_maintenance_date else None,
        "additional_data": equipment.additional_data,
        "maintenance_records": maintenance_records
    }


@router.get("/equipment/{equipment_id}/maintenance")
def get_equipment_maintenance(
    equipment_id: str, 
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get maintenance records for specific equipment.
    
    Args:
        equipment_id: ID of the equipment
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of maintenance records
    """
    equipment_repo = EquipmentRepository(db)
    maintenance_repo = MaintenanceRepository(db)
    
    # Check if equipment exists
    equipment = equipment_repo.get_by_id(equipment_id)
    if not equipment:
        raise HTTPException(status_code=404, detail=f"Equipment not found with ID: {equipment_id}")
    
    # Get maintenance records
    records = maintenance_repo.get_by_equipment_sorted(equipment_id, limit)
    
    # Convert to dict for response
    return [
        {
            "id": record.id,
            "equipment_id": record.equipment_id,
            "date": record.date.isoformat(),
            "type": record.type,
            "technician": record.technician,
            "findings": record.findings
        }
        for record in records
    ] 