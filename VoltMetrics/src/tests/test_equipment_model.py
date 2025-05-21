import unittest
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.equipment import Equipment, EquipmentType


class TestEquipmentModel(unittest.TestCase):
    """Test cases for the Equipment model."""
    
    def test_equipment_creation(self):
        """Test creating an equipment instance with valid data."""
        equipment = Equipment(
            id="PANEL-001",
            name="Main Distribution Panel",
            type=EquipmentType.PANEL,
            installation_date=datetime(2010, 5, 15),
            last_maintenance_date=datetime(2023, 3, 10),
            location="Building A, Floor 1, Room 101",
            manufacturer="Square D",
            model="PowerPact",
            is_aluminum_conductor=False,
            humidity_exposure=45.5,
            temperature_exposure=75.2,
            loading_percentage=65.0
        )
        
        self.assertEqual(equipment.id, "PANEL-001")
        self.assertEqual(equipment.name, "Main Distribution Panel")
        self.assertEqual(equipment.type, EquipmentType.PANEL)
        self.assertEqual(equipment.installation_date, datetime(2010, 5, 15))
        self.assertEqual(equipment.manufacturer, "Square D")
        self.assertFalse(equipment.is_aluminum_conductor)
        
    def test_equipment_age_calculation(self):
        """Test the age calculation method."""
        # Equipment installed 10 years ago
        installation_date = datetime.now() - timedelta(days=365 * 10)
        equipment = Equipment(
            id="TRANS-001",
            name="Transformer 1",
            type=EquipmentType.TRANSFORMER,
            installation_date=installation_date,
            last_maintenance_date=datetime.now() - timedelta(days=180),
            location="Building B",
            manufacturer="GE",
            model="PowerTransformer",
            is_aluminum_conductor=True,
            humidity_exposure=50.0,
            temperature_exposure=80.0,
            loading_percentage=70.0
        )
        
        # Allow for small differences in calculation due to test timing
        self.assertAlmostEqual(equipment.age_years, 10.0, delta=0.1)
        
    def test_time_since_maintenance(self):
        """Test calculation of time since last maintenance."""
        equipment = Equipment(
            id="SWGR-001",
            name="Main Switchgear",
            type=EquipmentType.SWITCHGEAR,
            installation_date=datetime(2015, 1, 1),
            last_maintenance_date=datetime.now() - timedelta(days=365),
            location="Main Electrical Room",
            manufacturer="Eaton",
            model="PowerLine",
            is_aluminum_conductor=False,
            humidity_exposure=40.0,
            temperature_exposure=70.0,
            loading_percentage=55.0
        )
        
        # Allow for small differences in calculation due to test timing
        self.assertAlmostEqual(equipment.years_since_maintenance, 1.0, delta=0.1)
        
    def test_expected_service_life(self):
        """Test expected service life based on equipment type."""
        panel = Equipment(
            id="PANEL-002",
            name="Sub Panel 2",
            type=EquipmentType.PANEL,
            installation_date=datetime(2018, 6, 1),
            last_maintenance_date=datetime(2023, 6, 1),
            location="Building C",
            manufacturer="ABB",
            model="Distribution Panel",
            is_aluminum_conductor=False,
            humidity_exposure=30.0,
            temperature_exposure=68.0,
            loading_percentage=40.0
        )
        
        transformer = Equipment(
            id="TRANS-002",
            name="Transformer 2",
            type=EquipmentType.TRANSFORMER,
            installation_date=datetime(2020, 1, 1),
            last_maintenance_date=datetime(2023, 1, 1),
            location="Utility Yard",
            manufacturer="Siemens",
            model="Power Transformer",
            is_aluminum_conductor=False,
            humidity_exposure=60.0,
            temperature_exposure=85.0,
            loading_percentage=80.0
        )
        
        self.assertEqual(panel.expected_service_life, 35)  # PANEL: 30-40 years
        self.assertEqual(transformer.expected_service_life, 25)  # TRANSFORMER: 25-30 years


if __name__ == "__main__":
    unittest.main() 