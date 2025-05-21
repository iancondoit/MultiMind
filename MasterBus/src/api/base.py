#!/usr/bin/env python3
"""
Base router for MasterBus API.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Any

# This will be configured properly in a later implementation
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get the current user from the request.
    
    This is a placeholder implementation that will be replaced with a proper
    JWT-based authentication system as specified in the project requirements.
    """
    # For now, we just return a mock user
    # In a real implementation, this would validate the JWT token
    return {"user_id": "mock-user", "roles": ["admin"]}


# Base router for all API endpoints
router = APIRouter(prefix="/api/v1")


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    This endpoint doesn't require authentication and is used to check
    if the API is running.
    """
    return {"status": "ok", "version": "0.1.0"} 