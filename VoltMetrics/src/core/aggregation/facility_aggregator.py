"""
Facility-level aggregation module for VoltMetrics.

This module implements algorithms for aggregating equipment-level risk assessments
and compliance evaluations at the facility level.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from src.models.equipment import Equipment, EquipmentType
from src.models.facility import Facility
from src.core.risk_calculator import RiskCalculator
from src.core.compliance.nfpa70b import NFPA70BEvaluator
from src.core.compliance.nfpa70e import NFPA70EEvaluator


class FacilityAggregator:
    """
    Aggregator for facility-level metrics.
    
    Aggregates equipment-level risk and compliance data into facility-level
    metrics and insights.
    """
    
    def __init__(self):
        """Initialize the facility aggregator."""
        self.risk_calculator = RiskCalculator()
        self.nfpa70b_evaluator = NFPA70BEvaluator()
        self.nfpa70e_evaluator = NFPA70EEvaluator()
    
    def aggregate_facility_risk(self, facility: Facility, 
                               equipment_list: List[Equipment]) -> Dict[str, Any]:
        """
        Calculate aggregate risk metrics for a facility.
        
        Args:
            facility: Facility to evaluate
            equipment_list: List of equipment in the facility
            
        Returns:
            Dictionary with facility-level risk metrics
        """
        if not equipment_list:
            return {
                "facility_id": facility.id,
                "name": facility.name,
                "overall_risk_score": 0,
                "risk_category": "unknown",
                "equipment_counts": {
                    "total": 0,
                    "by_risk_category": {},
                    "by_type": {}
                },
                "calculated_at": datetime.now().isoformat(),
                "error": "No equipment data available"
            }
        
        # Calculate risk for each piece of equipment
        risk_assessments = []
        for equipment in equipment_list:
            risk_result = self.risk_calculator.calculate_risk(equipment)
            risk_assessments.append(risk_result)
        
        # Calculate overall facility risk score (weighted by equipment importance)
        if not risk_assessments:
            overall_risk = 0
        else:
            # Calculate weighted average based on equipment type importance
            # Transformers and switchgear have higher weights than panels and breakers
            total_weight = 0
            weighted_sum = 0
            
            for assessment in risk_assessments:
                equipment = next((e for e in equipment_list if e.id == assessment["equipment_id"]), None)
                if equipment:
                    # Assign weight based on equipment type
                    if equipment.type == EquipmentType.TRANSFORMER:
                        weight = 1.5  # Transformers are critical
                    elif equipment.type == EquipmentType.SWITCHGEAR:
                        weight = 1.3  # Switchgear is important
                    elif equipment.type == EquipmentType.PANEL:
                        weight = 1.0  # Panels are standard
                    else:
                        weight = 0.8  # Other equipment types less critical
                    
                    weighted_sum += assessment["overall_risk"] * weight
                    total_weight += weight
            
            overall_risk = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Determine facility risk category
        if overall_risk >= 85:
            risk_category = "critical"
        elif overall_risk >= 70:
            risk_category = "high"
        elif overall_risk >= 40:
            risk_category = "medium"
        else:
            risk_category = "low"
        
        # Count equipment by risk category
        risk_category_counts = {
            "critical": sum(1 for r in risk_assessments if r["risk_category"] == "critical"),
            "high": sum(1 for r in risk_assessments if r["risk_category"] == "high"),
            "medium": sum(1 for r in risk_assessments if r["risk_category"] == "medium"),
            "low": sum(1 for r in risk_assessments if r["risk_category"] == "low"),
        }
        
        # Count equipment by type
        type_counts = {}
        for equipment in equipment_list:
            type_name = equipment.type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Identify top risk factors
        risk_factors = self._identify_top_risk_factors(risk_assessments)
        
        # Identify equipment with highest risk
        top_risk_equipment = sorted(
            risk_assessments, 
            key=lambda x: x["overall_risk"], 
            reverse=True
        )[:5]  # Top 5 highest risk
        
        top_risks = []
        for assessment in top_risk_equipment:
            equipment = next((e for e in equipment_list if e.id == assessment["equipment_id"]), None)
            if equipment:
                top_risks.append({
                    "equipment_id": equipment.id,
                    "name": equipment.name,
                    "type": equipment.type.value,
                    "risk_score": assessment["overall_risk"],
                    "risk_category": assessment["risk_category"],
                    "top_factor": max(assessment["factors"].items(), key=lambda x: x[1])[0]
                })
        
        # Return aggregated facility risk data
        return {
            "facility_id": facility.id,
            "name": facility.name,
            "overall_risk_score": round(overall_risk, 1),
            "risk_category": risk_category,
            "equipment_counts": {
                "total": len(equipment_list),
                "by_risk_category": risk_category_counts,
                "by_type": type_counts
            },
            "risk_factors": risk_factors,
            "top_risks": top_risks,
            "calculated_at": datetime.now().isoformat(),
            "algorithm_version": "1.0.0"
        }
    
    def aggregate_facility_compliance(self, facility: Facility, 
                                     equipment_list: List[Equipment],
                                     maintenance_records: Optional[Dict[str, List[Any]]] = None) -> Dict[str, Any]:
        """
        Calculate aggregate compliance metrics for a facility.
        
        Args:
            facility: Facility to evaluate
            equipment_list: List of equipment in the facility
            maintenance_records: Optional dict mapping equipment IDs to maintenance records
            
        Returns:
            Dictionary with facility-level compliance metrics
        """
        if not equipment_list:
            return {
                "facility_id": facility.id,
                "name": facility.name,
                "compliance": {
                    "nfpa70b": {"status": "unknown", "score": 0},
                    "nfpa70e": {"status": "unknown", "score": 0}
                },
                "calculated_at": datetime.now().isoformat(),
                "error": "No equipment data available"
            }
        
        # Evaluate NFPA 70B compliance
        nfpa70b_result = self.nfpa70b_evaluator.evaluate_facility(
            facility, equipment_list, maintenance_records
        )
        
        # Evaluate NFPA 70E compliance
        nfpa70e_result = self.nfpa70e_evaluator.evaluate_facility(
            facility, equipment_list
        )
        
        # Return aggregated compliance data
        return {
            "facility_id": facility.id,
            "name": facility.name,
            "compliance": {
                "nfpa70b": {
                    "status": nfpa70b_result["status"],
                    "score": nfpa70b_result["score"],
                    "equipment_compliance": nfpa70b_result["equipment_compliance"],
                    "common_issues": nfpa70b_result.get("common_issues", [])
                },
                "nfpa70e": {
                    "status": nfpa70e_result["status"],
                    "score": nfpa70e_result["score"],
                    "equipment_compliance": nfpa70e_result["equipment_compliance"],
                    "facility_issues": nfpa70e_result.get("facility_issues", []),
                    "common_equipment_issues": nfpa70e_result.get("common_equipment_issues", [])
                }
            },
            "calculated_at": datetime.now().isoformat(),
        }
    
    def generate_comprehensive_report(self, facility: Facility, 
                                     equipment_list: List[Equipment],
                                     maintenance_records: Optional[Dict[str, List[Any]]] = None,
                                     historical_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive facility report with risk, compliance, and historical data.
        
        Args:
            facility: Facility to evaluate
            equipment_list: List of equipment in the facility
            maintenance_records: Optional dict mapping equipment IDs to maintenance records
            historical_data: Optional list of previous facility risk assessments
            
        Returns:
            Dictionary with comprehensive facility report
        """
        # Get risk assessment
        risk_assessment = self.aggregate_facility_risk(facility, equipment_list)
        
        # Get compliance assessment
        compliance_assessment = self.aggregate_facility_compliance(
            facility, equipment_list, maintenance_records
        )
        
        # Process historical trend data if available
        historical_trend = self._process_historical_trend(facility.id, risk_assessment, historical_data)
        
        # Generate recommendations based on risk and compliance
        recommendations = self._generate_recommendations(risk_assessment, compliance_assessment)
        
        # Combine all data into comprehensive report
        return {
            "facility_id": facility.id,
            "name": facility.name,
            "report_date": datetime.now().isoformat(),
            "risk_assessment": risk_assessment,
            "compliance_assessment": compliance_assessment["compliance"],
            "historical_trend": historical_trend,
            "recommendations": recommendations,
            "equipment_count": len(equipment_list),
            "report_version": "1.0.0"
        }
    
    def _identify_top_risk_factors(self, risk_assessments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify the most significant risk factors across all equipment.
        
        Args:
            risk_assessments: List of equipment risk assessment results
            
        Returns:
            List of top risk factors with their contribution
        """
        # Sum up factor scores across all equipment
        factor_totals = {}
        factor_counts = {}
        
        for assessment in risk_assessments:
            for factor_name, factor_score in assessment["factors"].items():
                factor_totals[factor_name] = factor_totals.get(factor_name, 0) + factor_score
                factor_counts[factor_name] = factor_counts.get(factor_name, 0) + 1
        
        # Calculate average scores for each factor
        factor_averages = {}
        for factor_name, total in factor_totals.items():
            count = factor_counts.get(factor_name, 1)  # Avoid division by zero
            factor_averages[factor_name] = total / count
        
        # Convert to list and sort by average score
        factors_list = [
            {"factor": factor_name, "average_score": round(avg_score, 1)}
            for factor_name, avg_score in factor_averages.items()
        ]
        
        # Sort by highest average score
        return sorted(factors_list, key=lambda x: x["average_score"], reverse=True)
    
    def _process_historical_trend(self, facility_id: str, 
                                 current_assessment: Dict[str, Any],
                                 historical_data: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Process historical trend data for a facility.
        
        Args:
            facility_id: ID of the facility
            current_assessment: Current risk assessment
            historical_data: Optional list of previous facility risk assessments
            
        Returns:
            Dictionary with historical trend information
        """
        if not historical_data:
            # No historical data available, return just the current assessment
            current_date = datetime.now().strftime("%Y-%m")
            return {
                "periods": [current_date],
                "scores": [current_assessment["overall_risk_score"]],
                "trend": "unknown"
            }
        
        # Extract date and risk score from historical data
        # Sort by date to ensure chronological order
        sorted_history = sorted(
            historical_data, 
            key=lambda x: datetime.fromisoformat(x["calculated_at"])
        )
        
        # Extract the last 6 periods (including current)
        periods = []
        scores = []
        
        for assessment in sorted_history[-5:]:  # Take last 5 historical assessments
            period = datetime.fromisoformat(assessment["calculated_at"]).strftime("%Y-%m")
            periods.append(period)
            scores.append(assessment["overall_risk_score"])
        
        # Add current assessment
        current_period = datetime.now().strftime("%Y-%m")
        if not periods or periods[-1] != current_period:
            periods.append(current_period)
            scores.append(current_assessment["overall_risk_score"])
        
        # Calculate trend (improving, stable, worsening)
        if len(scores) <= 1:
            trend = "unknown"
        else:
            # Calculate percentage change over the period
            start_score = scores[0]
            end_score = scores[-1]
            
            if start_score == 0:
                # Handle division by zero
                percent_change = 100 if end_score > 0 else 0
            else:
                percent_change = ((end_score - start_score) / start_score) * 100
            
            if percent_change <= -10:
                trend = "improving"
            elif percent_change >= 10:
                trend = "worsening"
            else:
                trend = "stable"
        
        return {
            "periods": periods,
            "scores": scores,
            "trend": trend
        }
    
    def _generate_recommendations(self, risk_assessment: Dict[str, Any], 
                                compliance_assessment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on risk and compliance assessments.
        
        Args:
            risk_assessment: Facility risk assessment
            compliance_assessment: Facility compliance assessment
            
        Returns:
            List of recommendations with priority
        """
        recommendations = []
        
        # Check for critical risk equipment
        if risk_assessment["equipment_counts"]["by_risk_category"].get("critical", 0) > 0:
            recommendations.append({
                "priority": "high",
                "category": "risk",
                "recommendation": "Address critical risk equipment immediately",
                "details": f"Facility has {risk_assessment['equipment_counts']['by_risk_category']['critical']} piece(s) of equipment with critical risk levels"
            })
        
        # Check for non-compliant NFPA 70B status
        nfpa70b = compliance_assessment["compliance"]["nfpa70b"]
        if nfpa70b["status"] == "non_compliant":
            recommendations.append({
                "priority": "high",
                "category": "compliance",
                "recommendation": "Address NFPA 70B compliance issues",
                "details": "Facility is non-compliant with NFPA 70B maintenance standards"
            })
        
        # Check for non-compliant NFPA 70E status
        nfpa70e = compliance_assessment["compliance"]["nfpa70e"]
        if nfpa70e["status"] == "non_compliant":
            recommendations.append({
                "priority": "high",
                "category": "safety",
                "recommendation": "Address NFPA 70E safety compliance issues",
                "details": "Facility is non-compliant with NFPA 70E electrical safety standards"
            })
        
        # Check for high-risk equipment
        if risk_assessment["equipment_counts"]["by_risk_category"].get("high", 0) > 0:
            recommendations.append({
                "priority": "medium",
                "category": "risk",
                "recommendation": "Develop plan for high-risk equipment",
                "details": f"Facility has {risk_assessment['equipment_counts']['by_risk_category']['high']} piece(s) of equipment with high risk levels"
            })
        
        # Add recommendation for partial compliance
        if nfpa70b["status"] == "partial":
            recommendations.append({
                "priority": "medium",
                "category": "compliance",
                "recommendation": "Improve maintenance compliance",
                "details": "Facility is only partially compliant with NFPA 70B standards"
            })
        
        # Sort recommendations by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_recommendations = sorted(
            recommendations,
            key=lambda x: priority_order.get(x["priority"], 99)
        )
        
        return sorted_recommendations 