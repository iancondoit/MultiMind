"""
VoltMetrics API client for MasterBus.

Implements integration with VoltMetrics calculation services.
"""
import json
import logging
import os
import asyncio
from typing import Any, Dict, List, Optional, Union, Tuple
import httpx
from datetime import datetime

from src.utils.errors import ServiceUnavailableException, ValidationException, NotFoundException

logger = logging.getLogger(__name__)

class VoltMetricsClient:
    """
    Client for interacting with VoltMetrics API.
    
    Handles calculation requests, job status checks, and result retrieval.
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize the VoltMetrics client.
        
        Args:
            base_url: VoltMetrics API base URL
            api_key: API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or os.getenv("VOLTMETRICS_API_URL", "https://api.voltmetrics.com")
        self.api_key = api_key or os.getenv("VOLTMETRICS_API_KEY")
        self.timeout = timeout
        
        if not self.api_key:
            logger.warning("VoltMetrics API key not provided. Authentication will fail.")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests.
        
        Returns:
            Dictionary of request headers
        """
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to VoltMetrics API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request payload
            
        Returns:
            Response data as dictionary
            
        Raises:
            ServiceUnavailableException: If service is unavailable
            ValidationException: If request validation fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url, headers=self._get_headers())
                elif method == "POST":
                    response = await client.post(url, headers=self._get_headers(), json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Handle different status codes
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    raise NotFoundException("Resource not found", details={"url": url})
                elif response.status_code == 422:
                    error_data = response.json().get("error", {})
                    raise ValidationException(
                        message=error_data.get("message", "Validation error"),
                        details=error_data.get("details", {})
                    )
                elif response.status_code >= 500:
                    raise ServiceUnavailableException(
                        message="VoltMetrics service is currently unavailable",
                        service_name="VoltMetrics"
                    )
                else:
                    error_data = response.json().get("error", {})
                    raise Exception(f"Unexpected error: {error_data.get('message', 'Unknown error')}")
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout while connecting to VoltMetrics API: {url}")
            raise ServiceUnavailableException(
                message="VoltMetrics service timed out",
                service_name="VoltMetrics"
            )
            
        except httpx.ConnectError:
            logger.error(f"Unable to connect to VoltMetrics API: {url}")
            raise ServiceUnavailableException(
                message="VoltMetrics service is unreachable",
                service_name="VoltMetrics"
            )
    
    async def submit_risk_calculation(self, equipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit equipment data for risk calculation.
        
        Args:
            equipment_data: Equipment data for calculation
            
        Returns:
            Dictionary containing job_id and status
        """
        endpoint = "/api/v1/calculations/risk"
        response = await self._make_request("POST", endpoint, data=equipment_data)
        
        # Log the submission
        logger.info(
            f"Submitted risk calculation for equipment {equipment_data.get('id', 'unknown')}",
            extra={"job_id": response.get("job_id")}
        )
        
        return response
    
    async def get_calculation_status(self, job_id: str) -> Dict[str, Any]:
        """
        Check the status of a calculation job.
        
        Args:
            job_id: Calculation job ID
            
        Returns:
            Dictionary containing job status and results if complete
        """
        endpoint = f"/api/v1/calculations/{job_id}"
        return await self._make_request("GET", endpoint)
    
    async def get_equipment_risk(self, equipment_id: str) -> Dict[str, Any]:
        """
        Get cached risk calculation for specific equipment.
        
        Args:
            equipment_id: Equipment ID
            
        Returns:
            Dictionary containing risk assessment data
        """
        endpoint = f"/api/v1/equipment/{equipment_id}/risk"
        return await self._make_request("GET", endpoint)
    
    async def get_facility_risk(self, facility_id: str) -> Dict[str, Any]:
        """
        Get aggregated risk data for a facility.
        
        Args:
            facility_id: Facility ID
            
        Returns:
            Dictionary containing aggregated risk data
        """
        endpoint = f"/api/v1/facilities/{facility_id}/risk"
        return await self._make_request("GET", endpoint)
    
    async def get_nfpa70b_compliance(self, facility_id: str) -> Dict[str, Any]:
        """
        Get NFPA 70B compliance metrics for a facility.
        
        Args:
            facility_id: Facility ID
            
        Returns:
            Dictionary containing compliance metrics
        """
        endpoint = f"/api/v1/compliance/nfpa70b/{facility_id}"
        return await self._make_request("GET", endpoint)
    
    async def get_nfpa70e_compliance(self, facility_id: str) -> Dict[str, Any]:
        """
        Get NFPA 70E compliance metrics for a facility.
        
        Args:
            facility_id: Facility ID
            
        Returns:
            Dictionary containing compliance metrics
        """
        endpoint = f"/api/v1/compliance/nfpa70e/{facility_id}"
        return await self._make_request("GET", endpoint)
    
    async def wait_for_calculation(self, job_id: str, max_tries: int = 10, delay_seconds: int = 2) -> Dict[str, Any]:
        """
        Poll for calculation results until job completes or max tries reached.
        
        Args:
            job_id: Calculation job ID
            max_tries: Maximum number of polling attempts
            delay_seconds: Seconds to wait between attempts
            
        Returns:
            Final job status response
            
        Raises:
            TimeoutError: If max tries reached without completion
        """
        attempts = 0
        
        while attempts < max_tries:
            response = await self.get_calculation_status(job_id)
            status = response.get("status")
            
            if status in ["COMPLETED", "FAILED"]:
                return response
                
            attempts += 1
            if attempts < max_tries:
                await asyncio.sleep(delay_seconds)
        
        raise TimeoutError(f"Calculation job {job_id} did not complete within the expected time") 