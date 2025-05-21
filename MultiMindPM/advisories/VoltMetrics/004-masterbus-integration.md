# Advisory: MasterBus Integration and Status Update

Version: 1.0.0
Status: ANSWERED
Project: VoltMetrics
Created: 2025-05-23
Last Updated: 2025-05-23

## Question

As we move into Phase 3, we need:
1. Detailed guidance on integration with MasterBus
2. Clarification on API contract requirements
3. Direction on how to handle asynchronous calculation notifications

## Context

Our Phase 3 directives require us to integrate with MasterBus, but we need more specific information about their API, authentication requirements, and the expected communication patterns between our systems.

## Response

### 1. MasterBus Integration Overview

For Phase 3, both teams are simultaneously developing integration capabilities. Here's how the integration will work:

#### Core Interaction Flow

1. **Data Transfer**:
   - MasterBus will call your API to submit equipment/facility data for risk calculation
   - You'll process calculations asynchronously for larger datasets
   - Results will be returned directly or via callback depending on complexity

2. **Authentication**:
   - MasterBus will use JWT tokens for authentication
   - You should validate these tokens using the shared secret provided in your `.env` file
   - All API requests will include an `Authorization: Bearer <token>` header

3. **Communication Patterns**:
   - **Synchronous**: Direct API calls for immediate calculations
   - **Asynchronous**: Job submission and webhook callbacks for complex calculations
   - **Polling**: Status endpoint for MasterBus to check calculation progress

#### API Contract

Your API should expose these endpoints:

```
POST /api/v1/calculations/risk
  - Accepts equipment/facility data for risk calculation
  - Returns a job ID for checking status

GET /api/v1/calculations/{job_id}
  - Returns the status and results of a calculation job

GET /api/v1/equipment/{equipment_id}/risk
  - Returns cached risk calculation for specific equipment

GET /api/v1/facilities/{facility_id}/risk
  - Returns aggregated risk data for a facility

GET /api/v1/compliance/nfpa70b/{facility_id}
  - Returns NFPA 70B compliance metrics

GET /api/v1/compliance/nfpa70e/{facility_id}
  - Returns NFPA 70E compliance metrics
```

#### Webhook Implementation

For asynchronous notifications:

1. MasterBus will register a webhook URL when submitting calculations:
   ```json
   {
     "data": { /* equipment/facility data */ },
     "callback_url": "https://masterbus-api.example.com/webhooks/calculation-complete"
   }
   ```

2. When calculation completes, post results to their callback URL:
   ```json
   {
     "job_id": "calculation-123",
     "status": "completed",
     "results_url": "/api/v1/calculations/calculation-123",
     "summary": {
       "risk_score": 78,
       "critical_issues": 3,
       "high_risk_equipment_count": 12
     }
   }
   ```

### 2. Status Report Update

Your status report appears to be from Phase 1, but you've now completed Phase 2. Please update your status report to reflect:

1. Completion of Phase 2 tasks:
   - Core calculation engine implementation
   - API endpoint development
   - Data model implementation
   - Testing framework establishment

2. Current blockers for Phase 3:
   - Any integration questions not addressed in this advisory
   - Specific technical challenges with NFPA compliance calculations
   - Performance concerns for time-series data storage

3. Next steps focused on Phase 3 implementation:
   - NFPA compliance evaluation
   - Facility-level aggregation
   - Historical analysis features
   - MasterBus integration
   - Performance optimization

### 3. Data Formats and Schema

For integration, use these standardized data structures:

#### Equipment Risk Calculation Response

```json
{
  "equipment_id": "panel-123",
  "equipment_type": "panel",
  "risk_score": 78,
  "risk_category": "high",
  "risk_factors": [
    {
      "factor": "age",
      "score": 25,
      "weight": 0.3,
      "details": "Equipment is 15 years old (75% of expected lifespan)"
    },
    {
      "factor": "inspection_status",
      "score": 15,
      "weight": 0.2,
      "details": "Last inspection was 14 months ago"
    },
    {
      "factor": "material_risk",
      "score": 20,
      "weight": 0.25,
      "details": "Aluminum conductors present"
    },
    {
      "factor": "environmental",
      "score": 18,
      "weight": 0.25,
      "details": "Elevated temperature environment"
    }
  ],
  "compliance": {
    "nfpa70b": {
      "status": "partial",
      "score": 65,
      "issues": [
        "Maintenance interval exceeds recommendation",
        "Missing thermographic inspection"
      ]
    },
    "nfpa70e": {
      "status": "compliant",
      "score": 90,
      "issues": []
    }
  },
  "calculated_at": "2025-05-23T14:30:00Z",
  "algorithm_version": "1.2.0"
}
```

#### Facility Risk Summary Response

```json
{
  "facility_id": "facility-456",
  "name": "Main Production Facility",
  "overall_risk_score": 72,
  "risk_category": "high",
  "equipment_counts": {
    "total": 85,
    "by_risk_category": {
      "critical": 3,
      "high": 12,
      "medium": 45,
      "low": 25
    },
    "by_type": {
      "panel": 24,
      "transformer": 8,
      "switchboard": 4,
      "breaker": 49
    }
  },
  "compliance": {
    "nfpa70b": {
      "status": "partial",
      "score": 68,
      "equipment_compliance": {
        "compliant": 54,
        "partial": 21,
        "non_compliant": 10
      }
    },
    "nfpa70e": {
      "status": "compliant",
      "score": 85,
      "equipment_compliance": {
        "compliant": 78,
        "partial": 7,
        "non_compliant": 0
      }
    }
  },
  "top_risks": [
    {
      "equipment_id": "panel-123",
      "name": "Main Distribution Panel",
      "risk_score": 92,
      "risk_category": "critical",
      "top_factor": "age"
    },
    {
      "equipment_id": "transformer-45",
      "name": "Production Line Transformer",
      "risk_score": 85,
      "risk_category": "high",
      "top_factor": "material_risk"
    }
  ],
  "historical_trend": {
    "periods": ["2025-03", "2025-04", "2025-05"],
    "scores": [68, 70, 72]
  },
  "calculated_at": "2025-05-23T14:35:00Z",
  "algorithm_version": "1.2.0"
}
```

## Resolution

The VoltMetrics team should:
1. Update the status report to reflect Phase 2 completion and current work
2. Implement the API contract as specified above
3. Begin coordination with the MasterBus team through weekly integration meetings
4. Focus initial implementation on the core calculation endpoints before moving to more advanced features 