#!/usr/bin/env python3
"""
Tests for API endpoints in the MasterBus API.
"""
import pytest
from fastapi.testclient import TestClient
from src.api.app import app


@pytest.fixture
def client():
    """Create a TestClient for API testing."""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_get_facilities(client):
    """Test the get facilities endpoint."""
    # This endpoint requires authentication in a real implementation
    # For testing, we're bypassing authentication
    response = client.get(
        "/api/v1/facilities/",
        headers={"Authorization": "Bearer mocktoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "facilities" in data
    assert len(data["facilities"]) >= 1
    assert "page" in data
    assert "limit" in data
    assert "total" in data


def test_get_facility(client):
    """Test the get facility endpoint."""
    # This endpoint requires authentication in a real implementation
    # For testing, we're bypassing authentication
    response = client.get(
        "/api/v1/facilities/facility-123",
        headers={"Authorization": "Bearer mocktoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "facility-123"
    assert "name" in data
    assert "location" in data
    assert "risk_score" in data


def test_get_nonexistent_facility(client):
    """Test getting a facility that doesn't exist."""
    response = client.get(
        "/api/v1/facilities/nonexistent",
        headers={"Authorization": "Bearer mocktoken"}
    )
    assert response.status_code == 404


def test_voltmetrics_calculate(client):
    """Test the VoltMetrics calculation endpoint."""
    # Test payload
    payload = {
        "equipment_id": "equip-456",
        "calculation_type": "both",
        "equipment_data": {
            "type": "panel",
            "installation_date": "1980-03-15",
            "voltage": "208/120V",
            "amperage": 200
        },
        "include_history": True
    }
    
    response = client.post(
        "/api/v1/voltmetrics/calculate",
        json=payload,
        headers={"Authorization": "Bearer mocktoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["equipment_id"] == "equip-456"
    assert data["status"] == "completed"
    assert "risk_metrics" in data
    assert "compliance_metrics" in data


def test_voltmetrics_batch(client):
    """Test the VoltMetrics batch calculation endpoint."""
    # Test payload
    payload = {
        "facility_id": "facility-123",
        "calculation_type": "both",
        "equipment_ids": ["equip-456", "equip-789", "equip-101"],
        "priority": "high"
    }
    
    response = client.post(
        "/api/v1/voltmetrics/batch",
        json=payload,
        headers={"Authorization": "Bearer mocktoken"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["facility_id"] == "facility-123"
    assert data["status"] == "submitted"
    assert data["total_items"] == 3 