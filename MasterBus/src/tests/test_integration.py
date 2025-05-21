"""
Integration tests for MasterBus services.

Tests the interactions between different components of the system.
"""
import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from src.utils.cache import CacheManager
from src.utils.voltmetrics_client import VoltMetricsClient
from src.utils.data_transport import FacilityDataTransport
from src.utils.errors import NotFoundException, ServiceUnavailableException


# Fixture for mocked Redis
@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    with patch("redis.from_url") as mock_redis:
        # Create a mock Redis instance
        redis_instance = MagicMock()
        
        # Mock dictionary to store cache values
        redis_data = {}
        
        # Mock get method
        def mock_get(key):
            return redis_data.get(key)
        redis_instance.get.side_effect = mock_get
        
        # Mock setex method
        def mock_setex(key, expires, value):
            redis_data[key] = value
            return True
        redis_instance.setex.side_effect = mock_setex
        
        # Mock delete method
        def mock_delete(key):
            if key in redis_data:
                del redis_data[key]
                return 1
            return 0
        redis_instance.delete.side_effect = mock_delete
        
        # Mock time method
        redis_instance.time.return_value = [int(datetime.now().timestamp()), 0]
        
        # Return the mocked instance
        mock_redis.return_value = redis_instance
        yield redis_instance


# Fixture for mocked VoltMetrics client
@pytest.fixture
def mock_voltmetrics_client():
    """Create a mock VoltMetrics client."""
    with patch("src.utils.voltmetrics_client.VoltMetricsClient", autospec=True) as mock_client:
        # Create instance
        client_instance = mock_client.return_value
        
        # Mock submit_risk_calculation
        client_instance.submit_risk_calculation = AsyncMock(return_value={
            "job_id": "job-12345",
            "status": "SUBMITTED"
        })
        
        # Mock get_calculation_status
        client_instance.get_calculation_status = AsyncMock(return_value={
            "status": "COMPLETED",
            "resource_id": "test-equipment-123",
            "result": {
                "risk": {
                    "risk_level": "MEDIUM",
                    "risk_score": 65,
                    "details": {"age_factor": 70, "maintenance_factor": 60}
                },
                "compliance": {
                    "nfpa70b": {"score": 85, "issues": []},
                    "nfpa70e": {"score": 90, "issues": []}
                }
            }
        })
        
        # Mock get_equipment_risk
        client_instance.get_equipment_risk = AsyncMock(return_value={
            "risk_level": "MEDIUM",
            "risk_score": 65,
            "details": {"age_factor": 70, "maintenance_factor": 60}
        })
        
        # Mock get_facility_risk
        client_instance.get_facility_risk = AsyncMock(return_value={
            "overall_risk": "MEDIUM",
            "risk_score": 60,
            "details": {"average_equipment_risk": 65, "critical_count": 1}
        })
        
        # Mock get_nfpa70b_compliance
        client_instance.get_nfpa70b_compliance = AsyncMock(return_value={
            "compliance_score": 85,
            "issues": [],
            "assessment_date": "2025-01-15T12:00:00Z"
        })
        
        # Mock get_nfpa70e_compliance
        client_instance.get_nfpa70e_compliance = AsyncMock(return_value={
            "compliance_score": 90,
            "issues": [],
            "assessment_date": "2025-01-15T12:00:00Z"
        })
        
        # Mock wait_for_calculation
        client_instance.wait_for_calculation = AsyncMock(return_value={
            "status": "COMPLETED",
            "result": {
                "risk_level": "MEDIUM",
                "risk_score": 65
            }
        })
        
        yield client_instance


# Cache Manager Tests
@pytest.mark.asyncio
async def test_cache_manager(mock_redis):
    """Test the cache manager functionality."""
    # Create cache manager
    cache_manager = CacheManager()
    
    # Test setting data
    test_data = {"key": "value", "nested": {"test": 123}}
    success = cache_manager.set("test", "item-123", test_data)
    assert success is True
    
    # Test getting data
    retrieved = cache_manager.get("test", "item-123")
    assert retrieved == test_data
    
    # Test invalidation
    success = cache_manager.invalidate("test", "item-123")
    assert success is True
    
    # Verify data is gone
    retrieved = cache_manager.get("test", "item-123")
    assert retrieved is None
    
    # Test facility invalidation propagation
    cache_manager.set("risk", "facility:facility-123", {"score": 50})
    cache_manager.set("compliance:nfpa70b", "facility:facility-123", {"score": 80})
    
    # Invalidate facility
    cache_manager.invalidate_facility("facility-123")
    
    # Verify all related data is gone
    assert cache_manager.get("risk", "facility:facility-123") is None
    assert cache_manager.get("compliance:nfpa70b", "facility:facility-123") is None


# VoltMetrics Client Tests
@pytest.mark.asyncio
async def test_voltmetrics_client_submit_calculation(mock_voltmetrics_client):
    """Test submitting a calculation to VoltMetrics."""
    # Create a test client directly
    client = VoltMetricsClient()
    
    # Submit a calculation
    equipment_data = {
        "id": "test-equipment-123",
        "type": "both"
    }
    
    response = await client.submit_risk_calculation(equipment_data)
    
    # Verify the response
    assert response.get("job_id") == "job-12345"
    assert response.get("status") == "SUBMITTED"
    
    # Verify the client method was called correctly
    mock_voltmetrics_client.submit_risk_calculation.assert_called_once_with(equipment_data)


@pytest.mark.asyncio
async def test_voltmetrics_client_get_status(mock_voltmetrics_client):
    """Test getting calculation status from VoltMetrics."""
    # Create a test client directly
    client = VoltMetricsClient()
    
    # Get status
    job_id = "job-12345"
    response = await client.get_calculation_status(job_id)
    
    # Verify the response
    assert response.get("status") == "COMPLETED"
    assert "result" in response
    
    # Verify the client method was called correctly
    mock_voltmetrics_client.get_calculation_status.assert_called_once_with(job_id)


# Data Transport Tests
@pytest.mark.asyncio
async def test_facility_data_transport(mock_voltmetrics_client, mock_redis):
    """Test facility data transport service."""
    # Create transport with mocked clients
    transport = FacilityDataTransport(
        voltmetrics_client=mock_voltmetrics_client,
        cache_manager=CacheManager()
    )
    
    # Patch the _load_facility_data method to return test data
    with patch.object(
        transport, 
        '_load_facility_data', 
        new_callable=AsyncMock,
        return_value={
            "id": "facility-123",
            "name": "Test Facility",
            "address": "123 Test St",
            "contact_info": {"name": "Test User", "email": "test@example.com"},
            "equipment_count": 5
        }
    ):
        # Process a facility
        result = await transport.process_facility("facility-123")
        
        # Verify result structure
        assert result["id"] == "facility-123"
        assert result["name"] == "Test Facility"
        assert "risk" in result
        assert "compliance" in result
        assert "metadata" in result
        
        # Verify VoltMetrics calls
        mock_voltmetrics_client.get_facility_risk.assert_called_once()
        mock_voltmetrics_client.get_nfpa70b_compliance.assert_called_once()
        mock_voltmetrics_client.get_nfpa70e_compliance.assert_called_once()
        
        # Test cache by processing again
        mock_voltmetrics_client.reset_mock()
        result_cached = await transport.process_facility("facility-123")
        
        # Verify the cache was used
        assert "_cached" in result_cached
        assert result_cached["_cached"] is True
        
        # Verify no new VoltMetrics calls
        mock_voltmetrics_client.get_facility_risk.assert_not_called()
        mock_voltmetrics_client.get_nfpa70b_compliance.assert_not_called()
        mock_voltmetrics_client.get_nfpa70e_compliance.assert_not_called()


@pytest.mark.asyncio
async def test_equipment_data_transport(mock_voltmetrics_client, mock_redis):
    """Test equipment data transport service."""
    # Create transport with mocked clients
    transport = FacilityDataTransport(
        voltmetrics_client=mock_voltmetrics_client,
        cache_manager=CacheManager()
    )
    
    # Patch the _load_equipment_data method to return test data
    with patch.object(
        transport, 
        '_load_equipment_data', 
        new_callable=AsyncMock,
        return_value={
            "id": "equipment-123",
            "type": "SWITCHGEAR",
            "manufacturer": "TestMfg",
            "model": "Test-1000",
            "installation_date": "2020-01-01",
            "last_maintenance_date": "2023-06-15",
            "voltage_rating": 480,
            "current_rating": 800,
            "facility_id": "facility-123"
        }
    ):
        # Process equipment
        result = await transport.process_equipment("equipment-123")
        
        # Verify result structure
        assert result["id"] == "equipment-123"
        assert result["type"] == "SWITCHGEAR"
        assert "risk" in result
        assert "specifications" in result
        assert "dates" in result
        assert "metadata" in result
        
        # Verify VoltMetrics calls
        mock_voltmetrics_client.get_equipment_risk.assert_called_once()
        
        # Test cache by processing again
        mock_voltmetrics_client.reset_mock()
        result_cached = await transport.process_equipment("equipment-123")
        
        # Verify the cache was used
        assert "_cached" in result_cached
        assert result_cached["_cached"] is True
        
        # Verify no new VoltMetrics calls
        mock_voltmetrics_client.get_equipment_risk.assert_not_called()


@pytest.mark.asyncio
async def test_equipment_risk_calculation(mock_voltmetrics_client, mock_redis):
    """Test equipment risk calculation fallback."""
    # Create transport with mocked clients
    transport = FacilityDataTransport(
        voltmetrics_client=mock_voltmetrics_client,
        cache_manager=CacheManager()
    )
    
    # Setup get_equipment_risk to fail once, then pass on retry
    mock_voltmetrics_client.get_equipment_risk.side_effect = [
        NotFoundException("Risk data not found"),  # First call fails
        {"risk_level": "MEDIUM", "risk_score": 65}  # Second call succeeds
    ]
    
    # Patch _load_equipment_data
    with patch.object(
        transport, 
        '_load_equipment_data', 
        new_callable=AsyncMock,
        return_value={
            "id": "equipment-123",
            "type": "SWITCHGEAR",
            "facility_id": "facility-123"
        }
    ):
        # Process equipment - should trigger calculation when get_equipment_risk fails
        result = await transport.process_equipment("equipment-123")
        
        # Verify result and calls
        assert "risk" in result
        assert result["risk"]["level"] == "MEDIUM"
        
        # Verify calls - should have tried get_equipment_risk, then submit_risk_calculation
        assert mock_voltmetrics_client.get_equipment_risk.call_count == 1
        mock_voltmetrics_client.submit_risk_calculation.assert_called_once()
        mock_voltmetrics_client.wait_for_calculation.assert_called_once() 