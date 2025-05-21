"""
Webhook endpoints for MasterBus API.

Provides endpoints for receiving callbacks from external services.
"""
import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Request, Depends, HTTPException, status, Header
import json
import os
import hmac
import hashlib

from src.utils.cache import CacheManager

router = APIRouter(tags=["webhooks"])
logger = logging.getLogger(__name__)

# Initialize cache manager
cache_manager = CacheManager()

# Webhook security
WEBHOOK_SECRET = os.getenv("VOLTMETRICS_WEBHOOK_SECRET", "")


def verify_voltmetrics_signature(
    request_body: bytes,
    signature: Optional[str] = Header(None, alias="X-VoltMetrics-Signature")
) -> bool:
    """
    Verify the signature of a VoltMetrics webhook request.
    
    Args:
        request_body: Raw request body
        signature: Signature from request header
        
    Returns:
        True if signature is valid
    """
    if not WEBHOOK_SECRET or not signature:
        logger.warning("Webhook secret or signature missing, skipping verification")
        return False
        
    computed = hmac.new(
        WEBHOOK_SECRET.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed, signature)


@router.post("/api/v1/webhooks/voltmetrics/calculation")
async def voltmetrics_calculation_webhook(request: Request):
    """
    Webhook for receiving VoltMetrics calculation completion notifications.
    
    This endpoint is called by VoltMetrics when a risk calculation job completes.
    """
    # Get raw request body for signature verification
    body = await request.body()
    
    # Verify the request signature
    if WEBHOOK_SECRET and not verify_voltmetrics_signature(body, request.headers.get("X-VoltMetrics-Signature")):
        logger.warning("Invalid webhook signature received")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid signature")
    
    # Parse the JSON body
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON received in webhook")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON")
    
    # Process the webhook data
    job_id = data.get("job_id")
    calculation_type = data.get("type")
    status_value = data.get("status")
    resource_id = data.get("resource_id")  # equipment_id or facility_id
    resource_type = data.get("resource_type", "unknown")  # "equipment" or "facility"
    
    logger.info(
        f"Received webhook for {calculation_type} calculation {job_id} with status {status_value}",
        extra={
            "job_id": job_id,
            "calculation_type": calculation_type,
            "status": status_value,
            "resource_id": resource_id,
            "resource_type": resource_type
        }
    )
    
    if status_value == "COMPLETED" and resource_id and resource_type:
        # Result is available, invalidate cached data to force refresh on next request
        logger.info(f"Calculation completed, invalidating cache for {resource_type} {resource_id}")
        
        if resource_type == "equipment":
            # Invalidate equipment cache
            cache_manager.invalidate("processed_equipment", resource_id)
            cache_manager.invalidate("risk", f"equipment:{resource_id}")
            
            # If we have facility information, propagate invalidation
            facility_id = data.get("facility_id")
            if facility_id:
                logger.info(f"Propagating cache invalidation to facility {facility_id}")
                cache_manager.invalidate("processed_facility", facility_id)
                cache_manager.invalidate("risk", f"facility:{facility_id}")
                
        elif resource_type == "facility":
            # Invalidate facility cache
            cache_manager.invalidate("processed_facility", resource_id)
            cache_manager.invalidate("risk", f"facility:{resource_id}")
            
    return {"status": "acknowledged"} 