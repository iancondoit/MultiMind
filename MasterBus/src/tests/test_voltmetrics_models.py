#!/usr/bin/env python3
"""
Tests for VoltMetrics integration models in the MasterBus API.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.voltmetrics import (
    VoltMetricsCalculationRequest,
    VoltMetricsCalculationResponse,
    VoltMetricsBatchRequest, 
    VoltMetricsBatchResponse
)


class TestVoltMetricsCalculationRequest:
    """Tests for the VoltMetricsCalculationRequest model."""
    
    def test_create_calculation_request(self):
        """Test creating a valid calculation request."""
        request = VoltMetricsCalculationRequest(
            equipment_id="equip-456",
            calculation_type="both",
            equipment_data={
                "type": "panel",
                "installation_date": "1980-03-15",
                "voltage": "208/120V",
                "amperage": 200
            },
            include_history=True
        )
        
        assert request.equipment_id == "equip-456"
        assert request.calculation_type == "both"
        assert request.equipment_data["type"] == "panel"
        assert request.include_history is True

    def test_invalid_calculation_type(self):
        """Test that invalid calculation types are rejected."""
        with pytest.raises(ValidationError):
            VoltMetricsCalculationRequest(
                equipment_id="equip-456",
                calculation_type="invalid",  # Not one of the valid options
                equipment_data={
                    "type": "panel",
                    "installation_date": "1980-03-15"
                }
            )


class TestVoltMetricsCalculationResponse:
    """Tests for the VoltMetricsCalculationResponse model."""
    
    def test_create_calculation_response(self):
        """Test creating a valid calculation response."""
        response = VoltMetricsCalculationResponse(
            equipment_id="equip-456",
            request_id="req-123",
            status="completed",
            risk_metrics={
                "risk_level": "Critical",
                "risk_score": 82,
                "risk_factors": []
            },
            compliance_metrics={
                "nfpa_70b": {
                    "compliant": False,
                    "compliance_percentage": 45
                },
                "nfpa_70e": {
                    "compliant": True,
                    "compliance_percentage": 92
                }
            },
            calculation_timestamp=datetime.fromisoformat("2025-05-01T14:30:00"),
            created_at=datetime.fromisoformat("2025-05-01T14:29:00"),
            last_updated=datetime.fromisoformat("2025-05-01T14:30:00")
        )
        
        assert response.equipment_id == "equip-456"
        assert response.request_id == "req-123"
        assert response.status == "completed"
        assert response.risk_metrics["risk_level"] == "Critical"
        assert response.compliance_metrics["nfpa_70b"]["compliance_percentage"] == 45

    def test_failed_calculation_response(self):
        """Test creating a failed calculation response with error message."""
        response = VoltMetricsCalculationResponse(
            equipment_id="equip-456",
            request_id="req-123",
            status="failed",
            error_message="Invalid equipment data provided",
            calculation_timestamp=datetime.fromisoformat("2025-05-01T14:30:00")
        )
        
        assert response.equipment_id == "equip-456"
        assert response.status == "failed"
        assert response.error_message == "Invalid equipment data provided"
        assert response.risk_metrics is None
        assert response.compliance_metrics is None


class TestVoltMetricsBatchRequest:
    """Tests for the VoltMetricsBatchRequest model."""
    
    def test_create_batch_request(self):
        """Test creating a valid batch request."""
        request = VoltMetricsBatchRequest(
            facility_id="facility-123",
            calculation_type="both",
            equipment_ids=["equip-456", "equip-789", "equip-101"],
            priority="high",
            callback_url="https://api.masterbus.example.com/callbacks/batch-123"
        )
        
        assert request.facility_id == "facility-123"
        assert request.calculation_type == "both"
        assert len(request.equipment_ids) == 3
        assert request.priority == "high"
        assert request.callback_url == "https://api.masterbus.example.com/callbacks/batch-123"

    def test_default_priority(self):
        """Test that the default priority is 'medium'."""
        request = VoltMetricsBatchRequest(
            facility_id="facility-123",
            calculation_type="risk",
            equipment_ids=["equip-456", "equip-789"]
        )
        
        assert request.priority == "medium"


class TestVoltMetricsBatchResponse:
    """Tests for the VoltMetricsBatchResponse model."""
    
    def test_create_batch_response(self):
        """Test creating a valid batch response."""
        response = VoltMetricsBatchResponse(
            batch_id="batch-123",
            facility_id="facility-123",
            status="processing",
            total_items=50,
            processed_items=25,
            completion_percentage=50,
            estimated_completion_time=datetime.fromisoformat("2025-05-01T15:30:00"),
            created_at=datetime.fromisoformat("2025-05-01T14:30:00"),
            last_updated=datetime.fromisoformat("2025-05-01T14:45:00")
        )
        
        assert response.batch_id == "batch-123"
        assert response.facility_id == "facility-123"
        assert response.status == "processing"
        assert response.total_items == 50
        assert response.processed_items == 25
        assert response.completion_percentage == 50
        assert response.estimated_completion_time.isoformat() == "2025-05-01T15:30:00"

    def test_completed_batch_response(self):
        """Test creating a completed batch response with results URL."""
        response = VoltMetricsBatchResponse(
            batch_id="batch-123",
            facility_id="facility-123",
            status="completed",
            total_items=50,
            processed_items=50,
            completion_percentage=100,
            results_url="https://api.voltmetrics.example.com/results/batch-123"
        )
        
        assert response.batch_id == "batch-123"
        assert response.status == "completed"
        assert response.total_items == 50
        assert response.processed_items == 50
        assert response.completion_percentage == 100
        assert response.results_url == "https://api.voltmetrics.example.com/results/batch-123" 