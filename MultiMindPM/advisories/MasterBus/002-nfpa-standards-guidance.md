# Advisory: NFPA Standards Interpretation for Compliance Metrics

Version: 0.1.0
Status: ANSWERED
Project: MasterBus
Created: 2025-05-22
Last Updated: 2025-05-22

## Question

What information do we need about NFPA 70B and 70E standards for compliance metrics in the API?

## Context

The MasterBus status report identified this as a blocker:
- Need more information on NFPA 70B/70E standards and their compliance requirements

## Response

### NFPA Standards Overview

The responsibility for detailed NFPA compliance calculations has been shifted to VoltMetrics. However, MasterBus still needs to understand the basics of these standards to properly transport and represent compliance data:

1. **NFPA 70B: Recommended Practice for Electrical Equipment Maintenance**
   - Focuses on preventive maintenance of electrical systems
   - Key compliance factors include:
     - Maintenance intervals by equipment type
     - Documentation of maintenance activities
     - Testing procedures and record-keeping

2. **NFPA 70E: Standard for Electrical Safety in the Workplace**
   - Focuses on safe work practices and arc flash protection
   - Key compliance factors include:
     - Arc flash hazard analysis (required every 5 years)
     - Electrical equipment labeling
     - Personal protective equipment (PPE) requirements

### MasterBus API Requirements

For MasterBus, you need to support the following compliance-related data structures in your API:

1. **Compliance Status Representation**:
   ```json
   {
     "nfpa_70b_compliance": {
       "status": "compliant|warning|non_compliant",
       "percentage": 85,
       "last_assessment_date": "2025-03-15",
       "next_assessment_due": "2026-03-15"
     },
     "nfpa_70e_compliance": {
       "status": "compliant|warning|non_compliant",
       "percentage": 92,
       "arc_flash_study_date": "2022-10-01",
       "arc_flash_study_due": "2027-10-01"
     }
   }
   ```

2. **Equipment-Level Compliance**:
   ```json
   {
     "maintenance_status": "up_to_date|due_soon|overdue",
     "last_service_date": "2024-11-15",
     "next_service_due": "2025-11-15",
     "arc_flash_label_present": true
   }
   ```

3. **Facility-Level Aggregation**:
   ```json
   {
     "equipment_count": 120,
     "compliant_equipment_count": 105,
     "overdue_equipment_count": 15,
     "compliance_percentage": 87.5
   }
   ```

4. **Detail levels for each endpoint**:
   - Summary (status only)
   - Standard (status + percentages)
   - Detailed (all compliance information)

The actual calculation algorithms will be implemented by VoltMetrics, and MasterBus will integrate with their API to retrieve these compliance metrics.

## Resolution

[To be filled by MasterBus team after implementation] 