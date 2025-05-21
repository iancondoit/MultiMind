#!/usr/bin/env python3
"""
VoltMetrics integration endpoints for MasterBus API.
"""
from fastapi import APIRouter, Depends, HTTPException, Body, Path, Query, BackgroundTasks
from typing import Dict, List, Optional, Any
import uuid
import logging
import asyncio
from datetime import datetime, timedelta

from src.api.base import get_current_user
from src.models.voltmetrics import (
    VoltMetricsCalculationRequest,
    VoltMetricsCalculationResponse,
    VoltMetricsBatchRequest,
    VoltMetricsBatchResponse
)
from src.utils.voltmetrics_client import VoltMetricsClient
from src.utils.errors import NotFoundException, ServiceUnavailableException, ValidationException
from src.utils.cache import CacheManager


# Create router for VoltMetrics endpoints
router = APIRouter(prefix="/voltmetrics", tags=["VoltMetrics"])
logger = logging.getLogger(__name__)

# Initialize clients
voltmetrics_client = VoltMetricsClient()
cache_manager = CacheManager()

# Store batch jobs in memory (would be in a database in production)
batch_jobs = {}


@router.post("/calculate", response_model=VoltMetricsCalculationResponse)
async def calculate_metrics(
    request: VoltMetricsCalculationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> VoltMetricsCalculationResponse:
    """
    Calculate risk and compliance metrics for a single equipment item.
    
    This endpoint submits a calculation request to VoltMetrics and returns
    the job information. The calculation is performed asynchronously.
    """
    logger.info(f"Received calculation request for equipment {request.equipment_id}")
    
    try:
        # Submit calculation to VoltMetrics
        response = await voltmetrics_client.submit_risk_calculation({
            "id": request.equipment_id,
            "type": request.calculation_type,
            "context": request.context or {}
        })
        
        # Get job ID from response
        job_id = response.get("job_id")
        if not job_id:
            raise Exception("No job ID returned from VoltMetrics")
            
        return VoltMetricsCalculationResponse(
            equipment_id=request.equipment_id,
            request_id=job_id,
            status="submitted",
            calculation_timestamp=datetime.now()
        )
    except ServiceUnavailableException as e:
        raise HTTPException(status_code=503, detail=e.message)
    except Exception as e:
        logger.error(f"Error submitting calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error submitting calculation: {str(e)}")


@router.get("/calculate/{job_id}", response_model=VoltMetricsCalculationResponse)
async def get_calculation_status(
    job_id: str = Path(..., description="Calculation job ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> VoltMetricsCalculationResponse:
    """
    Check the status of a calculation job.
    
    This endpoint queries VoltMetrics for the status of a previously
    submitted calculation job and returns the current status and results
    if the calculation is complete.
    """
    logger.info(f"Checking status of calculation job {job_id}")
    
    try:
        # Get job status from VoltMetrics
        response = await voltmetrics_client.get_calculation_status(job_id)
        
        # Extract information from response
        status = response.get("status", "UNKNOWN")
        equipment_id = response.get("resource_id")
        result = response.get("result", {})
        
        # Map to response model
        calculation_response = VoltMetricsCalculationResponse(
            equipment_id=equipment_id,
            request_id=job_id,
            status=status.lower(),
            calculation_timestamp=datetime.now()
        )
        
        # If complete, include results
        if status == "COMPLETED":
            # Extract risk and compliance metrics
            if "risk" in result:
                calculation_response.risk_metrics = result["risk"]
                
            if "compliance" in result:
                calculation_response.compliance_metrics = result["compliance"]
        
        return calculation_response
    except NotFoundException:
        raise HTTPException(status_code=404, detail=f"Calculation job {job_id} not found")
    except ServiceUnavailableException as e:
        raise HTTPException(status_code=503, detail=e.message)
    except Exception as e:
        logger.error(f"Error checking calculation status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking calculation: {str(e)}")


async def process_batch(batch_id: str, facility_id: str, equipment_ids: List[str]):
    """
    Process a batch of equipment calculations in the background.
    
    Args:
        batch_id: Batch job ID
        facility_id: Facility ID
        equipment_ids: List of equipment IDs to process
    """
    logger.info(f"Starting batch processing for batch {batch_id}, {len(equipment_ids)} items")
    
    total_items = len(equipment_ids)
    processed_items = 0
    
    # Update batch status
    batch_jobs[batch_id].update({
        "status": "processing",
        "total_items": total_items,
        "processed_items": processed_items,
        "completion_percentage": 0,
        "start_time": datetime.now()
    })
    
    # Process each equipment item
    for equipment_id in equipment_ids:
        try:
            # Submit calculation
            response = await voltmetrics_client.submit_risk_calculation({
                "id": equipment_id,
                "type": "both",
                "facility_id": facility_id
            })
            
            # Get job ID
            job_id = response.get("job_id")
            if job_id:
                # Wait for completion
                await voltmetrics_client.wait_for_calculation(job_id)
                
            # Update progress
            processed_items += 1
            batch_jobs[batch_id].update({
                "processed_items": processed_items,
                "completion_percentage": int((processed_items / total_items) * 100)
            })
            
        except Exception as e:
            logger.error(f"Error processing equipment {equipment_id} in batch {batch_id}: {str(e)}")
            # Continue with next item
    
    # Mark batch as complete
    completion_time = datetime.now()
    batch_jobs[batch_id].update({
        "status": "completed",
        "completion_time": completion_time,
        "processed_items": processed_items,
        "completion_percentage": int((processed_items / total_items) * 100)
    })
    
    logger.info(f"Batch {batch_id} completed. Processed {processed_items}/{total_items} items")
    
    # Invalidate facility cache to reflect new calculations
    cache_manager.invalidate_facility(facility_id)


@router.post("/batch", response_model=VoltMetricsBatchResponse)
async def create_batch_calculation(
    request: VoltMetricsBatchRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> VoltMetricsBatchResponse:
    """
    Create a batch calculation request for multiple equipment items.
    
    This endpoint starts an asynchronous batch job to calculate metrics
    for multiple equipment items and returns the batch job information.
    """
    # Generate a batch ID
    batch_id = f"batch-{uuid.uuid4()}"
    
    # Create batch job entry
    batch_jobs[batch_id] = {
        "batch_id": batch_id,
        "facility_id": request.facility_id,
        "status": "submitted",
        "total_items": len(request.equipment_ids),
        "processed_items": 0,
        "completion_percentage": 0,
        "submit_time": datetime.now(),
        "estimated_completion_time": datetime.now() + timedelta(minutes=len(request.equipment_ids) // 10 + 1)
    }
    
    # Start background processing
    background_tasks.add_task(
        process_batch, 
        batch_id=batch_id,
        facility_id=request.facility_id,
        equipment_ids=request.equipment_ids
    )
    
    return VoltMetricsBatchResponse(
        batch_id=batch_id,
        facility_id=request.facility_id,
        status="submitted",
        total_items=len(request.equipment_ids),
        processed_items=0,
        completion_percentage=0,
        estimated_completion_time=batch_jobs[batch_id]["estimated_completion_time"]
    )


@router.get("/batch/{batch_id}", response_model=VoltMetricsBatchResponse)
async def get_batch_status(
    batch_id: str = Path(..., description="Batch job ID"),
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> VoltMetricsBatchResponse:
    """
    Get the status of a batch calculation.
    
    This endpoint returns the current status of a previously submitted
    batch calculation job, including progress information.
    """
    # Check if batch exists
    if batch_id not in batch_jobs:
        raise HTTPException(status_code=404, detail=f"Batch job {batch_id} not found")
    
    # Get batch information
    batch = batch_jobs[batch_id]
    
    # Calculate remaining time if processing
    estimated_completion_time = batch.get("estimated_completion_time")
    if batch["status"] == "processing" and batch["completion_percentage"] > 0:
        # Recalculate based on current progress
        elapsed = datetime.now() - batch["start_time"]
        progress = batch["completion_percentage"] / 100
        if progress > 0:
            total_estimated = elapsed.total_seconds() / progress
            remaining = total_estimated - elapsed.total_seconds()
            estimated_completion_time = datetime.now() + timedelta(seconds=remaining)
    
    return VoltMetricsBatchResponse(
        batch_id=batch["batch_id"],
        facility_id=batch["facility_id"],
        status=batch["status"],
        total_items=batch["total_items"],
        processed_items=batch["processed_items"],
        completion_percentage=batch["completion_percentage"],
        estimated_completion_time=estimated_completion_time
    ) 