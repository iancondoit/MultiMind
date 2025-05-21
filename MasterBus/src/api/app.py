#!/usr/bin/env python3
"""
FastAPI application configuration for MasterBus API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from src.api.base import router as base_router
from src.api.facilities import router as facilities_router
from src.api.voltmetrics import router as voltmetrics_router
from src.api.webhooks import router as webhooks_router
from src.utils.errors import MasterBusException, ErrorHandler


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Create FastAPI app with metadata
    app = FastAPI(
        title="MasterBus API",
        description="API layer connecting Condoit and ThreatMap",
        version="0.2.0",  # Updated version for Phase 3
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, this should be restricted
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register exception handlers
    app.add_exception_handler(RequestValidationError, ErrorHandler.validation_exception_handler)
    app.add_exception_handler(MasterBusException, ErrorHandler.masterbus_exception_handler)
    
    # Include routers
    app.include_router(base_router)
    app.include_router(facilities_router, prefix="/api/v1")
    app.include_router(voltmetrics_router, prefix="/api/v1")
    app.include_router(webhooks_router)
    
    return app


app = create_application() 