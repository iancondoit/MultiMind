"""
Test data generator for VoltMetrics.

This module implements a data generator for creating synthetic test data
to validate the risk assessment algorithms. It follows the guidance provided
in advisory 003-test-data-guidance.md.
"""

import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import uuid

from models.equipment import EquipmentType


class TestDataGenerator:
    """
    Generator for synthetic test data used to validate risk assessment algorithms.
    
    Generates realistic data distributions for facilities, equipment,
    and maintenance records following industry patterns as specified
    in the test data guidance advisory.
    """
    
    # US Cities for facility locations
    CITIES = [
        ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"),
        ("Houston", "TX"), ("Phoenix", "AZ"), ("Philadelphia", "PA"),
        ("San Antonio", "TX"), ("San Diego", "CA"), ("Dallas", "TX"),
        ("San Jose", "CA"), ("Austin", "TX"), ("Jacksonville", "FL"),
        ("Fort Worth", "TX"), ("Columbus", "OH"), ("Charlotte", "NC"),
        ("San Francisco", "CA"), ("Indianapolis", "IN"), ("Seattle", "WA"),
        ("Denver", "CO"), ("Washington", "DC"), ("Boston", "MA"),
        ("Nashville", "TN"), ("Baltimore", "MD"), ("Oklahoma City", "OK"),
        ("Portland", "OR")
    ]
    
    # Manufacturer names
    MANUFACTURERS = [
        "Square D", "Eaton", "ABB", "Siemens", "General Electric",
        "Schneider Electric", "Westinghouse", "Cutler-Hammer", "Allen-Bradley",
        "Federal Pacific", "Zinsco", "ITE", "Murray"
    ]
    
    # Building/facility types
    FACILITY_TYPES = [
        "commercial", "industrial", "healthcare", "education", "data center",
        "hospitality", "retail", "warehouse", "manufacturing", "office"
    ]
    
    # Environment exposure levels
    EXPOSURE_LEVELS = ["minimal", "moderate", "severe"]
    
    def __init__(self, seed: int = 42):
        """
        Initialize the test data generator.
        
        Args:
            seed: Random seed for reproducible data generation
        """
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        random.seed(seed)
        self.current_year = datetime.now().year
        
    def generate_facilities(self, count: int = 8) -> List[Dict[str, Any]]:
        """
        Generate synthetic facility data.
        
        Args:
            count: Number of facilities to generate
            
        Returns:
            List of facility dictionaries
        """
        facilities = []
        
        for i in range(1, count + 1):
            # Select a random city
            city, state = random.choice(self.CITIES)
            
            # Generate random coordinates (approximate US bounds)
            lat = self.rng.uniform(24.0, 49.0)  # US latitude bounds
            lng = self.rng.uniform(-125.0, -66.0)  # US longitude bounds
            
            # Generate random year built (1960-2020)
            year_built = self.rng.integers(1960, 2021)
            
            # Generate random size
            size_sqft = int(self.rng.integers(10000, 500001))
            
            # Select a random facility type
            facility_type = random.choice(self.FACILITY_TYPES)
            
            # Generate environmental conditions
            humidity_average = int(self.rng.integers(30, 81))
            temperature_average = int(self.rng.integers(65, 86))
            outdoor_exposure = random.choice(self.EXPOSURE_LEVELS)
            
            facility = {
                "id": f"facility-{i:03d}",
                "name": f"{city} {facility_type.title()} Facility",
                "location": f"{city}, {state}",
                "coordinates": {
                    "lat": round(lat, 6),
                    "lng": round(lng, 6)
                },
                "year_built": year_built,
                "size_sqft": size_sqft,
                "building_type": facility_type,
                "environment": {
                    "humidity_average": humidity_average,
                    "temperature_average": temperature_average,
                    "outdoor_exposure": outdoor_exposure
                }
            }
            
            facilities.append(facility)
            
        return facilities
        
    def generate_equipment(self, facility: Dict[str, Any], count: int = 100) -> List[Dict[str, Any]]:
        """
        Generate synthetic equipment for a facility.
        
        Args:
            facility: Facility dictionary
            count: Number of equipment items to generate
            
        Returns:
            List of equipment dictionaries
        """
        equipment_list = []
        facility_id = facility["id"]
        facility_year = facility["year_built"]
        facility_age = self.current_year - facility_year
        
        # Environmental factors from facility
        humidity = facility["environment"]["humidity_average"]
        temperature = facility["environment"]["temperature_average"]
        exposure = facility["environment"]["outdoor_exposure"]
        
        # Determine equipment type distribution
        num_panels = int(count * self.rng.uniform(0.3, 0.4))
        num_transformers = int(count * self.rng.uniform(0.05, 0.1))
        num_switchgear = int(count * self.rng.uniform(0.05, 0.1))
        num_breakers = int(count * self.rng.uniform(0.3, 0.4))
        num_other = count - (num_panels + num_transformers + num_switchgear + num_breakers)
        
        # Generate each type of equipment
        equipment_list.extend(self._generate_equipment_by_type(facility_id, "PANEL", num_panels, 
                                    facility_year, facility_age, humidity, temperature, exposure))
        equipment_list.extend(self._generate_equipment_by_type(facility_id, "TRANSFORMER", num_transformers, 
                                    facility_year, facility_age, humidity, temperature, exposure))
        equipment_list.extend(self._generate_equipment_by_type(facility_id, "SWITCHGEAR", num_switchgear, 
                                    facility_year, facility_age, humidity, temperature, exposure))
        equipment_list.extend(self._generate_equipment_by_type(facility_id, "BREAKER", num_breakers, 
                                    facility_year, facility_age, humidity, temperature, exposure))
        equipment_list.extend(self._generate_equipment_by_type(facility_id, "OTHER", num_other, 
                                    facility_year, facility_age, humidity, temperature, exposure))
        
        return equipment_list
        
    def _generate_equipment_by_type(self, facility_id: str, equipment_type: str, count: int, 
                                  facility_year: int, facility_age: int, humidity: float, 
                                  temperature: float, exposure: str) -> List[Dict[str, Any]]:
        """
        Generate equipment of a specific type.
        
        Args:
            facility_id: Parent facility ID
            equipment_type: Type of equipment to generate
            count: Number of items to generate
            facility_year: Year the facility was built
            facility_age: Age of the facility in years
            humidity: Average humidity
            temperature: Average temperature
            exposure: Exposure level
            
        Returns:
            List of equipment dictionaries
        """
        items = []
        
        for i in range(count):
            # Generate a semi-random equipment ID
            eq_id = f"{equipment_type.upper()}-{facility_id[-3:]}-{i+1:03d}"
            
            # Select manufacturer
            manufacturer = random.choice(self.MANUFACTURERS)
            
            # Generate models based on manufacturer and equipment type
            model = f"{manufacturer[:3]}-{equipment_type[:3]}-{self.rng.integers(1000, 9999)}"
            
            # Determine equipment age - normal distribution around facility_age/2
            # with some newer replacements and some original equipment
            equipment_age = max(1, int(self.rng.normal(facility_age / 2, facility_age / 4)))
            
            # Cap equipment age to facility age (can't be older than the building)
            equipment_age = min(equipment_age, facility_age)
            
            # Calculate installation date
            installation_date = datetime.now() - timedelta(days=365 * equipment_age)
            
            # Determine if equipment has aluminum conductors (more common in older equipment)
            has_aluminum = False
            if equipment_age > 40:  # Pre-1980s equipment
                has_aluminum = self.rng.random() < 0.8  # 80% chance
            elif equipment_age > 30:
                has_aluminum = self.rng.random() < 0.5  # 50% chance
            elif equipment_age > 20:
                has_aluminum = self.rng.random() < 0.2  # 20% chance
            else:
                has_aluminum = self.rng.random() < 0.05  # 5% chance for newer equipment
            
            # Generate location within facility
            location = self._generate_location(facility_id, equipment_type)
            
            # Generate loading percentage (correlated to age somewhat)
            loading_pct = min(100, max(10, int(self.rng.normal(60, 15) + equipment_age / 3)))
            
            # Generate maintenance data (older equipment = less regular maintenance)
            last_maintenance_date = None
            years_since_maintenance = None
            if self.rng.random() > 0.1 + (equipment_age / 100):  # Chance of no maintenance increases with age
                # Generate maintenance date
                years_since = max(0.1, min(10, self.rng.normal(2, 1.5) * (1 + equipment_age / 30)))
                last_maintenance_date = datetime.now() - timedelta(days=int(365 * years_since))
                years_since_maintenance = years_since
            
            # Adjust environmental factors for specific location within building
            humidity_exposure = humidity + self.rng.normal(0, 5)
            temperature_exposure = temperature + self.rng.normal(0, 3)
            
            # Cap to realistic values
            humidity_exposure = max(10, min(100, humidity_exposure))
            temperature_exposure = max(50, min(110, temperature_exposure))
            
            # Generate additional equipment-specific data
            additional_data = self._generate_additional_data(equipment_type, equipment_age, 
                                                          exposure, has_aluminum)
            
            # Generate a human-friendly name
            name = self._generate_equipment_name(equipment_type, i, location)
            
            # Create the equipment dictionary
            equipment = {
                "id": eq_id,
                "name": name,
                "type": equipment_type,
                "installation_date": installation_date.isoformat(),
                "location": location,
                "manufacturer": manufacturer,
                "model": model,
                "is_aluminum_conductor": has_aluminum,
                "humidity_exposure": humidity_exposure,
                "temperature_exposure": temperature_exposure,
                "loading_percentage": loading_pct,
            }
            
            if last_maintenance_date:
                equipment["last_maintenance_date"] = last_maintenance_date.isoformat()
            
            if additional_data:
                equipment["additional_data"] = additional_data
                
            items.append(equipment)
            
        return items
        
    def _generate_location(self, facility_id: str, equipment_type: str) -> str:
        """Generate a realistic location string for equipment."""
        floors = ["Basement", "Ground Floor", "Floor 1", "Floor 2", "Floor 3", "Roof"]
        rooms = {
            "PANEL": ["Electrical Room", "Utility Closet", "Main Room", "Office", "Hallway"],
            "TRANSFORMER": ["Electrical Room", "Utility Yard", "Basement", "Transformer Vault"],
            "SWITCHGEAR": ["Main Electrical Room", "Utility Room", "Service Entrance"],
            "BREAKER": ["Electrical Room", "Panel Location", "Utility Closet"],
            "OTHER": ["Various Locations", "Utility Room", "Dedicated Room"]
        }
        
        floor = random.choice(floors)
        room = random.choice(rooms.get(equipment_type, ["Utility Room"]))
        
        return f"{facility_id} - {floor} - {room}"
    
    def _generate_equipment_name(self, equipment_type: str, index: int, location: str) -> str:
        """Generate a human-friendly name for the equipment."""
        prefixes = {
            "PANEL": ["Distribution Panel", "Power Panel", "Lighting Panel", "Branch Panel"],
            "TRANSFORMER": ["Transformer", "Step-down Transformer", "Isolation Transformer"],
            "SWITCHGEAR": ["Main Switchgear", "Distribution Switchgear", "Switchboard"],
            "BREAKER": ["Circuit Breaker", "Main Breaker", "Feeder Breaker"],
            "OTHER": ["UPS System", "Generator", "VFD", "Motor Controller"]
        }
        
        prefix = random.choice(prefixes.get(equipment_type, ["Equipment"]))
        location_short = location.split(" - ")[-1][:10]
        
        return f"{prefix} {location_short}-{index+1}"
    
    def _generate_additional_data(self, equipment_type: str, equipment_age: int, 
                              exposure: str, has_aluminum: bool) -> Dict[str, Any]:
        """Generate additional data fields based on equipment type and age."""
        additional_data = {}
        
        # Common fields based on age and exposure
        if equipment_age > 30:
            additional_data["visible_corrosion"] = self.rng.random() < 0.4 + (0.2 if exposure == "severe" else 0)
            additional_data["outdated_insulation"] = self.rng.random() < 0.7
        elif equipment_age > 20:
            additional_data["visible_corrosion"] = self.rng.random() < 0.2 + (0.1 if exposure == "severe" else 0)
            additional_data["outdated_insulation"] = self.rng.random() < 0.3
        
        # Add connection type info (more crimped connections in older equipment)
        if equipment_age > 40:
            additional_data["connection_type"] = "crimped" if self.rng.random() < 0.7 else "bolted"
        elif equipment_age > 20:
            additional_data["connection_type"] = "crimped" if self.rng.random() < 0.3 else "bolted"
        else:
            additional_data["connection_type"] = "crimped" if self.rng.random() < 0.1 else "bolted"
        
        # Add specific fields for very old equipment
        if equipment_age > 40:
            additional_data["physical_damage"] = self.rng.random() < 0.4
            additional_data["loose_parts"] = self.rng.random() < 0.5
            additional_data["heat_discoloration"] = self.rng.random() < 0.3
        
        # Add documented issues
        issue_count = 0
        if equipment_age > 30:
            issue_count = self.rng.integers(0, 5)
        elif equipment_age > 20:
            issue_count = self.rng.integers(0, 3)
        elif equipment_age > 10:
            issue_count = self.rng.integers(0, 2)
        
        if issue_count > 0:
            additional_data["documented_issues"] = issue_count
        
        # Type-specific data
        if equipment_type == "PANEL":
            if has_aluminum:
                additional_data["undersized_conductors"] = self.rng.random() < 0.5
        
        elif equipment_type == "TRANSFORMER":
            additional_data["cooling_type"] = random.choice(["dry", "oil", "air"])
            if equipment_age > 15:
                additional_data["unusual_noise"] = self.rng.random() < 0.3
        
        elif equipment_type == "BREAKER":
            additional_data["trip_tests"] = "passed" if self.rng.random() < 0.9 else "failed"
            if equipment_age > 25:
                additional_data["failed_inspection"] = self.rng.random() < 0.3
        
        return additional_data
    
    def generate_maintenance_records(self, equipment: Dict[str, Any], 
                                  count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate maintenance records for a piece of equipment.
        
        Args:
            equipment: Equipment data
            count: Number of records to generate, or None for auto-selection
            
        Returns:
            List of maintenance record dictionaries
        """
        # Parse installation date
        installation_date = datetime.fromisoformat(equipment["installation_date"])
        equipment_age = (datetime.now() - installation_date).days / 365.0
        
        # Determine reasonable number of maintenance records based on age
        if count is None:
            if equipment_age < 5:
                count = self.rng.integers(0, 3)
            elif equipment_age < 15:
                count = self.rng.integers(1, 5)
            else:
                count = self.rng.integers(2, 8)
        
        # Generate the records
        records = []
        
        # Distribution of maintenance dates
        # Most recent to installation date
        if "last_maintenance_date" in equipment:
            last_date = datetime.fromisoformat(equipment["last_maintenance_date"])
        else:
            # No maintenance record, generate a reasonable last date
            years_back = min(equipment_age - 0.5, self.rng.normal(3, 2))
            years_back = max(0.5, years_back)  # At least 6 months ago
            last_date = datetime.now() - timedelta(days=int(365 * years_back))
        
        # Spread maintenance records between installation and last maintenance
        available_time = (last_date - installation_date).days
        
        # Can't generate records if available time is too small
        if available_time < 30 or count == 0:
            return records
        
        # Generate the dates
        maintenance_offsets = sorted(self.rng.integers(0, available_time, size=count))
        maintenance_dates = [last_date - timedelta(days=int(offset)) for offset in maintenance_offsets]
        
        # Generate different types of maintenance
        maintenance_types = ["Routine Inspection", "Preventive Maintenance", "Repair", 
                           "Thermography", "Testing", "Emergency Service"]
        
        for i, date in enumerate(maintenance_dates):
            # Select a maintenance type with higher chance of routine inspection
            if i == 0 or self.rng.random() < 0.7:
                maintenance_type = maintenance_types[0]  # Routine Inspection
            else:
                maintenance_type = random.choice(maintenance_types[1:])
            
            # Generate findings based on equipment age at time of maintenance
            age_at_maintenance = (date - installation_date).days / 365.0
            findings = self._generate_maintenance_findings(equipment, age_at_maintenance, maintenance_type)
            
            record = {
                "id": str(uuid.uuid4()),
                "equipment_id": equipment["id"],
                "date": date.isoformat(),
                "type": maintenance_type,
                "technician": f"Tech-{self.rng.integers(1000, 9999)}",
                "findings": findings
            }
            
            records.append(record)
        
        return records
    
    def _generate_maintenance_findings(self, equipment: Dict[str, Any], 
                                   age_at_maintenance: float, 
                                   maintenance_type: str) -> str:
        """Generate maintenance findings based on equipment and maintenance type."""
        findings = []
        equipment_type = equipment["type"]
        has_aluminum = equipment.get("is_aluminum_conductor", False)
        additional_data = equipment.get("additional_data", {})
        
        # Common findings based on age
        if age_at_maintenance > 30:
            if self.rng.random() < 0.6:
                findings.append("Equipment shows significant age-related wear")
            if self.rng.random() < 0.5:
                findings.append("Recommend replacement planning")
        elif age_at_maintenance > 20:
            if self.rng.random() < 0.4:
                findings.append("Equipment shows moderate age-related wear")
            if self.rng.random() < 0.3:
                findings.append("Increased monitoring recommended")
        elif age_at_maintenance > 10:
            if self.rng.random() < 0.2:
                findings.append("Equipment shows early signs of age-related wear")
        else:
            if self.rng.random() < 0.8:
                findings.append("Equipment in good condition")
        
        # Findings for routine inspection
        if maintenance_type == "Routine Inspection":
            # Connection findings
            if has_aluminum:
                if self.rng.random() < 0.4:
                    findings.append("Aluminum conductor connections checked and tightened")
                if age_at_maintenance > 15 and self.rng.random() < 0.5:
                    findings.append("Evidence of oxidation on aluminum connections")
            
            # Corrosion findings based on environmental factors
            if additional_data.get("visible_corrosion", False):
                findings.append("Corrosion observed on equipment")
                if self.rng.random() < 0.7:
                    findings.append("Treatment applied to corroded areas")
        
        # Findings for thermal scanning
        elif maintenance_type == "Thermography":
            if equipment["loading_percentage"] > 80:
                if self.rng.random() < 0.6:
                    findings.append("Elevated temperatures detected at connection points")
                    additional_data["thermal_issues"] = True
            elif equipment["loading_percentage"] > 60:
                if self.rng.random() < 0.3:
                    findings.append("Slight temperature increases noted at high-load connections")
            else:
                findings.append("No thermal issues detected")
        
        # Findings for emergency service
        elif maintenance_type == "Emergency Service":
            issues = [
                "Equipment failure", 
                "Breaker trip", 
                "Overheating",
                "Unusual noise", 
                "Power quality issues",
                "Intermittent operation"
            ]
            findings.append(f"Emergency response for: {random.choice(issues)}")
            findings.append("Repairs completed and equipment returned to service")
        
        # Equipment-specific findings
        if equipment_type == "PANEL":
            if age_at_maintenance > 15 and self.rng.random() < 0.3:
                findings.append("Some breakers show signs of wear")
            
        elif equipment_type == "TRANSFORMER":
            if age_at_maintenance > 20 and self.rng.random() < 0.4:
                findings.append("Insulation resistance test performed")
            
        elif equipment_type == "BREAKER":
            if self.rng.random() < 0.7:
                findings.append("Trip mechanism tested")
                
        elif equipment_type == "SWITCHGEAR":
            if age_at_maintenance > 10 and self.rng.random() < 0.5:
                findings.append("Bus connections inspected and torqued")
        
        # If no findings, add a default
        if not findings:
            findings.append("No issues found")
            
        return ". ".join(findings)
    
    def generate_scenario_data(self, scenario_type: str) -> Dict[str, Any]:
        """
        Generate a specific test scenario with known risk characteristics.
        
        Args:
            scenario_type: Type of scenario to generate: "high_risk", "medium_risk", or "low_risk"
            
        Returns:
            Dictionary containing facility and equipment data for the scenario
        """
        # Base facility
        facility = {
            "id": f"scenario-{scenario_type}",
            "name": f"Test Facility - {scenario_type.replace('_', ' ').title()}",
            "location": "Test Location",
            "year_built": 1990,
            "size_sqft": 50000,
            "building_type": "test",
            "environment": {
                "humidity_average": 50,
                "temperature_average": 75,
                "outdoor_exposure": "moderate"
            }
        }
        
        # Generate equipment based on scenario type
        if scenario_type == "high_risk":
            # Create a facility with high-risk equipment
            facility["environment"]["humidity_average"] = 85
            facility["environment"]["temperature_average"] = 90
            facility["environment"]["outdoor_exposure"] = "severe"
            facility["year_built"] = 1970
            
            # Equipment will be generated with high risk factors
            equipment_count = 10
            
        elif scenario_type == "medium_risk":
            # Create a facility with medium-risk equipment
            facility["environment"]["humidity_average"] = 65
            facility["environment"]["temperature_average"] = 80
            facility["year_built"] = 1995
            
            # Equipment will be generated with medium risk factors
            equipment_count = 8
            
        else:  # low_risk
            # Create a facility with low-risk equipment
            facility["environment"]["humidity_average"] = 40
            facility["environment"]["temperature_average"] = 72
            facility["environment"]["outdoor_exposure"] = "minimal"
            facility["year_built"] = 2015
            
            # Equipment will be generated with low risk factors
            equipment_count = 5
        
        # Generate equipment for this scenario
        equipment = self.generate_equipment(facility, equipment_count)
        
        # For high-risk scenarios, override certain values to ensure high risk
        if scenario_type == "high_risk":
            for i, eq in enumerate(equipment):
                if i == 0:  # Make sure the first item is extremely high risk
                    # 50+ year old panel with aluminum and no maintenance
                    eq["type"] = "PANEL"
                    eq["installation_date"] = (datetime.now() - timedelta(days=365 * 51)).isoformat()
                    eq["is_aluminum_conductor"] = True
                    if "last_maintenance_date" in eq:
                        del eq["last_maintenance_date"]
                    eq["loading_percentage"] = 95
                    eq["additional_data"] = {
                        "visible_corrosion": True,
                        "physical_damage": True,
                        "loose_parts": True,
                        "heat_discoloration": True,
                        "connection_type": "crimped",
                        "documented_issues": 4,
                        "undersized_conductors": True,
                        "outdated_insulation": True
                    }
                elif i == 1:
                    # Transformer with cooling issues
                    eq["type"] = "TRANSFORMER"
                    eq["installation_date"] = (datetime.now() - timedelta(days=365 * 28)).isoformat()
                    eq["loading_percentage"] = 92
                    eq["additional_data"] = {
                        "cooling_type": "oil",
                        "unusual_noise": True,
                        "thermal_issues": True,
                        "documented_issues": 3
                    }
        
        # For low-risk scenarios, ensure very good equipment
        elif scenario_type == "low_risk":
            for eq in equipment:
                # Make all equipment newer with good maintenance
                install_age = self.rng.integers(1, 5)
                eq["installation_date"] = (datetime.now() - timedelta(days=365 * install_age)).isoformat()
                eq["last_maintenance_date"] = (datetime.now() - timedelta(days=90)).isoformat()
                eq["is_aluminum_conductor"] = False
                eq["loading_percentage"] = self.rng.integers(30, 60)
                eq["additional_data"] = {
                    "visible_corrosion": False,
                    "connection_type": "bolted"
                }
        
        # Generate maintenance records for each piece of equipment
        maintenance_records = []
        for eq in equipment:
            records = self.generate_maintenance_records(eq)
            maintenance_records.extend(records)
        
        return {
            "facility": facility,
            "equipment": equipment,
            "maintenance_records": maintenance_records
        }
    
    def generate_full_dataset(self, facility_count: int = 8) -> Dict[str, Any]:
        """
        Generate a complete dataset with facilities, equipment, and maintenance records.
        
        Args:
            facility_count: Number of facilities to generate
            
        Returns:
            Dictionary containing all generated data
        """
        facilities = self.generate_facilities(facility_count)
        
        all_equipment = []
        all_maintenance = []
        
        for facility in facilities:
            # Generate a number of equipment items based on facility size
            size_factor = facility["size_sqft"] / 50000  # Normalize to reference size
            equipment_count = int(self.rng.integers(50, 200) * size_factor)
            equipment_count = max(30, min(250, equipment_count))  # Reasonable bounds
            
            # Generate equipment for this facility
            equipment = self.generate_equipment(facility, equipment_count)
            all_equipment.extend(equipment)
            
            # Generate maintenance records for each piece of equipment
            for eq in equipment:
                records = self.generate_maintenance_records(eq)
                all_maintenance.extend(records)
        
        # Add scenario-based test cases
        scenarios = ["high_risk", "medium_risk", "low_risk"]
        for scenario in scenarios:
            scenario_data = self.generate_scenario_data(scenario)
            facilities.append(scenario_data["facility"])
            all_equipment.extend(scenario_data["equipment"])
            all_maintenance.extend(scenario_data["maintenance_records"])
        
        return {
            "facilities": facilities,
            "equipment": all_equipment,
            "maintenance_records": all_maintenance
        }
    
    def save_dataset(self, dataset: Dict[str, Any], filename: str) -> None:
        """
        Save the generated dataset to a JSON file.
        
        Args:
            dataset: Generated dataset
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"Dataset saved to {filename}")
        print(f"Generated {len(dataset['facilities'])} facilities")
        print(f"Generated {len(dataset['equipment'])} equipment items")
        print(f"Generated {len(dataset['maintenance_records'])} maintenance records")


def main():
    """Generate a test dataset and save it to a file."""
    generator = TestDataGenerator(seed=42)
    dataset = generator.generate_full_dataset()
    generator.save_dataset(dataset, "test_data.json")


if __name__ == "__main__":
    main() 