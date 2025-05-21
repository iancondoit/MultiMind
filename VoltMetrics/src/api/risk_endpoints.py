"""
Risk assessment API endpoints for VoltMetrics.

This module defines FastAPI endpoints for accessing risk assessment data.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session

from src.db.database import get_db
from src.core.risk_service import RiskService
from src.models.equipment import EquipmentType

# Create router for risk endpoints
router = APIRouter(
    prefix="/api/risk",
    tags=["risk"],
    responses={404: {"description": "Not found"}},
)


@router.get("/equipment/{equipment_id}")
def get_equipment_risk(
    equipment_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get risk assessment for a specific equipment item.
    
    Args:
        equipment_id: ID of the equipment to evaluate
        db: Database session
        
    Returns:
        Risk assessment data
    """
    try:
        risk_service = RiskService(db)
        return risk_service.get_equipment_risk(equipment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/facility/{facility_id}")
def get_facility_risk(
    facility_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive risk assessment for an entire facility.
    
    Args:
        facility_id: ID of the facility to evaluate
        db: Database session
        
    Returns:
        Facility risk assessment data
    """
    try:
        risk_service = RiskService(db)
        return risk_service.get_facility_risk_assessment(facility_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/high-risk")
def get_high_risk_equipment(
    min_risk: float = Query(75.0, description="Minimum risk score threshold"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get all high-risk equipment across all facilities.
    
    Args:
        min_risk: Minimum risk score to include (default: 75.0)
        db: Database session
        
    Returns:
        List of high-risk equipment assessments
    """
    risk_service = RiskService(db)
    return risk_service.get_high_risk_equipment(min_risk)


@router.get("/maintenance-needed")
def get_equipment_needing_maintenance(
    months: int = Query(36, description="Months since last maintenance"),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get equipment that hasn't had maintenance in the specified period.
    
    Args:
        months: Number of months to check
        db: Database session
        
    Returns:
        List of equipment assessments
    """
    risk_service = RiskService(db)
    return risk_service.get_equipment_without_maintenance(months)


@router.get("/equipment-type/{type}")
def get_equipment_by_type(
    type: str,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get risk assessments for all equipment of a specific type.
    
    Args:
        type: Type of equipment (panel, transformer, switchgear, breaker, other)
        db: Database session
        
    Returns:
        List of risk assessments
    """
    try:
        # Convert string to enum
        try:
            equipment_type = EquipmentType[type.upper()]
        except KeyError:
            raise ValueError(f"Invalid equipment type: {type}. Valid types are: "
                           f"{', '.join(t.name.lower() for t in EquipmentType)}")
        
        risk_service = RiskService(db)
        return risk_service.get_equipment_by_type_risks(equipment_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/facility-summary")
def get_facility_risk_summary(
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    Get summary of risk assessments by facility.
    
    Args:
        db: Database session
        
    Returns:
        List of facility risk summaries
    """
    risk_service = RiskService(db)
    return risk_service.get_risk_summary_by_facility() 