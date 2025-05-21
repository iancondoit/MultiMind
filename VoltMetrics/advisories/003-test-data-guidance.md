# Advisory: Test Dataset Creation for Algorithm Validation

Version: 0.1.0
Status: ANSWERED
Project: VoltMetrics
Created: 2025-05-22
Last Updated: 2025-05-22

## Question

How should we create test datasets for algorithm validation without access to real electrical infrastructure data?

## Context

The VoltMetrics status report identified "Require dataset for algorithm testing and validation" as a blocker. We need guidance on creating realistic test data that can validate our risk algorithms.

## Response

### Test Data Approach

Since you don't have access to a complete real-world dataset yet, you should adopt a multi-layered approach to test data:

1. **Synthetic Base Dataset**
   - Create a core synthetic dataset that follows realistic distributions
   - Generate approximately 500-1000 equipment items across 5-10 facilities
   - Ensure broad coverage of equipment types and risk factors

2. **Scenario-Based Test Cases**
   - Develop specific test cases for edge conditions and known risk scenarios
   - Include examples from electrical engineering literature where available
   - Create "golden test cases" with pre-calculated expected results

3. **Validation Framework**
   - Implement property-based tests that verify mathematical properties
   - Create invariant checks that must hold true regardless of inputs
   - Develop sensitivity analysis to verify algorithm behavior

### Synthetic Dataset Generation

#### 1. Facility Generation

Generate 5-10 facilities with these characteristics:

```python
{
  "id": "facility-{id}",
  "name": "Facility {id}",
  "location": "{city}, {state}",
  "coordinates": {
    "lat": float,  # Random within continental US
    "lng": float
  },
  "year_built": int,  # Range from 1960-2020
  "size_sqft": int,  # Range from 10,000 to 500,000
  "occupancy_type": str,  # ["commercial", "industrial", "healthcare", "education"]
  "environment": {
    "humidity_average": int,  # Range from 30 to 80
    "temperature_average": int,  # Range from 65 to 85
    "outdoor_exposure": str  # ["minimal", "moderate", "severe"]
  }
}
```

#### 2. Equipment Generation

For each facility, generate 50-200 equipment items distributed across these types:

- **Panels**: 30-40%
- **Transformers**: 5-10%
- **Switchboards**: 5-10%
- **Breakers**: 30-40%
- **Other equipment**: 10-20%

#### 3. Risk Factor Distribution

Distribute risk factors following these rules to ensure realistic data:

- **Age Distribution**: 
  - Normal distribution centered around (current_year - facility_year_built)/2
  - Add some outliers with recent replacements and very old equipment

- **Material Factors**:
  - Aluminum conductors more common in older equipment (pre-1980)
  - Connection types correlating with age (older=more crimped)
  - Mix of conductor sizes with some undersized based on equipment load

- **Maintenance History**:
  - Correlation between maintenance frequency and equipment age/importance
  - Some equipment with no maintenance history
  - Most with irregular maintenance

- **Environmental Factors**:
  - Correlate with facility environment
  - Add location-specific modifiers

#### 4. Risk Correlation Factors

To ensure realistic data, implement these correlations:

- Older equipment should correlate with:
  - Higher corrosion levels
  - More aluminum conductors
  - Less maintenance
  - More documented issues

- Higher humidity environments should correlate with:
  - Increased corrosion
  - More maintenance requirements

### Scenario-Based Test Cases

Create these specific test scenarios with known outcomes:

1. **Critical Risk Scenarios**:
   - 50+ year-old panel with aluminum conductors and no maintenance
   - Transformer operating at >90% capacity with cooling issues
   - Equipment with visible corrosion and loose connections

2. **Medium Risk Scenarios**:
   - 25-year-old equipment with regular maintenance
   - Equipment with minor issues but good maintenance

3. **Low Risk Scenarios**:
   - New equipment (<5 years) with proper installation
   - Recently serviced equipment with no issues

### Data Generation Code

Begin with a data generator class structure like this:

```python
class TestDataGenerator:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        
    def generate_facilities(self, count=8):
        # Generate facility data
        
    def generate_equipment(self, facility_id, count=100):
        # Generate equipment for a facility
        
    def generate_maintenance_records(self, equipment_id, count=5):
        # Generate maintenance history
        
    def generate_full_dataset(self, facility_count=8):
        # Generate complete dataset
        
    def generate_test_scenarios(self):
        # Generate specific test cases with known outcomes
```

### Output Format

Generate the test data in a format compatible with your API specifications, using JSON that matches your planned data models:

```json
{
  "facilities": [...],
  "equipment": [...],
  "maintenance_records": [...]
}
```

### Validation Approach

For each test scenario:

1. Calculate expected risk scores manually
2. Compare algorithm output to expected values
3. Verify facility aggregation correctly reflects equipment risks
4. Test the same scenarios with variations to ensure stability

### Next Steps

1. Implement the data generator as a standalone module
2. Create a configurable parameter set for generating different distributions
3. Develop validation scripts to verify statistical properties of the generated data
4. Create a test harness that can run multiple validation scenarios

This approach will provide sufficient test data to validate your algorithms while waiting for access to real-world datasets.

## Resolution

[To be filled by VoltMetrics team after implementation] 