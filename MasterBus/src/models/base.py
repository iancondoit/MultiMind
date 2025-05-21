#!/usr/bin/env python3
"""
Base models for MasterBus API.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class BaseModelWithTimestamps(BaseModel):
    """Base model with creation and update timestamps."""
    
    created_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="The timestamp when the record was created"
    )
    last_updated: Optional[datetime] = Field(
        default_factory=datetime.now,
        description="The timestamp when the record was last updated"
    )
    
    class Config:
        """Pydantic model configuration."""
        
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 