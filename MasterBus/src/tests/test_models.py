#!/usr/bin/env python3
"""
Tests for data models in the MasterBus API.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

# These will be implemented later
from src.models.facility import Facility, FacilityLocation, RiskSummary
from src.models.equipment import Equipment, EquipmentSpecifications, EquipmentLocation
from src.models.risk import RiskAssessment, RiskFactor
from src.models.compliance import Compliance, NFPA70B, NFPA70E


class TestFacilityModel:
    """Tests for the Facility model."""
    
    def test_create_facility(self):
        """Test creating a valid Facility instance."""
        facility = Facility(
            id="facility-123",
            name="Main Campus",
            location=FacilityLocation(
                address="123 Main St, Springfield, IL 62701",
                coordinates={"lat": 39.7817, "lng": -89.6501}
            ),
            created_at=datetime.fromisoformat("2025-01-01T00:00:00"),
            last_updated=datetime.fromisoformat("2025-05-01T14:30:00"),
            risk_summary=RiskSummary(
                risk_score=65,
                risk_level="Medium",
                high_risk_equipment_count=5,
                medium_risk_equipment_count=29,
                low_risk_equipment_count=24,
                critical_risk_equipment_count=2
            )
        )
        
        assert facility.id == "facility-123"
        assert facility.name == "Main Campus"
        assert facility.location.address == "123 Main St, Springfield, IL 62701"
        assert facility.location.coordinates["lat"] == 39.7817
        assert facility.risk_summary.risk_score == 65
        assert facility.risk_summary.risk_level == "Medium"

    def test_invalid_risk_level(self):
        """Test that invalid risk levels are rejected."""
        with pytest.raises(ValidationError):
            RiskSummary(
                risk_score=65,
                risk_level="Invalid",  # Not one of the valid options
                high_risk_equipment_count=5,
                medium_risk_equipment_count=29,
                low_risk_equipment_count=24,
                critical_risk_equipment_count=2
            )


class TestEquipmentModel:
    """Tests for the Equipment model."""
    
    def test_create_equipment(self):
        """Test creating a valid Equipment instance."""
        equipment = Equipment(
            id="equip-456",
            name="Panel A",
            type="panel",
            manufacturer="Square D",
            model="QO-30",
            serial_number="SN123456",
            installation_date=datetime.fromisoformat("1980-03-15"),
            location=EquipmentLocation(
                facility_id="facility-123",
                facility_name="Main Campus",
                building="Building 1",
                room="Electrical Room 3",
                coordinates={"lat": 39.7834, "lng": -89.6520}
            ),
            specifications=EquipmentSpecifications(
                voltage="208/120V",
                amperage=200,
                phases=3,
                mount_type="surface",
                enclosure_type="NEMA 1"
            ),
            photos=[],
            risk_assessment=RiskAssessment(
                risk_level="Critical",
                risk_score=82,
                condition="Poor",
                risk_factors=[
                    RiskFactor(
                        factor="age",
                        score=90,
                        description="Panel is 45 years old"
                    )
                ],
                temperature="78°C",
                rust_level="Moderate",
                corrosion_level="Moderate"
            ),
            compliance=Compliance(
                nfpa_70b=NFPA70B(
                    compliant=False,
                    compliance_percentage=45,
                    next_inspection_due=datetime.fromisoformat("2023-08-05"),
                    maintenance_status="overdue",
                    last_inspection=datetime.fromisoformat("2023-08-05T09:00:00")
                ),
                nfpa_70e=NFPA70E(
                    compliant=True,
                    compliance_percentage=92,
                    arc_flash_label_present=True,
                    ppe_requirements="Category 2",
                    incident_energy=8.2,
                    last_assessment=datetime.fromisoformat("2024-06-03T14:15:00")
                )
            ),
            created_at=datetime.fromisoformat("2024-11-17T13:20:00"),
            last_updated=datetime.fromisoformat("2025-04-28T10:15:00")
        )
        
        assert equipment.id == "equip-456"
        assert equipment.name == "Panel A"
        assert equipment.type == "panel"
        assert equipment.installation_date.year == 1980
        assert equipment.risk_assessment.risk_level == "Critical"
        assert equipment.risk_assessment.risk_score == 82
        assert equipment.compliance.nfpa_70b.compliance_percentage == 45
        assert equipment.compliance.nfpa_70e.compliance_percentage == 92


class TestRiskAssessmentModel:
    """Tests for the RiskAssessment model."""
    
    def test_create_risk_assessment(self):
        """Test creating a valid RiskAssessment instance."""
        risk = RiskAssessment(
            risk_level="High",
            risk_score=75,
            condition="Fair",
            risk_factors=[
                RiskFactor(
                    factor="age",
                    score=70,
                    description="Equipment is 30 years old"
                ),
                RiskFactor(
                    factor="maintenance",
                    score=80,
                    description="Maintenance overdue by 6 months"
                )
            ],
            last_assessed=datetime.fromisoformat("2025-05-01T10:00:00")
        )
        
        assert risk.risk_level == "High"
        assert risk.risk_score == 75
        assert risk.condition == "Fair"
        assert len(risk.risk_factors) == 2
        assert risk.risk_factors[0].factor == "age"
        assert risk.risk_factors[1].score == 80

    def test_risk_score_range(self):
        """Test that risk scores must be within the valid range."""
        # Test score too high
        with pytest.raises(ValidationError):
            RiskAssessment(
                risk_level="High",
                risk_score=101,  # Above max of 100
                condition="Fair"
            )
            
        # Test score too low
        with pytest.raises(ValidationError):
            RiskAssessment(
                risk_level="High",
                risk_score=-1,  # Below min of 0
                condition="Fair"
            )


class TestComplianceModel:
    """Tests for the Compliance model."""
    
    def test_create_compliance(self):
        """Test creating a valid Compliance instance."""
        compliance = Compliance(
            nfpa_70b=NFPA70B(
                compliant=True,
                compliance_percentage=85,
                next_inspection_due=datetime.fromisoformat("2026-03-15"),
                maintenance_status="up_to_date",
                last_inspection=datetime.fromisoformat("2025-03-15T14:30:00")
            ),
            nfpa_70e=NFPA70E(
                compliant=True,
                compliance_percentage=92,
                arc_flash_label_present=True,
                ppe_requirements="Category 2",
                incident_energy=8.2,
                last_assessment=datetime.fromisoformat("2024-06-03T14:15:00")
            ),
            last_assessed=datetime.fromisoformat("2025-05-01T14:30:00")
        )
        
        assert compliance.nfpa_70b.compliant is True
        assert compliance.nfpa_70b.compliance_percentage == 85
        assert compliance.nfpa_70b.maintenance_status == "up_to_date"
        assert compliance.nfpa_70e.compliance_percentage == 92
        assert compliance.nfpa_70e.arc_flash_label_present is True 