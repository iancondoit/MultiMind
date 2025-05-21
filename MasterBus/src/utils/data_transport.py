"""
Data transport services for MasterBus.

Provides functionality to sync data between Condoit and ThreatMap.
"""
import logging
import asyncio
import json
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime

from src.utils.voltmetrics_client import VoltMetricsClient
from src.utils.errors import ValidationException, NotFoundException
from src.utils.validators import validate_facility_data, validate_equipment_data
from src.utils.cache import CacheManager

logger = logging.getLogger(__name__)

class FacilityDataTransport:
    """
    Handles transport and transformation of facility data.
    
    Responsible for:
    - Loading data from Condoit
    - Validating against models
    - Submitting to VoltMetrics for risk calculation
    - Transforming data for ThreatMap
    - Caching results
    """
    
    def __init__(
        self,
        voltmetrics_client: Optional[VoltMetricsClient] = None,
        cache_manager: Optional[CacheManager] = None
    ):
        """
        Initialize the facility data transport.
        
        Args:
            voltmetrics_client: Client for VoltMetrics API
            cache_manager: Manager for caching results
        """
        self.voltmetrics_client = voltmetrics_client or VoltMetricsClient()
        self.cache_manager = cache_manager or CacheManager()
    
    async def process_facility(self, facility_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Process a facility for ThreatMap consumption.
        
        Args:
            facility_id: ID of the facility to process
            force_refresh: Force refresh of data even if cached
            
        Returns:
            Processed facility data ready for ThreatMap
            
        Raises:
            NotFoundException: If facility not found
            ValidationException: If facility data is invalid
        """
        # Check cache first unless forced refresh
        if not force_refresh:
            cached_data = self.cache_manager.get("processed_facility", facility_id)
            if cached_data:
                logger.info(f"Retrieved facility {facility_id} from cache")
                # Add cache timestamp information
                cached_data["_cached"] = True
                return cached_data
        
        # Load and validate facility data
        facility_data = await self._load_facility_data(facility_id)
        facility, warnings = validate_facility_data(facility_data)
        
        # Log warnings but continue processing
        for warning in warnings:
            logger.warning(f"Facility {facility_id} data warning: {warning}")
        
        # Get risk assessment from VoltMetrics
        try:
            risk_data = await self.voltmetrics_client.get_facility_risk(facility_id)
        except Exception as e:
            logger.error(f"Failed to get risk data for facility {facility_id}: {str(e)}")
            # Continue with empty risk data
            risk_data = {"overall_risk": "UNKNOWN", "details": {}}
        
        # Get compliance metrics
        try:
            nfpa70b_data = await self.voltmetrics_client.get_nfpa70b_compliance(facility_id)
        except Exception as e:
            logger.error(f"Failed to get NFPA 70B data for facility {facility_id}: {str(e)}")
            nfpa70b_data = {"compliance_score": 0, "issues": []}
            
        try:
            nfpa70e_data = await self.voltmetrics_client.get_nfpa70e_compliance(facility_id)
        except Exception as e:
            logger.error(f"Failed to get NFPA 70E data for facility {facility_id}: {str(e)}")
            nfpa70e_data = {"compliance_score": 0, "issues": []}
        
        # Transform for ThreatMap
        result = self._transform_facility_for_threatmap(
            facility=facility,
            risk_data=risk_data,
            nfpa70b_data=nfpa70b_data,
            nfpa70e_data=nfpa70e_data
        )
        
        # Cache the result
        self.cache_manager.set(
            "processed_facility", 
            facility_id, 
            result,
            ttl=self.cache_manager.aggregate_ttl
        )
        
        return result
    
    async def process_equipment(self, equipment_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Process equipment data for ThreatMap consumption.
        
        Args:
            equipment_id: ID of the equipment to process
            force_refresh: Force refresh of data even if cached
            
        Returns:
            Processed equipment data ready for ThreatMap
            
        Raises:
            NotFoundException: If equipment not found
            ValidationException: If equipment data is invalid
        """
        # Check cache first unless forced refresh
        if not force_refresh:
            cached_data = self.cache_manager.get("processed_equipment", equipment_id)
            if cached_data:
                logger.info(f"Retrieved equipment {equipment_id} from cache")
                cached_data["_cached"] = True
                return cached_data
        
        # Load and validate equipment data
        equipment_data = await self._load_equipment_data(equipment_id)
        equipment, warnings = validate_equipment_data(equipment_data)
        
        # Log warnings but continue processing
        for warning in warnings:
            logger.warning(f"Equipment {equipment_id} data warning: {warning}")
        
        # Get or calculate risk assessment
        try:
            risk_data = await self._get_equipment_risk(equipment_id, equipment_data)
        except Exception as e:
            logger.error(f"Failed to get risk data for equipment {equipment_id}: {str(e)}")
            # Continue with empty risk data
            risk_data = {"risk_level": "UNKNOWN", "details": {}}
        
        # Transform for ThreatMap
        result = self._transform_equipment_for_threatmap(
            equipment=equipment,
            risk_data=risk_data
        )
        
        # Cache the result
        self.cache_manager.set("processed_equipment", equipment_id, result)
        
        return result
    
    async def _load_facility_data(self, facility_id: str) -> Dict[str, Any]:
        """
        Load facility data from Condoit.
        
        In a real implementation, this would interact with the Condoit API.
        For now, we'll simulate loading data from storage.
        
        Args:
            facility_id: Facility ID to load
            
        Returns:
            Raw facility data
            
        Raises:
            NotFoundException: If facility not found
        """
        # TODO: Replace with actual Condoit API interaction
        logger.info(f"Loading facility data for {facility_id} from Condoit")
        
        # Simulated data loading - would be replaced with actual API call
        # In a real implementation, this would call into Condoit's API
        try:
            # Placeholder for Condoit API call
            # In a real implementation, this would be:
            # async with httpx.AsyncClient() as client:
            #     response = await client.get(f"{condoit_api_url}/facilities/{facility_id}")
            #     if response.status_code == 404:
            #         raise NotFoundException(f"Facility {facility_id} not found")
            #     return response.json()
            
            # For now, simulate successful data retrieval
            return {
                "id": facility_id,
                "name": f"Facility {facility_id}",
                "address": "123 Main St, Anytown, USA",
                "contact_info": {"name": "John Doe", "email": "john@example.com"},
                "equipment_count": 5
            }
        except Exception as e:
            logger.error(f"Error loading facility {facility_id}: {str(e)}")
            raise NotFoundException(f"Facility {facility_id} not found")
    
    async def _load_equipment_data(self, equipment_id: str) -> Dict[str, Any]:
        """
        Load equipment data from Condoit.
        
        In a real implementation, this would interact with the Condoit API.
        For now, we'll simulate loading data from storage.
        
        Args:
            equipment_id: Equipment ID to load
            
        Returns:
            Raw equipment data
            
        Raises:
            NotFoundException: If equipment not found
        """
        # TODO: Replace with actual Condoit API interaction
        logger.info(f"Loading equipment data for {equipment_id} from Condoit")
        
        # Simulated data loading - would be replaced with actual API call
        try:
            # Placeholder for Condoit API call
            # In a real implementation, this would call into Condoit's API
            
            # For now, simulate successful data retrieval
            return {
                "id": equipment_id,
                "type": "SWITCHGEAR",
                "manufacturer": "PowerCo",
                "model": "SG-1000",
                "installation_date": "2020-01-15",
                "last_maintenance_date": "2023-03-10",
                "voltage_rating": 480,
                "current_rating": 800,
                "facility_id": "facility-123"  # Parent facility ID
            }
        except Exception as e:
            logger.error(f"Error loading equipment {equipment_id}: {str(e)}")
            raise NotFoundException(f"Equipment {equipment_id} not found")
    
    async def _get_equipment_risk(self, equipment_id: str, equipment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get risk assessment for equipment.
        
        Tries to get cached assessment first, then calls for calculation if needed.
        
        Args:
            equipment_id: Equipment ID
            equipment_data: Raw equipment data for calculation
            
        Returns:
            Risk assessment data
        """
        try:
            # Try to get cached risk assessment
            return await self.voltmetrics_client.get_equipment_risk(equipment_id)
        except NotFoundException:
            # Not found in cache, submit for calculation
            logger.info(f"No cached risk assessment for equipment {equipment_id}, calculating...")
            
            # Submit for calculation
            job = await self.voltmetrics_client.submit_risk_calculation(equipment_data)
            job_id = job.get("job_id")
            
            if not job_id:
                raise ValueError("No job ID returned from risk calculation submission")
                
            # Wait for completion
            result = await self.voltmetrics_client.wait_for_calculation(job_id)
            
            if result.get("status") == "COMPLETED":
                return result.get("result", {})
            else:
                raise Exception(f"Risk calculation failed: {result.get('error', 'Unknown error')}")
    
    def _transform_facility_for_threatmap(
        self,
        facility: Any,
        risk_data: Dict[str, Any],
        nfpa70b_data: Dict[str, Any],
        nfpa70e_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform facility data for ThreatMap consumption.
        
        Args:
            facility: Validated facility object
            risk_data: Risk assessment data
            nfpa70b_data: NFPA 70B compliance data
            nfpa70e_data: NFPA 70E compliance data
            
        Returns:
            Transformed data ready for ThreatMap
        """
        # Convert to ThreatMap expected format
        transformed = {
            "id": facility.id,
            "name": facility.name,
            "location": {
                "address": facility.address,
                # Additional location fields could be added here
            },
            "risk": {
                "level": risk_data.get("overall_risk", "UNKNOWN"),
                "score": risk_data.get("risk_score", 0),
                "factors": risk_data.get("details", {})
            },
            "compliance": {
                "nfpa70b": {
                    "score": nfpa70b_data.get("compliance_score", 0),
                    "issues": nfpa70b_data.get("issues", []),
                    "last_assessment": nfpa70b_data.get("assessment_date")
                },
                "nfpa70e": {
                    "score": nfpa70e_data.get("compliance_score", 0),
                    "issues": nfpa70e_data.get("issues", []),
                    "last_assessment": nfpa70e_data.get("assessment_date")
                }
            },
            "metadata": {
                "equipment_count": facility.equipment_count,
                "contact": facility.contact_info,
                "processed_at": datetime.utcnow().isoformat()
            }
        }
        
        return transformed
    
    def _transform_equipment_for_threatmap(
        self,
        equipment: Any,
        risk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform equipment data for ThreatMap consumption.
        
        Args:
            equipment: Validated equipment object
            risk_data: Risk assessment data
            
        Returns:
            Transformed data ready for ThreatMap
        """
        # Convert to ThreatMap expected format
        transformed = {
            "id": equipment.id,
            "type": equipment.type,
            "manufacturer": equipment.manufacturer,
            "model": equipment.model,
            "specifications": {
                "voltage_rating": equipment.voltage_rating,
                "current_rating": equipment.current_rating
            },
            "dates": {
                "installation": equipment.installation_date,
                "last_maintenance": equipment.last_maintenance_date
            },
            "risk": {
                "level": risk_data.get("risk_level", "UNKNOWN"),
                "score": risk_data.get("risk_score", 0),
                "factors": risk_data.get("details", {})
            },
            "facility_id": equipment.facility_id,
            "metadata": {
                "processed_at": datetime.utcnow().isoformat()
            }
        }
        
        return transformed 