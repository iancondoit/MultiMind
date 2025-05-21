# MasterBus API Specification

Version: 0.2.0
Created: 2025-05-20
Updated: 2025-05-20
Status: Draft

## Overview

This document defines the REST API for MasterBus, the interface layer between Condoit's electrical infrastructure data and ThreatMap's risk visualization dashboard. The API transforms raw electrical equipment data into risk assessment information.

## Base URL

```
https://api.masterbus.condoit.com/v1
```

## Authentication

All API requests require authentication using JWT tokens.

```
Authorization: Bearer [token]
```

## API Endpoints

### Facilities

#### GET /facilities

Retrieves a list of facilities with risk summary information.

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of results per page (default: 20)
- `sort` (optional): Sort field (options: name, risk_score, last_updated)
- `order` (optional): Sort order (options: asc, desc)
- `search` (optional): Search term for facility name or location

**Response:**
```json
{
  "total": 100,
  "page": 1,
  "limit": 20,
  "facilities": [
    {
      "id": "facility-123",
      "name": "Main Campus",
      "location": "123 Main St, Springfield, IL 62701",
      "coordinates": {
        "lat": 39.7817,
        "lng": -89.6501
      },
      "risk_score": 65,
      "compliance_status": "Warning",
      "last_inspection": "2025-04-01T14:30:00Z",
      "contractor": "Bright Electric",
      "equipment_count": 60,
      "critical_equipment_count": 2,
      "high_risk_equipment_count": 5,
      "risk_distribution": {
        "low": 24,
        "medium": 29,
        "high": 5,
        "critical": 2
      },
      "last_updated": "2025-05-01T14:30:00Z"
    }
    // Additional facilities...
  ]
}
```

#### GET /facilities/{facility_id}

Retrieves detailed information about a specific facility.

**Response:**
```json
{
  "id": "facility-123",
  "name": "Main Campus",
  "location": "123 Main St, Springfield, IL 62701",
  "coordinates": {
    "lat": 39.7817,
    "lng": -89.6501
  },
  "risk_score": 65,
  "compliance_status": "Warning",
  "risk_distribution": {
    "low": 24,
    "medium": 29,
    "high": 5,
    "critical": 2
  },
  "contractor": "Bright Electric",
  "last_inspection": "2025-04-01T14:30:00Z",
  "last_arc_flash_analysis": "2022-10-01T09:00:00Z",
  "last_infrared_scan": "2024-11-30T11:45:00Z",
  "system_age": "15 years",
  "facility_age": 15,
  "equipment_count": 60,
  "critical_equipment_count": 2,
  "high_risk_equipment_count": 5,
  "average_equipment_risk": 0.68,
  "humidity_risk": "Medium",
  "conductor_type_breakdown": {
    "copper": 43,
    "aluminum": 17
  },
  "risk_factors": [
    {
      "factor": "aging_infrastructure",
      "score": 72,
      "description": "Several panels over 30 years old"
    },
    {
      "factor": "aluminum_conductors",
      "score": 85,
      "description": "Multiple aluminum to copper transitions"
    },
    {
      "factor": "maintenance_compliance",
      "score": 45,
      "description": "Maintenance schedule behind NFPA 70B recommendations"
    }
  ],
  "historical_risk": [
    {
      "month": "Dec 2024",
      "risk_score": 63,
      "equipment_count": 58,
      "equipment_age": 14.7
    },
    {
      "month": "Jan 2025",
      "risk_score": 64,
      "equipment_count": 59,
      "equipment_age": 14.8
    },
    {
      "month": "Feb 2025",
      "risk_score": 64,
      "equipment_count": 59,
      "equipment_age": 14.9
    },
    {
      "month": "Mar 2025",
      "risk_score": 65,
      "equipment_count": 60,
      "equipment_age": 15.0
    },
    {
      "month": "Apr 2025",
      "risk_score": 65,
      "equipment_count": 60,
      "equipment_age": 15.1
    },
    {
      "month": "May 2025",
      "risk_score": 65,
      "equipment_count": 60,
      "equipment_age": 15.2
    }
  ],
  "top_threats": [
    {
      "id": "equip-456",
      "name": "Panel A",
      "type": "panel",
      "location": "Building 1, Electrical Room 3",
      "install_date": "1980-03-15",
      "condition": "Poor",
      "risk_rating": "Critical",
      "temperature": "78°C",
      "rust_level": "Moderate",
      "last_service": "2023-08-05",
      "photo_url": "/api/photos/equip-456/thumbnail",
      "intervention_count": 5,
      "conductor_material": "Aluminum",
      "corrosion_level": "Moderate"
    },
    {
      "id": "equip-789",
      "name": "Transformer TX-3",
      "type": "transformer",
      "location": "Building 2, Electrical Vault",
      "install_date": "1992-11-23",
      "condition": "Poor",
      "risk_rating": "High",
      "temperature": "91°C",
      "rust_level": "Severe",
      "last_service": "2022-06-12",
      "photo_url": "/api/photos/equip-789/thumbnail",
      "intervention_count": 3,
      "conductor_material": "Copper",
      "corrosion_level": "Severe"
    }
  ],
  "last_updated": "2025-05-01T14:30:00Z"
}
```

### Equipment

#### GET /facilities/{facility_id}/equipment

Retrieves a list of electrical equipment for a specific facility with risk information.

**Query Parameters:**
- `page` (optional): Page number for pagination (default: 1)
- `limit` (optional): Number of results per page (default: 50)
- `type` (optional): Filter by equipment type (options: panel, switchboard, transformer, etc.)
- `risk_level` (optional): Filter by risk level (options: low, medium, high, critical)
- `sort` (optional): Sort field (options: name, type, risk_rating, install_date, last_service)
- `order` (optional): Sort order (options: asc, desc)
- `search` (optional): Search term for equipment name or location

**Response:**
```json
{
  "total": 60,
  "page": 1,
  "limit": 50,
  "equipment": [
    {
      "id": "equip-456",
      "name": "Panel A",
      "type": "panel",
      "location": "Building 1, Electrical Room 3",
      "install_date": "1980-03-15",
      "condition": "Poor",
      "risk_rating": "Critical",
      "risk_score": 82,
      "risk_factors": [
        {
          "factor": "age",
          "score": 90,
          "description": "Panel is 45 years old"
        },
        {
          "factor": "maintenance",
          "score": 75,
          "description": "Last maintenance 3 years ago, exceeds NFPA 70B guidelines"
        },
        {
          "factor": "aluminum_conductors",
          "score": 80,
          "description": "Panel has aluminum conductor connections"
        }
      ],
      "temperature": "78°C",
      "rust_level": "Moderate",
      "last_service": "2023-08-05",
      "photo_url": "/api/photos/equip-456/thumbnail",
      "intervention_count": 5,
      "conductor_material": "Aluminum",
      "corrosion_level": "Moderate",
      "last_updated": "2025-04-28T10:15:00Z"
    }
    // Additional equipment...
  ]
}
```

#### GET /equipment/{equipment_id}

Retrieves detailed information about a specific piece of equipment.

**Response:**
```json
{
  "id": "equip-456",
  "name": "Panel A",
  "type": "panel",
  "manufacturer": "Square D",
  "model": "QO-30",
  "serial_number": "SN123456",
  "install_date": "1980-03-15",
  "location": {
    "facility_id": "facility-123",
    "facility_name": "Main Campus",
    "building": "Building 1",
    "room": "Electrical Room 3",
    "coordinates": {
      "lat": 39.7834,
      "lng": -89.6520
    }
  },
  "specifications": {
    "voltage": "208/120V",
    "amperage": 200,
    "phases": 3,
    "mount_type": "surface",
    "enclosure_type": "NEMA 1",
    "slots": 30,
    "main_disconnect": true,
    "main_disconnect_rating": 200
  },
  "photos": [
    {
      "id": "photo-789",
      "url": "/api/photos/photo-789",
      "thumbnail_url": "/api/photos/photo-789/thumbnail",
      "caption": "Front view",
      "taken_at": "2024-12-10T11:30:00Z"
    }
  ],
  "risk_assessment": {
    "risk_rating": "Critical",
    "risk_score": 82,
    "condition": "Poor",
    "risk_factors": [
      {
        "factor": "age",
        "score": 90,
        "description": "Panel is 45 years old"
      },
      {
        "factor": "maintenance",
        "score": 75,
        "description": "Last maintenance 3 years ago, exceeds NFPA 70B guidelines"
      },
      {
        "factor": "aluminum_conductors",
        "score": 80,
        "description": "Panel has aluminum conductor connections"
      },
      {
        "factor": "overloading",
        "score": 65,
        "description": "Panel loading at 85% capacity"
      }
    ],
    "temperature": "78°C",
    "rust_level": "Moderate",
    "corrosion_level": "Moderate"
  },
  "service_history": [
    {
      "id": "service-123",
      "type": "Maintenance",
      "date": "2023-08-05T09:00:00Z",
      "technician": "John Smith",
      "notes": "Cleaned connections, checked tightness. Noticed heat discoloration on breaker 3."
    }
  ],
  "compliance": {
    "nfpa_70b": {
      "compliant": false,
      "compliance_percentage": 45,
      "next_inspection_due": "2023-08-05",
      "maintenance_status": "overdue",
      "last_inspection": "2023-08-05T09:00:00Z"
    },
    "nfpa_70e": {
      "compliant": true,
      "compliance_percentage": 92,
      "arc_flash_label_present": true,
      "ppe_requirements": "Category 2",
      "incident_energy": 8.2,
      "last_assessment": "2024-06-03T14:15:00Z"
    }
  },
  "last_updated": "2025-04-28T10:15:00Z",
  "created_at": "2024-11-17T13:20:00Z"
}
```

### Compliance

#### GET /facilities/{facility_id}/compliance

Retrieves compliance information for a specific facility.

**Response:**
```json
{
  "facility_id": "facility-123",
  "facility_name": "Main Campus",
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
        "equipment_id": "equip-456",
        "equipment_name": "Panel A",
        "equipment_type": "panel",
        "due_date": "2025-08-05",
        "days_overdue": 270
      }
      // Additional equipment...
    ]
  },
  "nfpa_70e": {
    "compliance_percentage": 75,
    "equipment_counts": {
      "total": 60,
      "compliant": 45,
      "non_compliant": 15
    },
    "arc_flash_label_status": {
      "present": 52,
      "missing": 8
    },
    "next_assessments_due": [
      {
        "equipment_id": "equip-789",
        "equipment_name": "Transformer TX-3",
        "equipment_type": "transformer",
        "due_date": "2025-06-03"
      }
      // Additional equipment...
    ]
  },
  "last_updated": "2025-05-01T14:30:00Z"
}
```

### Risk Assessment

#### GET /facilities/{facility_id}/risks

Retrieves aggregated risk information for a specific facility.

**Response:**
```json
{
  "facility_id": "facility-123",
  "facility_name": "Main Campus",
  "risk_summary": {
    "risk_score": 65,
    "risk_level": "Medium",
    "high_risk_equipment_count": 5,
    "medium_risk_equipment_count": 29,
    "low_risk_equipment_count": 24,
    "critical_risk_equipment_count": 2
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
      "category": "aluminum_conductors",
      "score": 85,
      "description": "Facility has 17 aluminum conductor connections",
      "affected_equipment_count": 17,
      "percentage_of_facility": 28.3
    },
    {
      "category": "humidity",
      "score": 65,
      "description": "Medium humidity risk with some corrosion noted",
      "affected_equipment_count": 8,
      "percentage_of_facility": 13.3
    }
  ],
  "historical_trend": [
    {
      "month": "Dec 2024",
      "risk_score": 63,
      "equipment_count": 58,
      "equipment_age": 14.7
    },
    // Additional monthly entries...
  ],
  "high_risk_items": [
    {
      "equipment_id": "equip-456",
      "equipment_name": "Panel A",
      "equipment_type": "panel",
      "risk_level": "Critical",
      "risk_score": 82,
      "primary_risk_factor": "age",
      "location": "Building 1, Electrical Room 3"
    },
    // Additional high-risk items...
  ],
  "risk_recommendation": {
    "priority_actions": [
      {
        "action": "Replace Panel A",
        "affected_equipment": ["equip-456"],
        "risk_reduction": 15,
        "estimated_cost": "High",
        "urgency": "Critical"
      },
      {
        "action": "Update arc flash labels",
        "affected_equipment": ["equip-789", "equip-101"],
        "risk_reduction": 8,
        "estimated_cost": "Low",
        "urgency": "High"
      }
    ]
  },
  "last_updated": "2025-05-01T14:30:00Z"
}
```

### Photos

#### GET /photos/{photo_id}

Retrieves a specific photo.

**Response:**
- Binary image data with appropriate Content-Type header

#### GET /photos/{photo_id}/thumbnail

Retrieves a thumbnail version of a specific photo.

**Response:**
- Binary image data with appropriate Content-Type header

### Portfolio Analysis

#### GET /portfolio/summary

Retrieves summary information for the entire facility portfolio.

**Response:**
```json
{
  "total_facilities": 15,
  "total_equipment": 857,
  "risk_overview": {
    "average_risk_score": 58,
    "high_risk_facilities": 3,
    "critical_risk_equipment": 12,
    "high_risk_equipment": 47
  },
  "compliance_overview": {
    "nfpa_70b_compliance": 76,
    "nfpa_70e_compliance": 68,
    "overall_compliance": 72
  },
  "risk_trends": [
    {
      "month": "Dec 2024",
      "risk_score": 63,
      "equipment_count": 832,
      "equipment_age": 12.3
    },
    // Additional monthly entries...
  ],
  "highest_risk_facilities": [
    {
      "facility_id": "facility-456",
      "facility_name": "Riverside Medical Plaza",
      "risk_score": 88,
      "location": "Columbus, OH",
      "critical_equipment_count": 3
    },
    // Additional facilities...
  ],
  "last_updated": "2025-05-01T14:30:00Z"
}
```

## Error Responses

All API endpoints use standard HTTP status codes and return error details in the following format:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource could not be found",
    "details": "Facility with ID facility-999 does not exist"
  }
}
```

## Rate Limiting

API requests are limited to 100 requests per minute per API key. Rate limit information is included in response headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1590000000
```

## Versioning

The API is versioned through the URL path. The current version is v1. 