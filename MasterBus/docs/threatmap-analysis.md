# ThreatMap Codebase Analysis

Version: 0.2.0
Created: 2025-05-20
Status: Completed

## Overview

This document contains analysis of the ThreatMap codebase, focusing on its data requirements, expected input formats, and visualization needs for integration with the MasterBus API layer.

## Project Structure

ThreatMap is a Next.js application with TypeScript and Tailwind CSS:

- `app/` - Next.js app directory structure
  - `facilities/` - Portfolio view of all facilities
  - `facility/[id]/` - Individual facility detail pages
  - `reports/` - Reporting views
  - `settings/` - Configuration settings

- `components/` - React components
  - `dashboard/` - Dashboard visualization components
  - `facility/` - Facility detail components
  - `ui/` - Shared UI components

- `lib/` - Utility functions and data
  - `mock-data.ts` - Contains mock data structures and TypeScript interfaces

## Data Requirements

Based on the mock data and interfaces in `lib/mock-data.ts`, ThreatMap expects the following data structures:

### 1. Equipment Interface

```typescript
interface Equipment {
  id: string;
  name: string;
  type: string;
  location: string;
  installDate: string;
  condition: 'Excellent' | 'Good' | 'Fair' | 'Poor' | 'Critical';
  riskRating: 'Low' | 'Medium' | 'High' | 'Critical';
  temperature?: string;
  rustLevel?: 'None' | 'Minimal' | 'Moderate' | 'Severe';
  lastService: string;
  photo?: string;
  interventionCount?: number;
  conductorMaterial?: 'Copper' | 'Aluminum';
  clearanceIssue?: boolean;
  corrosionLevel?: 'None' | 'Minimal' | 'Moderate' | 'Severe';
}
```

### 2. Facility Interface

```typescript
interface Facility {
  id: string;
  name: string;
  location: string;
  coordinates: {
    lat: number;
    lng: number;
  };
  riskScore: number;
  complianceStatus: 'Compliant' | 'Warning' | 'Out of Compliance';
  lastInspection: string;
  contractor: string;
  lastArcFlashAnalysis?: string;
  lastInfraredScan?: string;
  systemAge?: string;
  facilityAge?: number;
  equipmentCount?: number;
  criticalEquipmentCount?: number;
  highRiskEquipmentCount?: number;
  averageEquipmentRisk?: number;
  humidityRisk?: 'Low' | 'Medium' | 'High';
  conductorTypeBreakdown?: {
    copper: number;
    aluminum: number;
  };
  equipmentRiskDistribution?: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  historicalRisk?: HistoricalRisk[];
  topThreats: Equipment[];
}
```

### 3. Historical Risk Interface

```typescript
interface HistoricalRisk {
  month: string;
  riskScore: number;
  equipmentCount: number;
  equipmentAge: number;
}
```

## Visualization Requirements

ThreatMap uses several visualization types that require specific data formats:

1. **Risk Score Visualization** - Circular gauge showing overall risk level (0-100)
2. **Risk Distribution Charts** - Bar or pie charts showing equipment risk levels
3. **Historical Trend Charts** - Line charts showing risk changes over time
4. **Geographic Map** - Google Maps integration showing facility locations with risk indicators
5. **Equipment Lists** - Sortable, filterable tables of equipment with risk indicators
6. **Compliance Status Indicators** - Visual indicators for NFPA 70B and 70E compliance

## Calculated Fields

ThreatMap expects several calculated fields that must be derived from raw Condoit data:

1. **Risk Scores** - Equipment and facility-level risk assessments on a 0-100 scale
2. **Compliance Status** - Evaluation of maintenance and arc flash study compliance
3. **Equipment Age** - Calculated from installation date to present
4. **Risk Distribution** - Counts of equipment in each risk category
5. **Top Threats** - Identification of the highest-risk equipment items
6. **Historical Trends** - Time-series data of risk metrics over the past 6-12 months

## API Integration Points

Based on the application structure, MasterBus API would need to provide:

1. **Facility Listing Endpoint** - For the dashboard/portfolio view
2. **Facility Detail Endpoint** - For individual facility pages
3. **Equipment Listing Endpoint** - For displaying equipment within a facility
4. **Equipment Detail Endpoint** - For individual equipment detail pages
5. **Historical Data Endpoint** - For trend visualization

## Next Steps

1. Determine if the facility page is expected to load data on the client or server side
2. Identify potential extension points for additional risk metrics
3. Understand the authentication flow for accessing the API
4. Determine caching requirements for performance optimization
5. Document specific formats for derived risk calculation metrics 