"""
Risk service for VoltMetrics.

This service coordinates between the database repositories
and the risk calculation algorithms to provide risk assessments.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from src.db.repositories.equipment_repository import EquipmentRepository
from src.db.repositories.facility_repository import FacilityRepository
from src.core.risk_calculator import RiskCalculator, RiskCategory
from src.models.equipment import Equipment, EquipmentType
from src.models.facility import Facility


class RiskService:
    """
    Service for calculating and managing equipment risk assessments.
    
    This service acts as a coordinator between database access and risk calculation,
    providing higher-level functionality for the API layer.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the risk service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.equipment_repo = EquipmentRepository(db_session)
        self.facility_repo = FacilityRepository(db_session)
        self.calculator = RiskCalculator()
    
    def get_equipment_risk(self, equipment_id: str) -> Dict[str, Any]:
        """
        Calculate risk for a specific equipment item.
        
        Args:
            equipment_id: ID of the equipment to evaluate
            
        Returns:
            Risk assessment dictionary
            
        Raises:
            ValueError: If equipment is not found
        """
        equipment = self.equipment_repo.get_by_id(equipment_id)
        if not equipment:
            raise ValueError(f"Equipment not found with ID: {equipment_id}")
        
        return self.calculator.calculate_risk(equipment)
    
    def get_facility_risk_assessment(self, facility_id: str) -> Dict[str, Any]:
        """
        Calculate risk assessment for an entire facility.
        
        Args:
            facility_id: ID of the facility to evaluate
            
        Returns:
            Risk assessment dictionary with overall facility risk and equipment breakdown
            
        Raises:
            ValueError: If facility is not found
        """
        facility = self.facility_repo.get_with_equipment(facility_id)
        if not facility:
            raise ValueError(f"Facility not found with ID: {facility_id}")
        
        # Calculate risk for each equipment item
        equipment_risks = self.calculator.bulk_calculate_risks(facility.equipment)
        
        # Calculate overall facility risk
        if not equipment_risks:
            return {
                "facility_id": facility_id,
                "name": facility.name,
                "risk_score": 0,
                "risk_category": RiskCategory.LOW,
                "equipment_count": 0,
                "risk_distribution": {
                    RiskCategory.LOW: 0,
                    RiskCategory.MEDIUM: 0,
                    RiskCategory.HIGH: 0,
                    RiskCategory.CRITICAL: 0
                },
                "equipment_risks": [],
                "assessment_date": datetime.now().isoformat()
            }
        
        # Calculate risk distribution
        risk_distribution = self.calculator.get_risk_distribution(equipment_risks)
        
        # Calculate weighted average risk score
        total_risk = sum(assessment["overall_risk"] for assessment in equipment_risks)
        avg_risk = total_risk / len(equipment_risks)
        
        # Get the highest risk category present
        highest_category = RiskCategory.LOW
        for category in [RiskCategory.CRITICAL, RiskCategory.HIGH, RiskCategory.MEDIUM]:
            if risk_distribution[category] > 0:
                highest_category = category
                break
        
        # Compile facility risk assessment
        return {
            "facility_id": facility_id,
            "name": facility.name,
            "risk_score": round(avg_risk, 1),
            "risk_category": highest_category,
            "equipment_count": len(equipment_risks),
            "risk_distribution": risk_distribution,
            "equipment_risks": sorted(
                equipment_risks, 
                key=lambda x: x["overall_risk"], 
                reverse=True
            ),
            "assessment_date": datetime.now().isoformat()
        }
    
    def get_high_risk_equipment(self, min_risk_score: float = 75.0) -> List[Dict[str, Any]]:
        """
        Get all high-risk equipment across all facilities.
        
        Args:
            min_risk_score: Minimum risk score to include (default: 75.0)
            
        Returns:
            List of risk assessments for high-risk equipment
        """
        # Get all equipment
        all_equipment = self.equipment_repo.get_all()
        
        # Calculate risk for all equipment
        all_risks = self.calculator.bulk_calculate_risks(all_equipment)
        
        # Filter to high-risk items
        high_risk = [
            assessment for assessment in all_risks
            if assessment["overall_risk"] >= min_risk_score
        ]
        
        # Sort by risk score (highest first)
        return sorted(high_risk, key=lambda x: x["overall_risk"], reverse=True)
    
    def get_equipment_without_maintenance(self, months: int = 36) -> List[Dict[str, Any]]:
        """
        Get equipment that hasn't had maintenance in the specified period.
        
        Args:
            months: Number of months to check
            
        Returns:
            List of equipment with risk assessments
        """
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        # Get equipment without maintenance since the cutoff
        equipment_list = self.equipment_repo.get_without_maintenance_since(cutoff_date)
        
        # Calculate risk for these items
        risks = self.calculator.bulk_calculate_risks(equipment_list)
        
        # Add facility information
        for risk in risks:
            equipment_id = risk["equipment_id"]
            equipment = next((e for e in equipment_list if e.id == equipment_id), None)
            if equipment:
                facility = self.facility_repo.get_by_id(equipment.facility_id)
                risk["facility_name"] = facility.name if facility else "Unknown Facility"
                risk["facility_id"] = equipment.facility_id
        
        # Sort by risk score (highest first)
        return sorted(risks, key=lambda x: x["overall_risk"], reverse=True)
    
    def get_equipment_by_type_risks(self, equipment_type: EquipmentType) -> List[Dict[str, Any]]:
        """
        Get risk assessments for all equipment of a specific type.
        
        Args:
            equipment_type: Type of equipment to evaluate
            
        Returns:
            List of risk assessments
        """
        # Get equipment by type
        equipment_list = self.equipment_repo.get_by_type(equipment_type)
        
        # Calculate risks
        risks = self.calculator.bulk_calculate_risks(equipment_list)
        
        # Sort by risk score (highest first)
        return sorted(risks, key=lambda x: x["overall_risk"], reverse=True)
    
    def get_risk_summary_by_facility(self) -> List[Dict[str, Any]]:
        """
        Get a summary of risk assessments by facility.
        
        Returns:
            List of facility risk summaries
        """
        # Get all facilities
        facilities = self.facility_repo.get_all()
        
        # Calculate risk for each facility
        facility_risks = []
        for facility in facilities:
            # Get equipment for this facility
            equipment = self.equipment_repo.get_by_facility(facility.id)
            
            if not equipment:
                # Skip facilities with no equipment
                continue
                
            # Calculate risks
            equipment_risks = self.calculator.bulk_calculate_risks(equipment)
            
            # Calculate distribution
            risk_distribution = self.calculator.get_risk_distribution(equipment_risks)
            
            # Calculate average risk
            avg_risk = sum(r["overall_risk"] for r in equipment_risks) / len(equipment_risks)
            
            # Determine highest risk category
            highest_category = RiskCategory.LOW
            for category in [RiskCategory.CRITICAL, RiskCategory.HIGH, RiskCategory.MEDIUM]:
                if risk_distribution[category] > 0:
                    highest_category = category
                    break
            
            # Create summary
            facility_risks.append({
                "facility_id": facility.id,
                "name": facility.name,
                "location": facility.location,
                "risk_score": round(avg_risk, 1),
                "risk_category": highest_category,
                "equipment_count": len(equipment),
                "risk_distribution": risk_distribution
            })
        
        # Sort by risk score (highest first)
        return sorted(facility_risks, key=lambda x: x["risk_score"], reverse=True) 