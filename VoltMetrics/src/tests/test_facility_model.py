import unittest
from datetime import datetime
import sys
import os

# Add src directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.facility import Facility
from models.equipment import Equipment, EquipmentType


class TestFacilityModel(unittest.TestCase):
    """Test cases for the Facility model."""
    
    def setUp(self):
        """Set up test fixtures for each test method."""
        # Create sample equipment items for test facility
        self.equipment1 = Equipment(
            id="PANEL-001",
            name="Main Panel",
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
        
        self.equipment2 = Equipment(
            id="TRANS-001",
            name="Transformer 1",
            type=EquipmentType.TRANSFORMER,
            installation_date=datetime(2015, 6, 20),
            last_maintenance_date=datetime(2023, 1, 15),
            location="Building A, Utility Room",
            manufacturer="GE",
            model="PowerTransformer",
            is_aluminum_conductor=True,
            humidity_exposure=50.0,
            temperature_exposure=80.0,
            loading_percentage=70.0
        )
        
        self.equipment3 = Equipment(
            id="SWGR-001",
            name="Main Switchgear",
            type=EquipmentType.SWITCHGEAR,
            installation_date=datetime(2005, 3, 10),
            last_maintenance_date=datetime(2022, 5, 5),
            location="Building A, Main Electrical Room",
            manufacturer="Eaton",
            model="PowerLine",
            is_aluminum_conductor=False,
            humidity_exposure=40.0,
            temperature_exposure=72.0,
            loading_percentage=55.0
        )
    
    def test_facility_creation(self):
        """Test creating a facility with equipment."""
        facility = Facility(
            id="FACILITY-001",
            name="Manufacturing Plant A",
            address="123 Industrial Pkwy, Anytown, US 12345",
            building_type="Manufacturing",
            square_footage=50000,
            year_built=1995,
            equipment=[]
        )
        
        self.assertEqual(facility.id, "FACILITY-001")
        self.assertEqual(facility.name, "Manufacturing Plant A")
        self.assertEqual(facility.building_type, "Manufacturing")
        self.assertEqual(len(facility.equipment), 0)
        
        # Add equipment to facility
        facility.add_equipment(self.equipment1)
        facility.add_equipment(self.equipment2)
        
        self.assertEqual(len(facility.equipment), 2)
        self.assertEqual(facility.equipment[0].id, "PANEL-001")
        self.assertEqual(facility.equipment[1].id, "TRANS-001")
    
    def test_facility_with_equipment(self):
        """Test creating a facility with equipment in constructor."""
        equipment_list = [self.equipment1, self.equipment2, self.equipment3]
        
        facility = Facility(
            id="FACILITY-002",
            name="Office Building B",
            address="456 Corporate Dr, Business City, US 54321",
            building_type="Office",
            square_footage=75000,
            year_built=2005,
            equipment=equipment_list
        )
        
        self.assertEqual(facility.id, "FACILITY-002")
        self.assertEqual(len(facility.equipment), 3)
        
    def test_facility_to_dict(self):
        """Test converting facility to dictionary."""
        facility = Facility(
            id="FACILITY-003",
            name="Data Center C",
            address="789 Server Ln, Tech City, US 67890",
            building_type="Data Center",
            square_footage=30000,
            year_built=2015,
            equipment=[self.equipment1, self.equipment2]
        )
        
        facility_dict = facility.to_dict()
        
        self.assertEqual(facility_dict["id"], "FACILITY-003")
        self.assertEqual(facility_dict["name"], "Data Center C")
        self.assertEqual(facility_dict["building_type"], "Data Center")
        self.assertEqual(len(facility_dict["equipment"]), 2)
        self.assertEqual(facility_dict["equipment"][0]["id"], "PANEL-001")
        self.assertEqual(facility_dict["equipment"][1]["id"], "TRANS-001")
        
    def test_equipment_count_by_type(self):
        """Test counting equipment by type."""
        facility = Facility(
            id="FACILITY-004",
            name="Hospital D",
            address="101 Health Blvd, Wellness Town, US 13579",
            building_type="Healthcare",
            square_footage=100000,
            year_built=2000,
            equipment=[self.equipment1, self.equipment2, self.equipment3]
        )
        
        equipment_counts = facility.equipment_count_by_type()
        
        self.assertEqual(equipment_counts[EquipmentType.PANEL], 1)
        self.assertEqual(equipment_counts[EquipmentType.TRANSFORMER], 1)
        self.assertEqual(equipment_counts[EquipmentType.SWITCHGEAR], 1)
        self.assertEqual(equipment_counts.get(EquipmentType.BREAKER, 0), 0)
        

if __name__ == "__main__":
    unittest.main() 