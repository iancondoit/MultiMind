# VoltMetrics Directives

Version: 0.1.0

## Project Context

VoltMetrics is the specialized analysis engine component of the Condoit-MasterBus-ThreatMap architecture. It is responsible for the computationally intensive risk assessment, compliance evaluation, and trend analysis of electrical infrastructure data. VoltMetrics receives raw data from the MasterBus API, performs complex calculations, and returns processed risk metrics that are then served to ThreatMap via MasterBus.

## Current Tasks - Phase 1: Analysis Engine Architecture

1. **Define Risk Assessment Algorithms**
   - Research NFPA 70B requirements for maintenance compliance scoring
   - Research NFPA 70E requirements for arc flash compliance scoring
   - Create equipment age impact formulas for different equipment types
   - Develop conductor material risk formulas (especially aluminum)
   - Establish environment/humidity impact factors

2. **Compliance Calculation Models**
   - Design compliance percentage calculation methods
   - Develop maintenance schedule evaluation algorithms
   - Create time-based compliance decay models
   - Establish thresholds for "Compliant", "Warning", "Out of Compliance" status

3. **Facility-Level Aggregation**
   - Design equipment roll-up metrics for facility scoring
   - Develop weighting factors for different equipment types
   - Create "top threats" identification algorithms
   - Establish overall facility risk score formula

4. **Historical Trend Analysis**
   - Design time-series data models
   - Develop statistical methods for trend detection
   - Create forecasting algorithms for future risk prediction
   - Establish data retention and aggregation rules

5. **Engine Architecture**
   - Define input/output interfaces for the analysis engine
   - Design engine component structure and data flow
   - Create caching strategy for calculation results
   - Establish background processing for complex calculations

## Integration Points

- **Input**: Raw equipment data, maintenance records, and facility information from MasterBus
- **Output**: Calculated risk scores, compliance evaluations, and trend analysis returned to MasterBus

## Technical Requirements

- Process data for potentially hundreds of facilities and thousands of equipment items
- Update risk calculations near real-time for critical changes
- Provide batch processing capability for historical analysis
- Allow for algorithm versioning to track how risk scores have been calculated over time
- Support extensibility for new risk factors and compliance standards

## Next Steps

1. Research NFPA standards to inform risk calculation formulas
2. Consult with electrical domain experts to validate risk assessment approaches
3. Create technical architecture for the analysis engine
4. Develop core algorithms for risk scoring
5. Design caching and processing strategy
