"""
Test database setup for VoltMetrics.

This script creates the database schema and tests basic operations 
without relying on external packages.
"""

import logging
import os
from datetime import datetime

from src.db.database import Base, engine, SessionLocal
from src.models.facility import Facility
from src.models.equipment import Equipment, EquipmentType
from src.models.maintenance import MaintenanceRecord

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Create the database schema."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")


def create_test_data():
    """Create sample test data."""
    db = SessionLocal()
    try:
        # Create a sample facility
        facility = Facility(
            id="facility-001",
            name="Test Facility",
            location="Test Location, CA",
            coordinates={"lat": 37.7749, "lng": -122.4194},
            year_built=2000,
            size_sqft=50000,
            building_type="office",
            environment={
                "humidity_average": 50,
                "temperature_average": 72,
                "outdoor_exposure": "minimal"
            }
        )
        db.add(facility)
        db.commit()
        logger.info(f"Created facility: {facility.id}")
        
        # Create a sample equipment item
        equipment = Equipment(
            id="PANEL-001-001",
            name="Main Distribution Panel",
            type=EquipmentType.PANEL,
            facility_id=facility.id,
            installation_date=datetime(2005, 1, 15),
            location=f"{facility.id} - Floor 1 - Electrical Room",
            manufacturer="Square D",
            model="QO-1224",
            is_aluminum_conductor=False,
            humidity_exposure=45.0,
            temperature_exposure=75.0,
            loading_percentage=60,
            last_maintenance_date=datetime(2022, 5, 10),
            additional_data={
                "connection_type": "bolted",
                "circuit_count": 24
            }
        )
        db.add(equipment)
        db.commit()
        logger.info(f"Created equipment: {equipment.id}")
        
        # Create a sample maintenance record
        maintenance = MaintenanceRecord(
            id="maint-001",
            equipment_id=equipment.id,
            date=datetime(2022, 5, 10),
            type="Routine Inspection",
            technician="Tech-1234",
            findings="Equipment in good condition. No issues found."
        )
        db.add(maintenance)
        db.commit()
        logger.info(f"Created maintenance record: {maintenance.id}")
        
        logger.info("Test data created successfully.")
    except Exception as e:
        logger.error(f"Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()


def test_query():
    """Test basic database queries."""
    db = SessionLocal()
    try:
        # Query facilities
        facilities = db.query(Facility).all()
        logger.info(f"Found {len(facilities)} facilities")
        
        # Query equipment
        equipment = db.query(Equipment).all()
        logger.info(f"Found {len(equipment)} equipment items")
        
        # Query maintenance records
        records = db.query(MaintenanceRecord).all()
        logger.info(f"Found {len(records)} maintenance records")
        
        # Test a more complex query - get all equipment for a facility
        if facilities:
            facility_id = facilities[0].id
            facility_equipment = db.query(Equipment).filter(
                Equipment.facility_id == facility_id
            ).all()
            logger.info(f"Found {len(facility_equipment)} equipment items for facility {facility_id}")
        
        logger.info("Database queries completed successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    # Remove existing database file if it exists (for testing only)
    if os.path.exists("./voltmetrics.db"):
        os.remove("./voltmetrics.db")
        logger.info("Removed existing database file")
    
    # Initialize the database
    init_db()
    
    # Create test data
    create_test_data()
    
    # Test queries
    test_query() 