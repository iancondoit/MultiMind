# VoltMetrics API Specification

Version: 0.1.0
Created: 2025-05-20
Status: Draft

## Overview

This document defines the API endpoints for the VoltMetrics analysis engine. These APIs enable MasterBus to send data for analysis and retrieve calculation results.

## Base URL

```
http://voltmetrics.internal/api/v1
```

## Authentication

All API requests require authentication using API keys.

```
X-API-Key: [api_key]
```

## Data Ingestion API

### POST /ingest/equipment

Submits electrical equipment data for risk analysis.

**Request:**
```json
{
  "equipment": [
    {
      "id": "equip-123",
      "type": "panel",
      "manufacturer": "Square D",
      "model": "QO-30",
      "install_date": "1980-03-15",
      "physical_data": {
        "voltage": "208/120V",
        "amperage": 200,
        "phases": 3,
        "mount_type": "surface",
        "enclosure_type": "NEMA 1",
        "slots": 30,
        "main_disconnect": true,
        "dimensions": {
          "height": 30,
          "width": 20,
          "depth": 6
        }
      },
      "location": {
        "facility_id": "facility-456",
        "building": "Building 1",
        "room": "Electrical Room 3",
        "coordinates": {
          "lat": 39.7834,
          "lng": -89.6520
        }
      },
      "conductors": [
        {
          "id": "cond-789",
          "material": "aluminum",
          "size": "2/0",
          "connection_type": "lug"
        }
      ],
      "condition": {
        "corrosion_level": "moderate",
        "rust_level": "minimal",
        "temperature": 68,
        "humidity": 65
      },
      "maintenance": {
        "last_service_date": "2022-08-05",
        "service_interval_months": 12
      },
      "photos": [
        {
          "id": "photo-789",
          "url": "https://api.condoit.com/photos/photo-789",
          "taken_at": "2024-12-10T11:30:00Z"
        }
      ]
    }
  ],
  "calculation_settings": {
    "algorithm_version": "1.2.0",
    "recalculate_all": false
  }
}
```

**Response:**
```json
{
  "job_id": "calc-job-456",
  "status": "processing",
  "equipment_count": 1,
  "estimated_completion_time": "2025-05-20T12:05:30Z",
  "webhook_url": "http://voltmetrics.internal/api/v1/jobs/calc-job-456/status"
}
```

### POST /ingest/facility

Submits facility data for aggregation and analysis.

**Request:**
```json
{
  "facility": {
    "id": "facility-456",
    "name": "Main Campus",
    "location": "123 Main St, Springfield, IL 62701",
    "coordinates": {
      "lat": 39.7817,
      "lng": -89.6501
    },
    "year_built": 1995,
    "environment": {
      "humidity_average": 65,
      "temperature_average": 72,
      "outdoor_exposure": "minimal"
    },
    "compliance": {
      "last_arc_flash_study": "2022-10-01",
      "last_infrared_scan": "2024-11-30"
    }
  },
  "calculation_settings": {
    "algorithm_version": "1.2.0",
    "recalculate_all": false
  }
}
```

**Response:**
```json
{
  "job_id": "calc-job-457",
  "status": "processing",
  "estimated_completion_time": "2025-05-20T12:10:30Z",
  "webhook_url": "http://voltmetrics.internal/api/v1/jobs/calc-job-457/status"
}
```

### POST /ingest/maintenance

Submits maintenance records for compliance evaluation.

**Request:**
```json
{
  "maintenance_records": [
    {
      "id": "maint-123",
      "equipment_id": "equip-123",
      "type": "preventive",
      "date": "2022-08-05T09:00:00Z",
      "technician": "John Smith",
      "findings": "Cleaned connections, checked tightness. Noticed heat discoloration on breaker 3.",
      "actions_taken": "Tightened all connections, replaced breaker 3",
      "next_service_due": "2023-08-05"
    }
  ],
  "calculation_settings": {
    "algorithm_version": "1.2.0",
    "recalculate_all": false
  }
}
```

**Response:**
```json
{
  "job_id": "calc-job-458",
  "status": "processing",
  "record_count": 1,
  "estimated_completion_time": "2025-05-20T12:03:30Z",
  "webhook_url": "http://voltmetrics.internal/api/v1/jobs/calc-job-458/status"
}
```

## Calculation Job API

### GET /jobs/{job_id}

Retrieves the status of a calculation job.

**Response:**
```json
{
  "job_id": "calc-job-456",
  "status": "completed",
  "started_at": "2025-05-20T12:00:30Z",
  "completed_at": "2025-05-20T12:03:45Z",
  "calculation_type": "equipment_risk",
  "items_processed": 1,
  "algorithm_version": "1.2.0",
  "results_available": true,
  "results_url": "http://voltmetrics.internal/api/v1/results/calc-job-456"
}
```

### POST /jobs/batch

Submits a batch of calculation jobs.

**Request:**
```json
{
  "jobs": [
    {
      "type": "equipment_risk",
      "equipment_ids": ["equip-123", "equip-124", "equip-125"]
    },
    {
      "type": "facility_aggregation",
      "facility_ids": ["facility-456"]
    }
  ],
  "priority": "high",
  "webhook_url": "https://api.masterbus.condoit.com/v1/calculation-webhooks/batch-update",
  "calculation_settings": {
    "algorithm_version": "1.2.0"
  }
}
```

**Response:**
```json
{
  "batch_id": "batch-789",
  "job_count": 2,
  "job_ids": ["calc-job-459", "calc-job-460"],
  "status": "processing",
  "estimated_completion_time": "2025-05-20T12:15:30Z",
  "webhook_url": "http://voltmetrics.internal/api/v1/jobs/batch-789/status"
}
```

## Results API

### GET /results/equipment/{equipment_id}

Retrieves risk assessment results for a specific equipment item.

**Query Parameters:**
- `algorithm_version` (optional): Specify which algorithm version to use (default: latest)
- `include_history` (optional): Include historical data points (default: false)

**Response:**
```json
{
  "equipment_id": "equip-123",
  "calculation_timestamp": "2025-05-20T12:03:45Z",
  "algorithm_version": "1.2.0",
  "risk_assessment": {
    "risk_score": 82,
    "risk_rating": "High",
    "risk_factors": [
      {
        "factor": "age",
        "score": 90,
        "description": "Panel is 45 years old",
        "weight": 0.35
      },
      {
        "factor": "maintenance",
        "score": 75,
        "description": "Last maintenance 3 years ago, exceeds NFPA 70B guidelines",
        "weight": 0.25
      },
      {
        "factor": "material",
        "score": 80,
        "description": "Aluminum conductors present",
        "weight": 0.20
      },
      {
        "factor": "environmental",
        "score": 65,
        "description": "Moderate humidity environment",
        "weight": 0.10
      },
      {
        "factor": "condition",
        "score": 70,
        "description": "Moderate corrosion observed",
        "weight": 0.10
      }
    ]
  },
  "compliance": {
    "nfpa_70b": {
      "compliant": false,
      "compliance_percentage": 45,
      "next_inspection_due": "2023-08-05",
      "maintenance_status": "overdue",
      "last_inspection": "2022-08-05T09:00:00Z"
    }
  },
  "historical_data": [
    {
      "date": "2024-12-01",
      "risk_score": 78
    },
    {
      "date": "2025-01-01",
      "risk_score": 79
    },
    {
      "date": "2025-02-01",
      "risk_score": 80
    },
    {
      "date": "2025-03-01",
      "risk_score": 80
    },
    {
      "date": "2025-04-01",
      "risk_score": 81
    },
    {
      "date": "2025-05-01",
      "risk_score": 82
    }
  ],
  "forecast": {
    "next_3_months": [
      {
        "date": "2025-06-01",
        "risk_score": 83
      },
      {
        "date": "2025-07-01",
        "risk_score": 84
      },
      {
        "date": "2025-08-01",
        "risk_score": 85
      }
    ]
  }
}
```

### GET /results/facility/{facility_id}

Retrieves aggregated risk assessment results for a facility.

**Query Parameters:**
- `algorithm_version` (optional): Specify which algorithm version to use (default: latest)
- `include_equipment` (optional): Include individual equipment data (default: false)
- `include_history` (optional): Include historical data points (default: false)

**Response:**
```json
{
  "facility_id": "facility-456",
  "calculation_timestamp": "2025-05-20T12:10:30Z",
  "algorithm_version": "1.2.0",
  "risk_summary": {
    "risk_score": 65,
    "risk_level": "Medium",
    "equipment_count": 60,
    "critical_equipment_count": 2,
    "high_risk_equipment_count": 5,
    "medium_risk_equipment_count": 29,
    "low_risk_equipment_count": 24
  },
  "risk_categories": [
    {
      "category": "age",
      "score": 70,
      "description": "Average equipment age is 15 years",
      "affected_equipment_count": 18,
      "percentage_of_facility": 30
    },
    {
      "category": "maintenance",
      "score": 65,
      "description": "Maintenance compliance is at 82%",
      "affected_equipment_count": 11,
      "percentage_of_facility": 18.3
    },
    {
      "category": "material",
      "score": 85,
      "description": "17 aluminum conductor connections",
      "affected_equipment_count": 17,
      "percentage_of_facility": 28.3
    },
    {
      "category": "environmental",
      "score": 65,
      "description": "Medium humidity risk",
      "affected_equipment_count": 8,
      "percentage_of_facility": 13.3
    }
  ],
  "compliance_summary": {
    "overall_compliance": 78,
    "nfpa_70b_compliance": 82,
    "nfpa_70e_compliance": 75
  },
  "top_threats": [
    {
      "equipment_id": "equip-123",
      "name": "Panel A",
      "type": "panel",
      "risk_score": 82,
      "risk_rating": "High",
      "primary_risk_factor": "age"
    }
  ],
  "historical_data": [
    {
      "date": "2024-12-01",
      "risk_score": 63
    },
    {
      "date": "2025-05-01",
      "risk_score": 65
    }
  ],
  "forecast": {
    "next_3_months": [
      {
        "date": "2025-08-01",
        "risk_score": 67
      }
    ]
  }
}
```

### GET /results/compliance/{facility_id}

Retrieves detailed compliance information for a facility.

**Query Parameters:**
- `standard` (optional): Filter by standard (nfpa_70b, nfpa_70e, or all)
- `include_equipment` (optional): Include individual equipment data (default: false)

**Response:**
```json
{
  "facility_id": "facility-456",
  "calculation_timestamp": "2025-05-20T12:10:30Z",
  "algorithm_version": "1.2.0",
  "compliance_summary": {
    "overall_compliance": 78,
    "nfpa_70b_compliance": 82,
    "nfpa_70e_compliance": 75
  },
  "nfpa_70b": {
    "compliance_percentage": 82,
    "equipment_counts": {
      "total": 60,
      "compliant": 49,
      "non_compliant": 11
    },
    "inspection_status": {
      "up_to_date": 42,
      "due_soon": 7,
      "overdue": 11
    },
    "next_inspections_due": [
      {
        "equipment_id": "equip-123",
        "equipment_name": "Panel A",
        "equipment_type": "panel",
        "due_date": "2023-08-05",
        "days_overdue": 655
      }
    ]
  },
  "nfpa_70e": {
    "compliance_percentage": 75,
    "arc_flash_study": {
      "last_study_date": "2022-10-01",
      "next_study_due": "2027-10-01",
      "status": "current"
    },
    "equipment_counts": {
      "total": 60,
      "compliant": 45,
      "non_compliant": 15
    },
    "label_status": {
      "present": 45,
      "missing": 15
    }
  }
}
```

## Algorithm API

### GET /algorithms

Retrieves a list of available algorithm versions.

**Response:**
```json
{
  "current_version": "1.2.0",
  "available_versions": [
    {
      "version": "1.0.0",
      "released_date": "2024-11-15",
      "description": "Initial algorithm implementation"
    },
    {
      "version": "1.1.0",
      "released_date": "2025-02-10",
      "description": "Added humidity impact factors"
    },
    {
      "version": "1.2.0",
      "released_date": "2025-04-25",
      "description": "Refined material risk calculations"
    }
  ]
}
```

### GET /algorithms/{version}/documentation

Retrieves documentation for a specific algorithm version.

**Response:**
```json
{
  "version": "1.2.0",
  "released_date": "2025-04-25",
  "description": "Refined material risk calculations",
  "changes": [
    "Updated aluminum conductor risk factors",
    "Improved connection type assessment",
    "Adjusted age impact by equipment type"
  ],
  "formula_documentation": "https://voltmetrics-docs.internal/algorithms/1.2.0",
  "validation_results": {
    "test_cases": 500,
    "accuracy": 95.8,
    "false_positives": 2.1,
    "false_negatives": 2.1
  }
}
```

## Webhook API

VoltMetrics sends webhook notifications to MasterBus when calculations are complete.

### POST {webhook_url}

**Request** (sent by VoltMetrics to MasterBus):
```json
{
  "event_type": "calculation_complete",
  "timestamp": "2025-05-20T12:03:45Z",
  "job_id": "calc-job-456",
  "job_type": "equipment_risk",
  "items_processed": 1,
  "status": "completed",
  "results_url": "http://voltmetrics.internal/api/v1/results/calc-job-456"
}
```

## Error Responses

All API endpoints use standard HTTP status codes and return error details in the following format:

```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "The provided input data is invalid",
    "details": "Equipment ID 'equip-123' is missing required field 'install_date'"
  }
}
```

## Versioning

The API is versioned through the URL path. The current version is v1. 