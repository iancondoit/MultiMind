# MasterBus Data Models

Version: 0.2.0
Created: 2025-05-20
Status: Completed

## Overview

This document outlines the data models used within MasterBus and the mapping between Condoit data structures and ThreatMap requirements. The models represent the transformation of electrical infrastructure data into risk assessment information.

## Core Entities

### Facility

The Facility model represents a physical location containing electrical infrastructure.

#### Data Fields

| Field Name | Type | Description | Source |
|------------|------|-------------|--------|
| id | String | Unique identifier | Condoit facility ID |
| name | String | Facility name | Condoit facility name |
| location | Object | Physical location details | Condoit facility location |
| created_at | DateTime | Creation timestamp | Condoit facility creation time |
| last_updated | DateTime | Last update timestamp | MasterBus calculation |
| risk_summary | Object | Aggregated risk metrics | MasterBus calculation |

### Equipment

The Equipment model represents an individual piece of electrical infrastructure.

#### Data Fields

| Field Name | Type | Description | Source |
|------------|------|-------------|--------|
| id | String | Unique identifier | Condoit equipment ID |
| name | String | Equipment name | Condoit equipment name |
| type | String | Equipment type (panel, transformer, etc.) | Condoit equipment type |
| manufacturer | String | Equipment manufacturer | Condoit equipment details |
| model | String | Equipment model | Condoit equipment details |
| serial_number | String | Serial number | Condoit equipment details |
| installation_date | Date | When equipment was installed | Condoit equipment details |
| location | Object | Physical location within facility | Condoit equipment location |
| specifications | Object | Technical specifications | Condoit equipment specs |
| photos | Array | Photo references | Condoit photos |
| risk_assessment | Object | Risk scoring information | MasterBus calculation |
| compliance | Object | NFPA compliance information | MasterBus calculation |
| created_at | DateTime | Creation timestamp | Condoit equipment creation time |
| last_updated | DateTime | Last update timestamp | MasterBus calculation |

### Risk Assessment

The Risk Assessment model represents the calculated risk level for equipment or facilities.

#### Data Fields

| Field Name | Type | Description | Source |
|------------|------|-------------|--------|
| risk_level | String | Overall risk level (high, medium, low) | MasterBus calculation |
| risk_score | Number | Numerical risk score (0-100) | MasterBus calculation |
| risk_factors | Array | Specific risk factors | MasterBus calculation |
| last_assessed | DateTime | When risk was last calculated | MasterBus calculation |

### Compliance

The Compliance model represents adherence to NFPA 70B and 70E standards.

#### Data Fields

| Field Name | Type | Description | Source |
|------------|------|-------------|--------|
| nfpa_70b | Object | Preventative maintenance compliance | MasterBus calculation |
| nfpa_70e | Object | Arc flash analysis compliance | MasterBus calculation |
| overall_compliance | Number | Combined compliance percentage | MasterBus calculation |
| last_assessed | DateTime | When compliance was last calculated | MasterBus calculation |

## Transformation Logic

### Risk Level Calculation

Risk levels are calculated based on multiple factors including:

1. **Age Factor**
   - Equipment older than 40 years: High risk
   - Equipment 20-40 years old: Medium risk
   - Equipment <20 years old: Low risk

2. **Maintenance Factor**
   - Last maintenance exceeds NFPA 70B schedule by >1 year: High risk
   - Last maintenance within 1 year of NFPA 70B schedule: Medium risk
   - Maintenance up to date: Low risk

3. **Conductor Type Factor**
   - Aluminum to copper connections: High risk
   - Aluminum conductors: Medium risk
   - Copper conductors: Low risk

4. **Loading Factor**
   - >90% of rated capacity: High risk
   - 75-90% of rated capacity: Medium risk
   - <75% of rated capacity: Low risk

The overall risk score is calculated using weighted averages of these factors, with adjustments based on the specific equipment type and environment.

### Compliance Calculation

NFPA 70B compliance is calculated based on:
1. Adherence to maintenance schedules
2. Documentation completeness
3. Testing results

NFPA 70E compliance is calculated based on:
1. Arc flash labeling
2. Proper PPE requirements
3. Up-to-date arc flash studies

## Data Flow Mapping

### Condoit → MasterBus

| Condoit Data | MasterBus Model | Transformation |
|--------------|-----------------|----------------|
| Facility records | Facility | Direct mapping with added risk summaries |
| Equipment records | Equipment | Direct mapping with added risk assessment |
| Maintenance records | Compliance.nfpa_70b | Calculate compliance percentage from maintenance history |
| Arc flash studies | Compliance.nfpa_70e | Calculate compliance percentage from arc flash data |
| Equipment specifications | Risk Assessment | Calculate risk factors from specifications |
| Photos | Equipment.photos | Reference mapping |

### MasterBus → ThreatMap

| MasterBus Model | ThreatMap Requirement | Transformation |
|-----------------|------------------------|----------------|
| Facility with risk_summary | Facility dashboard data | JSON formatting |
| Equipment with risk_assessment | Equipment detail data | JSON formatting |
| Compliance | Compliance overview charts | Aggregate and format as JSON |
| Risk Assessment | Risk visualization data | Format as JSON with visualization metadata |

## Implementation Considerations

1. **Caching Strategy**
   - Risk calculations are computationally expensive and should be cached
   - Cache invalidation needed when underlying Condoit data changes

2. **Batch Processing**
   - Risk calculations for entire facilities should be processed in batches
   - Consider background processing for large datasets

3. **Validation Rules**
   - Enforce data type validation on all Condoit inputs
   - Implement bounds checking on calculated risk scores

## Next Steps

1. Analyze Condoit data structures to refine source mappings
2. Review ThreatMap requirements to validate transformation outputs
3. Develop risk calculation algorithms with domain experts
4. Create detailed schema definitions for all models 