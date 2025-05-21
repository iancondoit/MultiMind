#!/usr/bin/env python3
"""
VoltMetrics integration models for the MasterBus API.
"""
from datetime import datetime
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field

from src.models.base import BaseModelWithTimestamps


class VoltMetricsCalculationRequest(BaseModel):
    """Model representing a request to calculate risk metrics via VoltMetrics."""
    
    equipment_id: str = Field(
        ...,
        description="ID of the equipment to calculate metrics for"
    )
    calculation_type: Literal["risk", "compliance", "both"] = Field(
        ...,
        description="Type of calculation to perform"
    )
    equipment_data: Dict = Field(
        ...,
        description="Raw equipment data from Condoit"
    )
    include_history: bool = Field(
        False,
        description="Whether to include historical data in the response"
    )


class VoltMetricsCalculationResponse(BaseModelWithTimestamps):
    """Model representing a response from VoltMetrics calculation service."""
    
    equipment_id: str = Field(
        ...,
        description="ID of the equipment the metrics were calculated for"
    )
    request_id: str = Field(
        ...,
        description="Unique identifier for this calculation request"
    )
    status: Literal["completed", "pending", "failed"] = Field(
        ...,
        description="Status of the calculation"
    )
    risk_metrics: Optional[Dict] = Field(
        None,
        description="Risk metrics if requested"
    )
    compliance_metrics: Optional[Dict] = Field(
        None,
        description="Compliance metrics if requested"
    )
    calculation_timestamp: datetime = Field(
        default_factory=datetime.now,
        description="When the calculation was performed"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if calculation failed"
    )


class VoltMetricsBatchRequest(BaseModel):
    """Model representing a batch request for multiple calculations."""
    
    facility_id: str = Field(
        ...,
        description="ID of the facility to calculate metrics for"
    )
    calculation_type: Literal["risk", "compliance", "both"] = Field(
        ...,
        description="Type of calculation to perform"
    )
    equipment_ids: List[str] = Field(
        ...,
        description="IDs of equipment to calculate metrics for"
    )
    priority: Literal["high", "medium", "low"] = Field(
        "medium",
        description="Priority of this batch request"
    )
    callback_url: Optional[str] = Field(
        None,
        description="URL to call when batch processing is complete"
    )


class VoltMetricsBatchResponse(BaseModelWithTimestamps):
    """Model representing a response to a batch processing request."""
    
    batch_id: str = Field(
        ...,
        description="Unique identifier for this batch request"
    )
    facility_id: str = Field(
        ...,
        description="ID of the facility the metrics were calculated for"
    )
    status: Literal["submitted", "processing", "completed", "failed"] = Field(
        ...,
        description="Status of the batch calculation"
    )
    total_items: int = Field(
        ...,
        description="Total number of items in the batch"
    )
    processed_items: int = Field(
        0,
        description="Number of items processed so far"
    )
    completion_percentage: int = Field(
        0,
        description="Percentage of completion (0-100)"
    )
    estimated_completion_time: Optional[datetime] = Field(
        None,
        description="Estimated time when the batch will be complete"
    )
    results_url: Optional[str] = Field(
        None,
        description="URL to fetch results when processing is complete"
    ) 