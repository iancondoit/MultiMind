# Condoit Codebase Analysis

Version: 0.1.0
Created: 2025-05-20
Status: Initial Analysis

## Overview

This document contains analysis of the Condoit codebase, focusing on data structures, models, and potential API integration points for the MasterBus API layer.

## Project Structure

The Condoit project uses a monorepo structure managed with pnpm workspaces:

- `apps/` - Contains the main applications
  - `mobileapp/` - Mobile application
  - `eventbus/` - Event messaging system (potential integration point)
  - `webapp-remix/` - Web application

- `packages/` - Shared libraries and modules
  - `database/` - Database access and models
  - `ui/` - Shared UI components
  - `services/` - Business logic and services
  - `equipment-classes/` - Equipment type definitions
  - `condoit-types/` - TypeScript type definitions
  - `utils/` - Utility functions
  - `config/` - Shared configuration

## Key Data Models

The Condoit database uses Prisma ORM with PostgreSQL. Key equipment models from `packages/database/prisma/schema/Equipment.prisma` include:

1. **Panel** - Electrical panels with properties like:
   - Voltage, phases, power ratings
   - Manufacturing details (manufacturer, model, etc.)
   - Physical characteristics (dimensions, mounting type)
   - Location information
   - Risk factors (age via installDate, condition via inspections)

2. **Switchboard** - Similar to panels but with higher capacity

3. **Transformer** - Voltage transformation equipment

4. **Raceway** - Conduits and cable trays that connect equipment

5. **Equipment** - Generic equipment type

6. **Conductors** - Wiring information including material (copper/aluminum)

7. **Breaker** - Circuit protection devices

These models contain the raw data needed for risk assessment, including:
- Equipment age (installDate)
- Material types (particularly aluminum conductors)
- Inspection history
- Physical specifications

## Potential API Integration Points

1. **Event Bus** - The `apps/eventbus` component may provide a way to subscribe to equipment changes

2. **Database Access** - The `packages/database` contains Prisma models that could be queried directly

3. **Services** - The `packages/services` likely contains business logic that could be leveraged

## Data Transformation Requirements

To transform Condoit data into ThreatMap-compatible risk assessments, we need to:

1. **Calculate Equipment Risk Scores** based on:
   - Age (from installDate)
   - Conductor material (particularly aluminum)
   - Inspection status and history
   - Physical conditions (corrosion, temperature)

2. **Aggregate Facility-Level Metrics**:
   - Count equipment by risk level (low, medium, high, critical)
   - Calculate overall facility risk score
   - Identify "top threat" equipment

3. **Evaluate Compliance Status**:
   - NFPA 70B compliance (maintenance schedules)
   - NFPA 70E compliance (arc flash studies)

## Next Steps

1. Examine the API structure of the webapp and eventbus components
2. Investigate how Condoit handles authentication and authorization
3. Identify optimal data access patterns (direct DB access vs API)
4. Analyze how inspections and maintenance records are stored
5. Document facility/location hierarchy to understand data organization
6. Explore how photos and visual data are stored and accessed 