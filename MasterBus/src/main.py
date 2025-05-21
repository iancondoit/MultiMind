#!/usr/bin/env python3
"""
Main module for MasterBus API.
"""
import uvicorn
import os


def main():
    """Main entry point for the application."""
    # Get configuration from environment variables or use defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"Starting MasterBus API on {host}:{port}")
    
    # Run the FastAPI application using uvicorn
    uvicorn.run(
        "src.api.app:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )


if __name__ == "__main__":
    main()
