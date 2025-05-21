"""
NFPA 70B compliance evaluation module.

This module implements algorithms for evaluating compliance with NFPA 70B
(Recommended Practice for Electrical Equipment Maintenance).
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from src.models.equipment import Equipment, EquipmentType
from src.models.facility import Facility
from src.models.maintenance import MaintenanceRecord


class NFPA70BEvaluator:
    """
    Evaluator for NFPA 70B compliance.
    
    Implements algorithms to determine if equipment and facilities are in compliance
    with NFPA 70B recommended maintenance practices.
    """
    
    # Recommended inspection intervals (in months) by equipment type
    INSPECTION_INTERVALS = {
        EquipmentType.PANEL: 12,           # Annual inspection for panels
        EquipmentType.TRANSFORMER: 6,       # Bi-annual for transformers
        EquipmentType.SWITCHGEAR: 6,        # Bi-annual for switchgear
        EquipmentType.BREAKER: 12,          # Annual for breakers
        EquipmentType.OTHER: 12,            # Default annual
    }
    
    # Recommended thermographic inspection intervals (in months)
    THERMOGRAPHIC_INTERVALS = {
        EquipmentType.PANEL: 12,           # Annual thermographic inspection
        EquipmentType.TRANSFORMER: 6,       # Bi-annual for transformers
        EquipmentType.SWITCHGEAR: 6,        # Bi-annual for switchgear
        EquipmentType.BREAKER: 12,          # Annual for breakers
        EquipmentType.OTHER: 12,            # Default annual
    }
    
    # Required maintenance types by equipment type
    REQUIRED_MAINTENANCE_TYPES = {
        EquipmentType.PANEL: ["visual_inspection", "thermographic", "connection_tightness"],
        EquipmentType.TRANSFORMER: ["visual_inspection", "thermographic", "oil_analysis", "insulation_test"],
        EquipmentType.SWITCHGEAR: ["visual_inspection", "thermographic", "connection_tightness", "mechanism_test"],
        EquipmentType.BREAKER: ["visual_inspection", "thermographic", "mechanism_test", "trip_test"],
        EquipmentType.OTHER: ["visual_inspection", "thermographic"],
    }
    
    def evaluate_equipment(self, equipment: Equipment, 
                          maintenance_records: Optional[List[MaintenanceRecord]] = None) -> Dict[str, Any]:
        """
        Evaluate NFPA 70B compliance for a single piece of equipment.
        
        Args:
            equipment: Equipment to evaluate
            maintenance_records: Optional list of maintenance records (will be fetched if not provided)
            
        Returns:
            Dictionary with compliance evaluation results
        """
        now = datetime.now()
        
        # Get recommended intervals based on equipment type
        inspection_interval = self.INSPECTION_INTERVALS.get(
            equipment.type, self.INSPECTION_INTERVALS[EquipmentType.OTHER]
        )
        thermographic_interval = self.THERMOGRAPHIC_INTERVALS.get(
            equipment.type, self.THERMOGRAPHIC_INTERVALS[EquipmentType.OTHER]
        )
        required_types = self.REQUIRED_MAINTENANCE_TYPES.get(
            equipment.type, self.REQUIRED_MAINTENANCE_TYPES[EquipmentType.OTHER]
        )
        
        # If no maintenance records provided or empty list, mark as non-compliant
        if not maintenance_records:
            return {
                "status": "non_compliant",
                "score": 0,
                "issues": ["No maintenance records found"],
                "equipment_id": equipment.id,
                "last_evaluation": now.isoformat()
            }
        
        # Check time since last inspection
        last_inspection = max(
            (record.date for record in maintenance_records 
             if record.maintenance_type == "visual_inspection"),
            default=None
        )
        
        # Check time since last thermographic inspection
        last_thermographic = max(
            (record.date for record in maintenance_records 
             if record.maintenance_type == "thermographic"),
            default=None
        )
        
        # Initialize issues list
        issues = []
        
        # Check if regular inspection is overdue
        if not last_inspection:
            issues.append("No visual inspection records found")
        elif (now - last_inspection).days > (inspection_interval * 30):
            months_overdue = ((now - last_inspection).days / 30) - inspection_interval
            issues.append(f"Regular inspection overdue by {int(months_overdue)} months")
        
        # Check if thermographic inspection is overdue
        if not last_thermographic:
            issues.append("No thermographic inspection records found")
        elif (now - last_thermographic).days > (thermographic_interval * 30):
            months_overdue = ((now - last_thermographic).days / 30) - thermographic_interval
            issues.append(f"Thermographic inspection overdue by {int(months_overdue)} months")
        
        # Check for other required maintenance types
        performed_types = {record.maintenance_type for record in maintenance_records}
        missing_types = [mtype for mtype in required_types if mtype not in performed_types]
        
        if missing_types:
            issues.append(f"Missing required maintenance types: {', '.join(missing_types)}")
        
        # Calculate compliance score (0-100)
        if not issues:
            # Fully compliant
            compliance_score = 100
            status = "compliant"
        elif len(issues) == 1 and "overdue" in issues[0]:
            # Partially compliant - just timing issues
            compliance_score = 70
            status = "partial"
        elif len(issues) < 3:
            # Partially compliant - some issues
            compliance_score = 50
            status = "partial"
        else:
            # Major compliance issues
            compliance_score = 20
            status = "non_compliant"
        
        return {
            "status": status,
            "score": compliance_score,
            "issues": issues,
            "equipment_id": equipment.id,
            "last_evaluation": now.isoformat()
        }
    
    def evaluate_facility(self, facility: Facility, 
                         equipment_list: Optional[List[Equipment]] = None,
                         maintenance_records: Optional[Dict[str, List[MaintenanceRecord]]] = None) -> Dict[str, Any]:
        """
        Evaluate NFPA 70B compliance for an entire facility.
        
        Args:
            facility: Facility to evaluate
            equipment_list: Optional list of equipment in facility (will be fetched if not provided)
            maintenance_records: Optional dict mapping equipment IDs to their maintenance records
            
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
            records = maintenance_records.get(equipment.id, []) if maintenance_records else []
            equipment_evaluations.append(self.evaluate_equipment(equipment, records))
        
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
        
        # Identify most common issues
        all_issues = [issue for ev in equipment_evaluations for issue in ev["issues"]]
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
            
        # Sort issues by frequency
        common_issues = sorted(
            [{"issue": issue, "count": count} for issue, count in issue_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )
        
        return {
            "status": facility_status,
            "score": round(facility_score),
            "equipment_compliance": status_counts,
            "equipment_count": len(equipment_evaluations),
            "common_issues": common_issues[:5],  # Top 5 most common issues
            "facility_id": facility.id,
            "last_evaluation": datetime.now().isoformat()
        } 