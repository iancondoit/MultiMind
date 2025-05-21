# Advisory: Electrical Risk Assessment Factors

Version: 0.1.0
Status: ANSWERED
Project: VoltMetrics
Created: 2025-05-22
Last Updated: 2025-05-22

## Question

What are the key risk factors that should be considered for electrical equipment risk assessment?

## Context

Both the MasterBus and VoltMetrics status reports identified the need for detailed information about electrical risk assessment factors. This information is critical for developing the risk calculation algorithms in VoltMetrics.

## Response

### Key Risk Factors for Electrical Equipment

Based on industry standards and electrical engineering best practices, here are the key risk factors to incorporate into your risk assessment algorithms:

1. **Age-Related Factors**
   - **Equipment Age**: Use a non-linear scale where risk increases more rapidly after 75% of expected service life
   - **Expected Service Life**: Typical values by equipment type:
     - Panels: 30-40 years
     - Transformers: 25-30 years
     - Switchgear: 30-35 years
     - Breakers: 20-25 years
   - **Technology Generation**: Equipment using obsolete technology has higher risk
   - **Part Availability**: Equipment with discontinued parts has higher risk

2. **Material-Related Factors**
   - **Aluminum Conductors**: Higher risk, especially in older installations (pre-1975)
   - **Connection Types**: Crimped connections are higher risk than bolted
   - **Conductor Sizing**: Undersized conductors relative to current load
   - **Insulation Type and Condition**: Deteriorated or outdated insulation
   - **Bus Material**: Tin-plated vs. bare copper vs. aluminum

3. **Environmental Factors**
   - **Humidity**: Accelerates corrosion (>65% RH is problematic)
   - **Temperature**: Both high (>85°F) and cycling temperatures increase risk
   - **Exposure**: Outdoor, damp, or corrosive environments
   - **Contaminants**: Dust, chemicals, salt air
   - **Ventilation**: Poor ventilation increases operational temperature

4. **Maintenance Factors**
   - **Inspection Frequency**: Time since last inspection
   - **Maintenance Quality**: Thoroughness of previous maintenance
   - **Documented Issues**: Number and severity of noted problems
   - **Repair History**: Frequency and types of repairs needed
   - **Thermal Scanning**: Results from infrared scanning

5. **Operational Factors**
   - **Loading**: Percentage of rated capacity being used
   - **Harmonics**: Presence and level of harmonic distortion
   - **Power Factor**: Poor power factor increases heating
   - **Cycling**: Frequent on-off cycles increase wear
   - **Voltage Stability**: Frequent sags or surges

6. **Visual/Physical Conditions**
   - **Corrosion**: Visible rust or corrosion on components
   - **Physical Damage**: Dents, cracks, or other damage
   - **Heat Discoloration**: Darkening around connections
   - **Loose Parts**: Evidence of vibration or loosening
   - **Noise**: Unusual sounds during operation

### Risk Factor Weighting

For your algorithm development, use these suggested weightings as a starting point:

| Risk Category         | Weight | Justification                                     |
|-----------------------|--------|---------------------------------------------------|
| Age-Related           | 35%    | Primary predictor of equipment failure            |
| Material-Related      | 20%    | Fundamental to equipment safety                   |
| Maintenance Factors   | 20%    | Can mitigate other risks when properly maintained |
| Environmental Factors | 10%    | Accelerates deterioration of components           |
| Operational Factors   | 10%    | Impacts rate of wear and deterioration            |
| Visual Conditions     | 5%     | Indicators of existing problems                   |

These weights can be adjusted based on equipment type and empirical data as it becomes available.

### Risk Level Thresholds

For categorizing equipment risk levels, use these thresholds:

- **Low Risk**: 0-40
- **Medium Risk**: 41-70
- **High Risk**: 71-85
- **Critical Risk**: 86-100

## Resolution

[To be filled by VoltMetrics team after implementation] 