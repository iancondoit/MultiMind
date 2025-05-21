#!/usr/bin/env python3
"""
Main entry point for the VoltMetrics application.

This script initializes the database and starts the API server.
"""

import os
import logging
import uvicorn
from pathlib import Path

from src.db.database import engine, Base
from src.api.app import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def init_db():
    """Initialize the database by creating all tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def main():
    """Main function to run the application."""
    # Initialize database if running as main script
    init_db()
    
    # Get host and port from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Log application startup
    logger.info(f"Starting VoltMetrics API on {host}:{port}")
    
    # Start the server
    uvicorn.run(
        "src.api.app:app",
        host=host,
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False,
    )


if __name__ == "__main__":
    main()
