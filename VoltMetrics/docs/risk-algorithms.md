# Risk Calculation Algorithms

Version: 0.1.0
Created: 2025-05-20
Status: Draft

## Overview

This document outlines the risk calculation algorithms, compliance evaluation methods, and aggregation techniques used by VoltMetrics. These algorithms convert raw electrical infrastructure data into quantifiable risk scores and compliance metrics.

## Equipment Risk Score Calculation

The equipment risk score (0-100) is calculated as a weighted combination of multiple risk factors:

### General Formula

```
EquipmentRiskScore = 
    (AgeRisk * W_age) + 
    (MaterialRisk * W_material) + 
    (MaintenanceRisk * W_maintenance) + 
    (EnvironmentalRisk * W_environmental) +
    (ConditionRisk * W_condition)
```

Where:
- Each risk component is normalized to a 0-100 scale
- W_x represents the weight of each factor (summing to 1)

### Age Risk

Age risk evaluates the relative age of equipment compared to its expected service life:

```
AgeRisk = (CurrentAge / ExpectedServiceLife) * 100
```

With adjustments:
- Cap at 100 for equipment beyond expected service life
- Apply equipment-specific multipliers (e.g., transformers age impact > panels)
- Adjust based on environment (e.g., outdoor equipment ages faster)

### Material Risk

Material risk focuses primarily on conductor material and connections:

```
MaterialRisk = BaseMaterialRisk + ConnectionRiskFactor
```

Where:
- Aluminum conductors have a BaseMaterialRisk of 60-80 depending on gauge
- Copper conductors have a BaseMaterialRisk of 20-40 depending on gauge
- ConnectionRiskFactor increases when joining dissimilar metals (Al-Cu connections)

### Maintenance Risk

Maintenance risk evaluates compliance with maintenance schedules and NFPA 70B:

```
MaintenanceRisk = BaseMaintenanceRisk * TimeFactorMultiplier
```

Where:
- BaseMaintenanceRisk is determined by the interval since last maintenance
- TimeFactorMultiplier increases exponentially after the recommended interval passes

### Environmental Risk

Environmental risk accounts for humidity, temperature, and physical conditions:

```
EnvironmentalRisk = 
    (HumidityFactor * W_humidity) + 
    (TemperatureFactor * W_temperature) + 
    (ExposureFactor * W_exposure)
```

With higher values for:
- High humidity environments (>70% relative humidity)
- Extreme temperatures (both high and low)
- Outdoor or harsh environment exposure

### Condition Risk

Condition risk evaluates physical observations from inspections:

```
ConditionRisk = 
    (CorrosionLevel * W_corrosion) + 
    (RustLevel * W_rust) + 
    (WearLevel * W_wear)
```

Based on rating scales (None, Minimal, Moderate, Severe) for each factor.

## Risk Rating Determination

Equipment risk scores map to qualitative ratings using the following thresholds:

- **Low Risk**: 0-40
- **Medium Risk**: 41-70
- **High Risk**: 71-85
- **Critical Risk**: 86-100

## Compliance Evaluation

### NFPA 70B Compliance

NFPA 70B compliance evaluates adherence to preventive maintenance schedules:

```
NFPA70BCompliance = 100 - (OverdueEquipment / TotalEquipment) * 100
```

Equipment is considered overdue when:
- Current date > (Last Maintenance Date + Recommended Interval)

Compliance status thresholds:
- **Compliant**: 90-100%
- **Warning**: 75-89%
- **Out of Compliance**: 0-74%

### NFPA 70E Compliance

NFPA 70E compliance evaluates arc flash study recency and labeling:

```
NFPA70ECompliance = 
    (StudyCompliance * 0.7) + 
    (LabelingCompliance * 0.3)
```

Where:
- StudyCompliance = 100 if arc flash study within 5 years, 0 otherwise
- LabelingCompliance = % of equipment with proper arc flash labels

## Facility Risk Aggregation

Facility risk score aggregates equipment risk with weighted importance:

```
FacilityRiskScore = 
    ∑(EquipmentRiskScore * EquipmentImportanceFactor) / 
    ∑(EquipmentImportanceFactor)
```

Equipment importance factors vary by type:
- Critical equipment (transformers, main switchgear): 3.0
- Standard distribution equipment (panels, disconnects): 1.0
- Supporting equipment (raceways, conductors): 0.5

## Critical Equipment Identification

Equipment is flagged as critical threat when:
1. Risk score is in Critical range (86-100), OR
2. Equipment is classified as critical AND risk score is in High range (71-85), OR
3. Equipment serves critical loads AND risk score is above 70

## Top Threat Selection

Top threats are selected by:
1. Filtering equipment to those with high or critical risk ratings
2. Sorting by risk score (highest first)
3. Taking the top N items, with a maximum of 5
4. Ensuring representation of different equipment types if possible

## Historical Trend Generation

Historical trends are calculated by:
1. Storing point-in-time risk scores and metrics on a monthly basis
2. Calculating month-over-month and year-over-year changes
3. Detecting significant trend changes (>10% in any direction)
4. Forecasting future values using exponential smoothing

## Algorithm Versioning

All algorithm formulas, weights, and thresholds are versioned:
1. Major version increments for formula changes
2. Minor version increments for weight or threshold adjustments
3. Full version history maintained for audit purposes
4. Result metadata includes algorithm version information

## Next Steps in Algorithm Development

1. Validate initial formulas with domain experts
2. Gather baseline data to calibrate weighting factors
3. Perform sensitivity analysis to validate model behavior
4. Develop equipment-specific variations of core formulas
5. Create simulation capability to test algorithm outputs 