"""
NFPA 70E compliance evaluation module.

This module implements algorithms for evaluating compliance with NFPA 70E
(Standard for Electrical Safety in the Workplace).
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from src.models.equipment import Equipment, EquipmentType
from src.models.facility import Facility


class NFPA70EEvaluator:
    """
    Evaluator for NFPA 70E compliance.
    
    Implements algorithms to determine if equipment and facilities comply with
    NFPA 70E standards for electrical safety in the workplace.
    """
    
    # Equipment types requiring arc flash assessment
    ARC_FLASH_REQUIRED_TYPES = [
        EquipmentType.PANEL,
        EquipmentType.TRANSFORMER,
        EquipmentType.SWITCHGEAR
    ]
    
    # Equipment loading percentages that trigger higher scrutiny
    HIGH_LOAD_THRESHOLD = 80  # >= 80% considered high load
    
    def evaluate_equipment(self, equipment: Equipment) -> Dict[str, Any]:
        """
        Evaluate NFPA 70E compliance for a single piece of equipment.
        
        Args:
            equipment: Equipment to evaluate
            
        Returns:
            Dictionary with compliance evaluation results
        """
        issues = []
        now = datetime.now()
        
        # Check if arc flash assessment is required
        requires_arc_flash = equipment.type in self.ARC_FLASH_REQUIRED_TYPES
        
        # Check if additional data contains arc flash information
        if requires_arc_flash:
            if not equipment.additional_data or 'arc_flash' not in equipment.additional_data:
                issues.append("Missing required arc flash assessment")
            else:
                arc_data = equipment.additional_data['arc_flash']
                
                # Check arc flash label date (if available)
                if 'assessment_date' in arc_data:
                    try:
                        assessment_date = datetime.fromisoformat(arc_data['assessment_date'])
                        years_since_assessment = (now - assessment_date).days / 365.25
                        
                        # NFPA 70E requires reevaluation every 5 years or when changes occur
                        if years_since_assessment > 5:
                            issues.append(f"Arc flash assessment outdated (last done {int(years_since_assessment)} years ago)")
                    except (ValueError, TypeError):
                        issues.append("Invalid arc flash assessment date format")
                else:
                    issues.append("Arc flash assessment date not documented")
                
                # Check if PPE category is specified
                if 'ppe_category' not in arc_data:
                    issues.append("PPE category not specified")
                    
                # Check if incident energy is specified
                if 'incident_energy' not in arc_data:
                    issues.append("Incident energy not specified")
                    
                # Check if working distance is specified
                if 'working_distance' not in arc_data:
                    issues.append("Working distance not specified")
                    
                # Check if arc flash boundary is specified
                if 'arc_flash_boundary' not in arc_data:
                    issues.append("Arc flash boundary not specified")
        
        # Check if equipment is labeled for safety
        if not equipment.additional_data or 'safety_labels' not in equipment.additional_data:
            issues.append("Missing safety labeling information")
        else:
            safety_labels = equipment.additional_data['safety_labels']
            
            # Check for required safety labels
            required_labels = ["shock_hazard", "voltage"]
            missing_labels = [label for label in required_labels if label not in safety_labels]
            if missing_labels:
                issues.append(f"Missing required safety labels: {', '.join(missing_labels)}")
        
        # Check loading percentage for overload conditions
        if equipment.loading_percentage >= self.HIGH_LOAD_THRESHOLD:
            issues.append(f"Equipment loaded at {equipment.loading_percentage}% of rating (exceeds {self.HIGH_LOAD_THRESHOLD}% threshold)")
        
        # Calculate compliance score and status
        if not issues:
            compliance_score = 100
            status = "compliant"
        elif len(issues) == 1:
            compliance_score = 75
            status = "partial"
        elif len(issues) <= 3:
            compliance_score = 50
            status = "partial"
        else:
            compliance_score = 25
            status = "non_compliant"
        
        return {
            "status": status,
            "score": compliance_score,
            "issues": issues,
            "equipment_id": equipment.id,
            "last_evaluation": now.isoformat()
        }
    
    def evaluate_facility(self, facility: Facility, 
                         equipment_list: Optional[List[Equipment]] = None) -> Dict[str, Any]:
        """
        Evaluate NFPA 70E compliance for an entire facility.
        
        Args:
            facility: Facility to evaluate
            equipment_list: Optional list of equipment in facility (will be fetched if not provided)
            
        Returns:
            Dictionary with facility-level compliance evaluation results
        """
        if not equipment_list:
            # In a real system, this would fetch from the database
            return {
                "status": "unknown",
                "score": 0,
                "equipment_compliance": {
                    "compliant": 0,
                    "partial": 0,
                    "non_compliant": 0
                },
                "facility_id": facility.id,
                "last_evaluation": datetime.now().isoformat(),
                "issues": ["No equipment data available for evaluation"]
            }
        
        # Evaluate each piece of equipment
        equipment_evaluations = []
        
        for equipment in equipment_list:
            equipment_evaluations.append(self.evaluate_equipment(equipment))
        
        # Count equipment by compliance status
        status_counts = {
            "compliant": sum(1 for ev in equipment_evaluations if ev["status"] == "compliant"),
            "partial": sum(1 for ev in equipment_evaluations if ev["status"] == "partial"),
            "non_compliant": sum(1 for ev in equipment_evaluations if ev["status"] == "non_compliant")
        }
        
        # Calculate overall facility compliance score
        if not equipment_evaluations:
            facility_score = 0
        else:
            facility_score = sum(ev["score"] for ev in equipment_evaluations) / len(equipment_evaluations)
        
        # Determine overall facility compliance status
        if facility_score >= 90:
            facility_status = "compliant"
        elif facility_score >= 60:
            facility_status = "partial"
        else:
            facility_status = "non_compliant"
        
        # Identify facility-level NFPA 70E issues
        facility_issues = []
        
        # Check if facility has documented electrical safety program
        if not facility.additional_data or 'safety_program' not in facility.additional_data:
            facility_issues.append("No documented electrical safety program")
        
        # Check if facility has emergency procedures
        if not facility.additional_data or 'emergency_procedures' not in facility.additional_data:
            facility_issues.append("No documented emergency procedures")
        
        # Identify most common equipment issues
        all_equipment_issues = [issue for ev in equipment_evaluations for issue in ev["issues"]]
        issue_counts = {}
        for issue in all_equipment_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
        # Sort issues by frequency
        common_issues = sorted(
            [{"issue": issue, "count": count} for issue, count in issue_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )
        
        # Combine facility and equipment issues
        all_issues = facility_issues + [issue["issue"] for issue in common_issues[:3]]
        
        return {
            "status": facility_status,
            "score": round(facility_score),
            "equipment_compliance": status_counts,
            "equipment_count": len(equipment_evaluations),
            "facility_issues": facility_issues,
            "common_equipment_issues": common_issues[:5],  # Top 5 most common equipment issues
            "facility_id": facility.id,
            "last_evaluation": datetime.now().isoformat()
        } 