"""
Database initialization script for VoltMetrics.

This script initializes the database by creating all tables
defined in the SQLAlchemy models.
"""

import logging
from db.database import Base, engine
from models.facility import Facility
from models.equipment import Equipment, EquipmentType
from models.maintenance import MaintenanceRecord

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """
    Initialize the database by creating all tables.
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")


if __name__ == "__main__":
    init_db() 