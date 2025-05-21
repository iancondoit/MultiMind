"""
Risk calculator for VoltMetrics.

This module implements algorithms for calculating risk scores for electrical equipment.
"""

import math
from datetime import datetime
from typing import Dict, Any, Optional, Tuple, List

from src.models.equipment import Equipment, EquipmentType


class RiskCategory:
    """Risk categories for classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCalculator:
    """
    Calculator for electrical equipment risk scores.
    
    Implements algorithms to evaluate equipment risk based on multiple factors:
    - Age factor
    - Material factor (aluminum vs copper)
    - Maintenance factor
    - Environmental factor
    - Operational factor
    """
    
    # Expected service life in years by equipment type
    SERVICE_LIFE_MAP = {
        EquipmentType.PANEL: 35,        # 30-40 years average
        EquipmentType.TRANSFORMER: 25,   # 25-30 years average
        EquipmentType.SWITCHGEAR: 30,    # 30-35 years average
        EquipmentType.BREAKER: 20,       # 20-25 years average
        EquipmentType.OTHER: 20,         # Default conservative estimate
    }
    
    # Weight factors for different risk components (must sum to 1.0)
    WEIGHT_AGE = 0.30
    WEIGHT_MATERIAL = 0.15
    WEIGHT_MAINTENANCE = 0.20
    WEIGHT_ENVIRONMENTAL = 0.15
    WEIGHT_OPERATIONAL = 0.20
    
    # Risk thresholds (for 0-100 scale)
    THRESHOLD_LOW = 25
    THRESHOLD_MEDIUM = 50
    THRESHOLD_HIGH = 75
    
    def __init__(self):
        """Initialize the risk calculator."""
        # Validate weights sum to 1.0
        weights_sum = (self.WEIGHT_AGE + self.WEIGHT_MATERIAL + self.WEIGHT_MAINTENANCE + 
                      self.WEIGHT_ENVIRONMENTAL + self.WEIGHT_OPERATIONAL)
        if not math.isclose(weights_sum, 1.0, rel_tol=1e-5):
            raise ValueError(f"Risk factor weights must sum to 1.0, got {weights_sum}")
    
    def calculate_risk(self, equipment: Equipment) -> Dict[str, Any]:
        """
        Calculate overall risk score for a piece of equipment.
        
        Args:
            equipment: Equipment object to evaluate
            
        Returns:
            Dictionary with risk scores and category
        """
        # Calculate individual risk factors
        age_risk = self._calculate_age_risk(equipment)
        material_risk = self._calculate_material_risk(equipment)
        maintenance_risk = self._calculate_maintenance_risk(equipment)
        environmental_risk = self._calculate_environmental_risk(equipment)
        operational_risk = self._calculate_operational_risk(equipment)
        
        # Calculate weighted overall risk score (0-100 scale)
        overall_risk = (
            age_risk * self.WEIGHT_AGE +
            material_risk * self.WEIGHT_MATERIAL +
            maintenance_risk * self.WEIGHT_MAINTENANCE +
            environmental_risk * self.WEIGHT_ENVIRONMENTAL +
            operational_risk * self.WEIGHT_OPERATIONAL
        )
        
        # Determine risk category
        if overall_risk >= self.THRESHOLD_HIGH:
            risk_category = RiskCategory.CRITICAL if overall_risk >= 90 else RiskCategory.HIGH
        elif overall_risk >= self.THRESHOLD_MEDIUM:
            risk_category = RiskCategory.MEDIUM
        else:
            risk_category = RiskCategory.LOW
        
        # Compile results
        return {
            "overall_risk": round(overall_risk, 1),
            "risk_category": risk_category,
            "factors": {
                "age_risk": round(age_risk, 1),
                "material_risk": round(material_risk, 1),
                "maintenance_risk": round(maintenance_risk, 1),
                "environmental_risk": round(environmental_risk, 1),
                "operational_risk": round(operational_risk, 1)
            },
            "equipment_id": equipment.id,
            "equipment_type": equipment.type.value,
            "assessment_date": datetime.now().isoformat()
        }
    
    def _calculate_age_risk(self, equipment: Equipment) -> float:
        """
        Calculate risk based on equipment age.
        
        Args:
            equipment: Equipment object to evaluate
            
        Returns:
            Risk score (0-100)
        """
        # Get expected service life for this type of equipment
        expected_life = self.SERVICE_LIFE_MAP.get(equipment.type, self.SERVICE_LIFE_MAP[EquipmentType.OTHER])
        
        # Calculate age in years
        age_delta = datetime.now() - equipment.installation_date
        age_years = age_delta.days / 365.25
        
        # Calculate age as percentage of expected life
        life_percentage = (age_years / expected_life) * 100
        
        # Map to risk score (0-100)
        # - Below 50% of service life: low risk (0-25)
        # - 50-80% of service life: medium risk (25-50)
        # - 80-100% of service life: high risk (50-75)
        # - Beyond service life: critical risk (75-100)
        if life_percentage < 50:
            # Linear mapping from 0% to 50% of life to 0-25 risk
            return min(25, (life_percentage / 50) * 25)
        elif life_percentage < 80:
            # Linear mapping from 50% to 80% of life to 25-50 risk
            return 25 + ((life_percentage - 50) / 30) * 25
        elif life_percentage < 100:
            # Linear mapping from 80% to 100% of life to 50-75 risk
            return 50 + ((life_percentage - 80) / 20) * 25
        else:
            # Beyond service life, risk increases more quickly
            # Cap at 100 for equipment well beyond service life
            over_life = life_percentage - 100
            return min(100, 75 + (over_life / 50) * 25)
    
    def _calculate_material_risk(self, equipment: Equipment) -> float:
        """
        Calculate risk based on materials (aluminum vs copper).
        
        Args:
            equipment: Equipment object to evaluate
            
        Returns:
            Risk score (0-100)
        """
        # Base risk on aluminum conductors
        base_risk = 60 if equipment.is_aluminum_conductor else 20
        
        # Additional risk from age if aluminum (older aluminum connections are higher risk)
        if equipment.is_aluminum_conductor:
            age_delta = datetime.now() - equipment.installation_date
            age_years = age_delta.days / 365.25
            
            # Add up to 40 more points for very old aluminum equipment
            if age_years > 40:  # Pre-1980s aluminum wiring has higher risk
                additional_risk = 40
            elif age_years > 30:
                additional_risk = 30
            elif age_years > 20:
                additional_risk = 20
            elif age_years > 10:
                additional_risk = 10
            else:
                additional_risk = 0
            
            return min(100, base_risk + additional_risk)
        
        return base_risk
    
    def _calculate_maintenance_risk(self, equipment: Equipment) -> float:
        """
        Calculate risk based on maintenance history.
        
        Args:
            equipment: Equipment object to evaluate
            
        Returns:
            Risk score (0-100)
        """
        # If no maintenance record exists, high risk
        if not equipment.last_maintenance_date:
            return 90
        
        # Calculate years since last maintenance
        maintenance_delta = datetime.now() - equipment.last_maintenance_date
        years_since_maintenance = maintenance_delta.days / 365.25
        
        # Risk increases with time since maintenance
        if years_since_maintenance < 1:
            # Recent maintenance, low risk
            return 10 + (years_since_maintenance * 15)
        elif years_since_maintenance < 3:
            # Moderate time since maintenance
            return 25 + ((years_since_maintenance - 1) / 2) * 25
        elif years_since_maintenance < 5:
            # Longer time since maintenance
            return 50 + ((years_since_maintenance - 3) / 2) * 25
        else:
            # Very long time since maintenance
            return min(100, 75 + ((years_since_maintenance - 5) / 5) * 25)
    
    def _calculate_environmental_risk(self, equipment: Equipment) -> float:
        """
        Calculate risk based on environmental factors.
        
        Args:
            equipment: Equipment object to evaluate
            
        Returns:
            Risk score (0-100)
        """
        # Consider humidity exposure (higher humidity = higher risk)
        humidity_risk = 0
        if equipment.humidity_exposure > 80:
            humidity_risk = 40  # Very high humidity
        elif equipment.humidity_exposure > 70:
            humidity_risk = 30  # High humidity
        elif equipment.humidity_exposure > 60:
            humidity_risk = 20  # Moderate humidity
        elif equipment.humidity_exposure > 50:
            humidity_risk = 10  # Slight humidity concern
        
        # Consider temperature exposure (higher temperature = higher risk)
        temp_risk = 0
        if equipment.temperature_exposure > 90:
            temp_risk = 40  # Very high temperature
        elif equipment.temperature_exposure > 85:
            temp_risk = 30  # High temperature
        elif equipment.temperature_exposure > 80:
            temp_risk = 20  # Moderate temperature
        elif equipment.temperature_exposure > 75:
            temp_risk = 10  # Slight temperature concern
        
        # Consider additional environmental data if available
        additional_risk = 0
        additional_data = equipment.additional_data or {}
        
        if additional_data.get("visible_corrosion", False):
            additional_risk += 20
            
        if additional_data.get("unusual_noise", False) and equipment.type == EquipmentType.TRANSFORMER:
            additional_risk += 15
            
        # Combine and cap at 100
        return min(100, humidity_risk + temp_risk + additional_risk)
    
    def _calculate_operational_risk(self, equipment: Equipment) -> float:
        """
        Calculate risk based on operational factors.
        
        Args:
            equipment: Equipment object to evaluate
            
        Returns:
            Risk score (0-100)
        """
        # Calculate operational risk based primarily on loading percentage
        loading_pct = equipment.loading_percentage
        
        # Loading percentage risk
        if loading_pct > 90:
            loading_risk = 70  # Very high loading
        elif loading_pct > 80:
            loading_risk = 50  # High loading
        elif loading_pct > 70:
            loading_risk = 30  # Moderate loading
        elif loading_pct > 60:
            loading_risk = 20  # Normal high loading
        else:
            loading_risk = 10  # Normal loading
        
        # Consider additional operational data if available
        additional_risk = 0
        additional_data = equipment.additional_data or {}
        
        if additional_data.get("thermal_issues", False):
            additional_risk += 20
            
        if additional_data.get("loose_parts", False):
            additional_risk += 15
            
        if additional_data.get("heat_discoloration", False):
            additional_risk += 15
            
        if equipment.type == EquipmentType.BREAKER and additional_data.get("trip_tests") == "failed":
            additional_risk += 25
        
        # Combine and cap at 100
        return min(100, loading_risk + additional_risk)
    
    def bulk_calculate_risks(self, equipment_list: List[Equipment]) -> List[Dict[str, Any]]:
        """
        Calculate risk for multiple equipment items.
        
        Args:
            equipment_list: List of Equipment objects to evaluate
            
        Returns:
            List of risk assessment dictionaries
        """
        return [self.calculate_risk(equipment) for equipment in equipment_list]
    
    def get_risk_distribution(self, risk_assessments: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get distribution of risk categories from assessments.
        
        Args:
            risk_assessments: List of risk assessment dictionaries
            
        Returns:
            Dictionary with counts for each risk category
        """
        distribution = {
            RiskCategory.LOW: 0,
            RiskCategory.MEDIUM: 0,
            RiskCategory.HIGH: 0,
            RiskCategory.CRITICAL: 0
        }
        
        for assessment in risk_assessments:
            category = assessment["risk_category"]
            distribution[category] += 1
            
        return distribution 