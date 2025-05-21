"""
Main application module for VoltMetrics.

This module sets up the FastAPI application with all routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.data_endpoints import router as data_router
from src.api.risk_endpoints import router as risk_router

# Create FastAPI app
app = FastAPI(
    title="VoltMetrics API",
    description="API for electrical infrastructure risk assessment",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(data_router)
app.include_router(risk_router)

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint."""
    return {
        "name": "VoltMetrics API",
        "version": "0.1.0",
        "description": "API for electrical infrastructure risk assessment",
        "documentation": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"} 