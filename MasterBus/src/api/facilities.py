#!/usr/bin/env python3
"""
Facility endpoints for MasterBus API.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Dict, List, Optional, Any
import logging

from src.api.base import get_current_user
from src.models.facility import Facility, FacilityLocation, RiskSummary
from src.utils.data_transport import FacilityDataTransport
from src.utils.errors import NotFoundException


# Create router for facility endpoints
router = APIRouter(prefix="/facilities", tags=["Facilities"])
logger = logging.getLogger(__name__)

# Initialize the data transport service
facility_transport = FacilityDataTransport()


@router.get("/", response_model=Dict[str, Any])
async def get_facilities(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: Optional[str] = Query(None, description="Sort field"),
    order: Optional[str] = Query(None, description="Sort order (asc, desc)"),
    search: Optional[str] = Query(None, description="Search term"),
    force_refresh: bool = Query(False, description="Force refresh from source"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve a list of facilities with risk summary information.
    
    This endpoint returns facilities with their risk assessment
    and compliance metrics for display in ThreatMap.
    """
    # TODO: Implement facility listing with database query
    # For Phase 3, we'll return a mock list but with enhanced processing
    
    # In a real implementation, this would:
    # 1. Query database for facilities matching filters
    # 2. Process each facility using the transport service
    # 3. Apply pagination, sorting, etc.
    
    # Mock facility IDs for now
    facility_ids = ["facility-123", "facility-456"]
    processed_facilities = []
    
    # Process each facility
    for facility_id in facility_ids:
        try:
            facility_data = await facility_transport.process_facility(
                facility_id=facility_id,
                force_refresh=force_refresh
            )
            processed_facilities.append(facility_data)
        except NotFoundException:
            logger.warning(f"Facility {facility_id} not found")
            continue
        except Exception as e:
            logger.error(f"Error processing facility {facility_id}: {str(e)}")
            continue
    
    # Calculate pagination info
    total = len(processed_facilities)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paged_facilities = processed_facilities[start_idx:end_idx]
    
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "facilities": paged_facilities
    }


@router.get("/{facility_id}", response_model=Dict[str, Any])
async def get_facility(
    facility_id: str = Path(..., description="Facility ID"),
    force_refresh: bool = Query(False, description="Force refresh from source"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific facility.
    
    This endpoint returns comprehensive facility data including
    risk assessment and compliance metrics for display in ThreatMap.
    """
    try:
        return await facility_transport.process_facility(
            facility_id=facility_id,
            force_refresh=force_refresh
        )
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=f"Facility {facility_id} not found")


@router.get("/{facility_id}/equipment", response_model=Dict[str, Any])
async def get_facility_equipment(
    facility_id: str = Path(..., description="Facility ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: Optional[str] = Query(None, description="Sort field"),
    order: Optional[str] = Query(None, description="Sort order (asc, desc)"),
    search: Optional[str] = Query(None, description="Search term"),
    force_refresh: bool = Query(False, description="Force refresh from source"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve equipment within a specific facility.
    
    This endpoint returns equipment data with risk assessments
    for all equipment in the specified facility.
    """
    # TODO: Implement equipment listing with database query
    # For Phase 3, we'll return a mock list
    
    # Mock equipment IDs for this facility
    # In a real implementation, this would query a database
    equipment_ids = [f"{facility_id}-equip-{i}" for i in range(1, 6)]
    processed_equipment = []
    
    # Process each piece of equipment
    for equipment_id in equipment_ids:
        try:
            equipment_data = await facility_transport.process_equipment(
                equipment_id=equipment_id,
                force_refresh=force_refresh
            )
            processed_equipment.append(equipment_data)
        except NotFoundException:
            logger.warning(f"Equipment {equipment_id} not found")
            continue
        except Exception as e:
            logger.error(f"Error processing equipment {equipment_id}: {str(e)}")
            continue
    
    # Calculate pagination info
    total = len(processed_equipment)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paged_equipment = processed_equipment[start_idx:end_idx]
    
    return {
        "facility_id": facility_id,
        "total": total,
        "page": page,
        "limit": limit,
        "equipment": paged_equipment
    }


@router.get("/{facility_id}/equipment/{equipment_id}", response_model=Dict[str, Any])
async def get_facility_equipment_item(
    facility_id: str = Path(..., description="Facility ID"),
    equipment_id: str = Path(..., description="Equipment ID"),
    force_refresh: bool = Query(False, description="Force refresh from source"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Retrieve detailed information about a specific equipment item.
    
    This endpoint returns comprehensive equipment data including
    risk assessment for display in ThreatMap.
    """
    try:
        equipment_data = await facility_transport.process_equipment(
            equipment_id=equipment_id,
            force_refresh=force_refresh
        )
        
        # Verify this equipment belongs to the facility
        if equipment_data.get("facility_id") != facility_id:
            raise HTTPException(
                status_code=404,
                detail=f"Equipment {equipment_id} not found in facility {facility_id}"
            )
            
        return equipment_data
    except NotFoundException:
        raise HTTPException(
            status_code=404,
            detail=f"Equipment {equipment_id} not found"
        ) 