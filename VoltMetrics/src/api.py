"""
API endpoints for VoltMetrics.

This module provides a simple API for data ingestion and risk assessment
using FastAPI.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Body, Depends, Query
from pydantic import BaseModel, Field

from models.equipment import Equipment, EquipmentType
from models.facility import Facility
from models.maintenance import MaintenanceRecord
from utils.risk_calculator import RiskCalculator
from core.compliance.nfpa70b import NFPA70BEvaluator
from core.compliance.nfpa70e import NFPA70EEvaluator
from core.aggregation.facility_aggregator import FacilityAggregator
from core.forecasting import RiskForecaster


# Pydantic models for request validation
class EquipmentData(BaseModel):
    """Data model for equipment API requests."""
    
    id: str
    name: str
    type: str
    installation_date: str
    location: str
    manufacturer: str
    model: str
    is_aluminum_conductor: bool
    humidity_exposure: float
    temperature_exposure: float
    loading_percentage: float
    last_maintenance_date: Optional[str] = None
    notes: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class FacilityData(BaseModel):
    """Data model for facility API requests."""
    
    id: str
    name: str
    address: str
    building_type: str
    square_footage: int
    year_built: int
    notes: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


# Initialize FastAPI app
app = FastAPI(
    title="VoltMetrics API",
    description="API for electrical equipment risk assessment",
    version="0.2.0",  # Updated version for Phase 3
)

# Initialize core services
risk_calculator = RiskCalculator()
nfpa70b_evaluator = NFPA70BEvaluator()
nfpa70e_evaluator = NFPA70EEvaluator()
facility_aggregator = FacilityAggregator()
risk_forecaster = RiskForecaster()

# In-memory storage for demo purposes
# In a real implementation, this would be replaced with a database
equipment_store = {}
facility_store = {}
maintenance_store = {}  # Map equipment_id to list of maintenance records
risk_history_store = {}  # Map equipment_id or facility_id to list of historical assessments


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "VoltMetrics API",
        "version": "0.2.0",  # Updated version for Phase 3
        "description": "Electrical equipment risk assessment API with compliance evaluation and forecasting"
    }


@app.post("/equipment")
async def create_equipment(equipment_data: EquipmentData):
    """
    Create a new equipment record.
    
    Args:
        equipment_data: Equipment data from request body
        
    Returns:
        Dictionary with created equipment information
    """
    # Convert string dates to datetime objects
    try:
        installation_date = datetime.fromisoformat(equipment_data.installation_date)
        
        last_maintenance_date = None
        if equipment_data.last_maintenance_date:
            last_maintenance_date = datetime.fromisoformat(equipment_data.last_maintenance_date)
            
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
    
    # Convert string type to EquipmentType enum
    try:
        equipment_type = EquipmentType(equipment_data.type)
    except ValueError:
        valid_types = [t.value for t in EquipmentType]
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid equipment type. Valid types are: {valid_types}"
        )
    
    # Create Equipment object
    equipment = Equipment(
        id=equipment_data.id,
        name=equipment_data.name,
        type=equipment_type,
        installation_date=installation_date,
        last_maintenance_date=last_maintenance_date,
        location=equipment_data.location,
        manufacturer=equipment_data.manufacturer,
        model=equipment_data.model,
        is_aluminum_conductor=equipment_data.is_aluminum_conductor,
        humidity_exposure=equipment_data.humidity_exposure,
        temperature_exposure=equipment_data.temperature_exposure,
        loading_percentage=equipment_data.loading_percentage,
        notes=equipment_data.notes,
        additional_data=equipment_data.additional_data
    )
    
    # Store equipment in memory
    equipment_store[equipment.id] = equipment
    
    # Calculate risk for this equipment
    risk_score = risk_calculator.calculate_equipment_risk(equipment)
    risk_level = risk_calculator.get_risk_level(risk_score)
    
    # Return equipment data with risk assessment
    response = equipment.to_dict()
    response.update({
        "risk_score": risk_score,
        "risk_level": risk_level
    })
    
    return response


@app.get("/equipment/{equipment_id}")
async def get_equipment(equipment_id: str):
    """
    Get equipment by ID.
    
    Args:
        equipment_id: ID of equipment to retrieve
        
    Returns:
        Equipment data with risk assessment
    """
    if equipment_id not in equipment_store:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    equipment = equipment_store[equipment_id]
    
    # Calculate risk
    risk_score = risk_calculator.calculate_equipment_risk(equipment)
    risk_level = risk_calculator.get_risk_level(risk_score)
    
    # Return equipment data with risk assessment
    response = equipment.to_dict()
    response.update({
        "risk_score": risk_score,
        "risk_level": risk_level
    })
    
    return response


@app.post("/facility")
async def create_facility(facility_data: FacilityData):
    """
    Create a new facility record.
    
    Args:
        facility_data: Facility data from request body
        
    Returns:
        Dictionary with created facility information
    """
    # Create Facility object
    facility = Facility(
        id=facility_data.id,
        name=facility_data.name,
        address=facility_data.address,
        building_type=facility_data.building_type,
        square_footage=facility_data.square_footage,
        year_built=facility_data.year_built,
        equipment=[],  # Start with empty equipment list
        notes=facility_data.notes,
        additional_data=facility_data.additional_data
    )
    
    # Store facility in memory
    facility_store[facility.id] = facility
    
    return facility.to_dict()


@app.post("/facility/{facility_id}/equipment/{equipment_id}")
async def add_equipment_to_facility(facility_id: str, equipment_id: str):
    """
    Add equipment to a facility.
    
    Args:
        facility_id: ID of facility
        equipment_id: ID of equipment
        
    Returns:
        Updated facility data
    """
    if facility_id not in facility_store:
        raise HTTPException(status_code=404, detail="Facility not found")
        
    if equipment_id not in equipment_store:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    facility = facility_store[facility_id]
    equipment = equipment_store[equipment_id]
    
    # Add equipment to facility
    facility.add_equipment(equipment)
    
    return facility.to_dict()


@app.get("/facility/{facility_id}")
async def get_facility(facility_id: str):
    """
    Get facility by ID.
    
    Args:
        facility_id: ID of facility to retrieve
        
    Returns:
        Facility data
    """
    if facility_id not in facility_store:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    facility = facility_store[facility_id]
    return facility.to_dict()


@app.get("/facility/{facility_id}/risk")
async def assess_facility_risk(facility_id: str):
    """
    Assess risk for a facility.
    
    Args:
        facility_id: ID of facility to assess
        
    Returns:
        Risk assessment results
    """
    if facility_id not in facility_store:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    facility = facility_store[facility_id]
    
    # Calculate facility risk
    facility_risk = risk_calculator.calculate_facility_risk(facility)
    
    return facility_risk


@app.get("/api/v1/equipment/{equipment_id}/risk")
async def get_equipment_risk(equipment_id: str):
    """
    Get risk assessment for a specific equipment item.
    
    Args:
        equipment_id: ID of equipment to assess
        
    Returns:
        Equipment risk assessment
    """
    if equipment_id not in equipment_store:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    equipment = equipment_store[equipment_id]
    
    # Calculate risk
    risk_assessment = risk_calculator.calculate_risk(equipment)
    
    # Store risk assessment in history
    if equipment_id not in risk_history_store:
        risk_history_store[equipment_id] = []
    
    risk_history_store[equipment_id].append(risk_assessment)
    
    return risk_assessment


@app.get("/api/v1/facilities/{facility_id}/risk")
async def get_facility_risk(facility_id: str):
    """
    Get aggregated risk assessment for a facility.
    
    Args:
        facility_id: ID of facility to assess
        
    Returns:
        Facility-level risk assessment
    """
    if facility_id not in facility_store:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    facility = facility_store[facility_id]
    
    # Get equipment for this facility
    facility_equipment = []
    for equipment_id, equipment in equipment_store.items():
        if equipment.facility_id == facility_id:
            facility_equipment.append(equipment)
    
    # Use facility aggregator to calculate risk
    risk_assessment = facility_aggregator.aggregate_facility_risk(
        facility, facility_equipment
    )
    
    # Store risk assessment in history
    facility_history_key = f"facility_{facility_id}"
    if facility_history_key not in risk_history_store:
        risk_history_store[facility_history_key] = []
    
    risk_history_store[facility_history_key].append(risk_assessment)
    
    return risk_assessment


@app.get("/api/v1/compliance/nfpa70b/{equipment_id}")
async def get_equipment_nfpa70b_compliance(equipment_id: str):
    """
    Get NFPA 70B compliance evaluation for a specific equipment item.
    
    Args:
        equipment_id: ID of equipment to evaluate
        
    Returns:
        NFPA 70B compliance evaluation
    """
    if equipment_id not in equipment_store:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    equipment = equipment_store[equipment_id]
    
    # Get maintenance records for this equipment
    maintenance_records = maintenance_store.get(equipment_id, [])
    
    # Evaluate NFPA 70B compliance
    compliance_evaluation = nfpa70b_evaluator.evaluate_equipment(
        equipment, maintenance_records
    )
    
    return compliance_evaluation


@app.get("/api/v1/compliance/nfpa70e/{equipment_id}")
async def get_equipment_nfpa70e_compliance(equipment_id: str):
    """
    Get NFPA 70E compliance evaluation for a specific equipment item.
    
    Args:
        equipment_id: ID of equipment to evaluate
        
    Returns:
        NFPA 70E compliance evaluation
    """
    if equipment_id not in equipment_store:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    equipment = equipment_store[equipment_id]
    
    # Evaluate NFPA 70E compliance
    compliance_evaluation = nfpa70e_evaluator.evaluate_equipment(equipment)
    
    return compliance_evaluation


@app.get("/api/v1/compliance/nfpa70b/facilities/{facility_id}")
async def get_facility_nfpa70b_compliance(facility_id: str):
    """
    Get NFPA 70B compliance evaluation for a facility.
    
    Args:
        facility_id: ID of facility to evaluate
        
    Returns:
        Facility-level NFPA 70B compliance evaluation
    """
    if facility_id not in facility_store:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    facility = facility_store[facility_id]
    
    # Get equipment for this facility
    facility_equipment = []
    for equipment_id, equipment in equipment_store.items():
        if equipment.facility_id == facility_id:
            facility_equipment.append(equipment)
    
    # Get maintenance records for facility equipment
    maintenance_records = {}
    for equipment in facility_equipment:
        maintenance_records[equipment.id] = maintenance_store.get(equipment.id, [])
    
    # Evaluate NFPA 70B compliance for facility
    compliance_evaluation = nfpa70b_evaluator.evaluate_facility(
        facility, facility_equipment, maintenance_records
    )
    
    return compliance_evaluation


@app.get("/api/v1/compliance/nfpa70e/facilities/{facility_id}")
async def get_facility_nfpa70e_compliance(facility_id: str):
    """
    Get NFPA 70E compliance evaluation for a facility.
    
    Args:
        facility_id: ID of facility to evaluate
        
    Returns:
        Facility-level NFPA 70E compliance evaluation
    """
    if facility_id not in facility_store:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    facility = facility_store[facility_id]
    
    # Get equipment for this facility
    facility_equipment = []
    for equipment_id, equipment in equipment_store.items():
        if equipment.facility_id == facility_id:
            facility_equipment.append(equipment)
    
    # Evaluate NFPA 70E compliance for facility
    compliance_evaluation = nfpa70e_evaluator.evaluate_facility(
        facility, facility_equipment
    )
    
    return compliance_evaluation


@app.get("/api/v1/facilities/{facility_id}/report")
async def get_facility_comprehensive_report(facility_id: str):
    """
    Get comprehensive report for a facility including risk, compliance, and forecasting.
    
    Args:
        facility_id: ID of facility to report on
        
    Returns:
        Comprehensive facility report
    """
    if facility_id not in facility_store:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    facility = facility_store[facility_id]
    
    # Get equipment for this facility
    facility_equipment = []
    for equipment_id, equipment in equipment_store.items():
        if equipment.facility_id == facility_id:
            facility_equipment.append(equipment)
    
    # Get maintenance records for facility equipment
    maintenance_records = {}
    for equipment in facility_equipment:
        maintenance_records[equipment.id] = maintenance_store.get(equipment.id, [])
    
    # Get historical data for facility
    facility_history_key = f"facility_{facility_id}"
    historical_data = risk_history_store.get(facility_history_key, [])
    
    # Generate comprehensive report
    report = facility_aggregator.generate_comprehensive_report(
        facility, facility_equipment, maintenance_records, historical_data
    )
    
    return report


@app.get("/api/v1/equipment/{equipment_id}/forecast")
async def get_equipment_risk_forecast(
    equipment_id: str,
    forecast_periods: int = Query(6, ge=1, le=24, description="Number of periods to forecast"),
    period_months: int = Query(1, ge=1, le=12, description="Number of months per period")
):
    """
    Get risk forecast for a specific equipment item.
    
    Args:
        equipment_id: ID of equipment to forecast
        forecast_periods: Number of periods to forecast
        period_months: Number of months per period
        
    Returns:
        Equipment risk forecast
    """
    if equipment_id not in equipment_store:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    equipment = equipment_store[equipment_id]
    
    # Get historical data for equipment
    historical_data = risk_history_store.get(equipment_id, [])
    
    if len(historical_data) < 3:
        return {
            "equipment_id": equipment_id,
            "error": "Insufficient historical data for forecasting",
            "minimum_history_required": 3,
            "history_available": len(historical_data)
        }
    
    # Generate risk forecast
    forecast = risk_forecaster.forecast_equipment_risk(
        equipment, historical_data, forecast_periods, period_months
    )
    
    return forecast


@app.get("/api/v1/facilities/{facility_id}/forecast")
async def get_facility_risk_forecast(
    facility_id: str,
    forecast_periods: int = Query(6, ge=1, le=24, description="Number of periods to forecast"),
    period_months: int = Query(1, ge=1, le=12, description="Number of months per period")
):
    """
    Get risk forecast for a facility.
    
    Args:
        facility_id: ID of facility to forecast
        forecast_periods: Number of periods to forecast
        period_months: Number of months per period
        
    Returns:
        Facility risk forecast
    """
    if facility_id not in facility_store:
        raise HTTPException(status_code=404, detail="Facility not found")
    
    facility = facility_store[facility_id]
    
    # Get historical data for facility
    facility_history_key = f"facility_{facility_id}"
    historical_data = risk_history_store.get(facility_history_key, [])
    
    if len(historical_data) < 3:
        return {
            "facility_id": facility_id,
            "error": "Insufficient historical data for forecasting",
            "minimum_history_required": 3,
            "history_available": len(historical_data)
        }
    
    # Get equipment for this facility
    facility_equipment = []
    for equipment_id, equipment in equipment_store.items():
        if equipment.facility_id == facility_id:
            facility_equipment.append(equipment)
    
    # Generate equipment forecasts for blending
    equipment_forecasts = []
    for equipment in facility_equipment:
        equip_history = risk_history_store.get(equipment.id, [])
        if len(equip_history) >= 3:  # Only forecast if we have enough history
            equip_forecast = risk_forecaster.forecast_equipment_risk(
                equipment, equip_history, forecast_periods, period_months
            )
            equipment_forecasts.append(equip_forecast)
    
    # Generate facility risk forecast
    forecast = risk_forecaster.forecast_facility_risk(
        facility, historical_data, equipment_forecasts, forecast_periods, period_months
    )
    
    return forecast


@app.post("/api/v1/maintenance/{equipment_id}")
async def add_maintenance_record(equipment_id: str, maintenance_data: Dict[str, Any]):
    """
    Add a maintenance record for equipment.
    
    Args:
        equipment_id: ID of equipment
        maintenance_data: Maintenance record data
        
    Returns:
        Added maintenance record
    """
    if equipment_id not in equipment_store:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Create a maintenance record
    try:
        maintenance_date = datetime.fromisoformat(maintenance_data.get("date", datetime.now().isoformat()))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
    
    maintenance_record = MaintenanceRecord(
        id=f"{equipment_id}-{len(maintenance_store.get(equipment_id, []))+1}",
        equipment_id=equipment_id,
        date=maintenance_date,
        maintenance_type=maintenance_data.get("type", "general"),
        description=maintenance_data.get("description", ""),
        performed_by=maintenance_data.get("performed_by", ""),
        findings=maintenance_data.get("findings", ""),
        additional_data=maintenance_data.get("additional_data", {})
    )
    
    # Store maintenance record
    if equipment_id not in maintenance_store:
        maintenance_store[equipment_id] = []
    
    maintenance_store[equipment_id].append(maintenance_record)
    
    return maintenance_record.to_dict()


@app.get("/api/v1/equipment/{equipment_id}/maintenance_forecast")
async def get_equipment_maintenance_forecast(equipment_id: str):
    """
    Get maintenance forecast for a specific equipment item.
    
    Args:
        equipment_id: ID of equipment to forecast maintenance for
        
    Returns:
        Equipment maintenance forecast
    """
    if equipment_id not in equipment_store:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    equipment = equipment_store[equipment_id]
    
    # Get historical data for equipment
    historical_data = risk_history_store.get(equipment_id, [])
    
    if len(historical_data) < 3:
        return {
            "equipment_id": equipment_id,
            "error": "Insufficient historical data for forecasting",
            "minimum_history_required": 3,
            "history_available": len(historical_data)
        }
    
    # Generate risk forecast first
    risk_forecast = risk_forecaster.forecast_equipment_risk(
        equipment, historical_data
    )
    
    # Then forecast maintenance needs based on risk forecast
    maintenance_forecast = risk_forecaster.forecast_maintenance_needs(
        equipment, historical_data, risk_forecast
    )
    
    return maintenance_forecast


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 