# VoltMetrics Architecture

Version: 0.1.0
Created: 2025-05-20
Status: Draft

## System Overview

VoltMetrics is the analysis engine responsible for processing electrical infrastructure data and generating risk assessments, compliance evaluations, and trend analyses. It serves as a specialized computational service that works in concert with MasterBus to provide actionable insights to ThreatMap and other potential consumers.

## Architecture Principles

1. **Computational Isolation** - Separate intensive calculations from data transport concerns
2. **Algorithm Versioning** - Track and version all risk calculation methods
3. **Stateless Core** - Core calculation engine operates statelessly for scalability
4. **Cached Results** - Store calculation results to minimize redundant processing
5. **Asynchronous Processing** - Handle long-running calculations without blocking
6. **Domain Separation** - Organize functionality by electrical domain rather than technical function

## High-Level Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                         VoltMetrics Engine                         │
├───────────┬───────────────────┬──────────────────┬────────────────┤
│           │                   │                  │                │
│  Input    │   Calculation     │   Result         │  Notification  │
│  API      │   Engine          │   Storage        │  Service       │
│           │                   │                  │                │
└───┬───────┴─────────┬─────────┴──────┬───────────┴────────┬───────┘
    │                 │                │                    │
    │                 ▼                ▼                    │
    │         ┌───────────────┐ ┌─────────────┐            │
    │         │ Algorithm     │ │ Time-Series │            │
    │         │ Repository    │ │ Database    │            │
    │         └───────────────┘ └─────────────┘            │
    ▼                                                       ▼
┌─────────────┐                                    ┌────────────────┐
│             │                                    │                │
│  MasterBus  │◄───────────────────────────────────┤  MasterBus    │
│  (Input)    │                                    │  (Output)      │
│             │                                    │                │
└─────────────┘                                    └────────────────┘
```

## Core Components

### 1. Input API

The Input API receives raw data from MasterBus, including:
- Equipment details and specifications
- Maintenance records and inspection results
- Facility information
- Historical data points

This component validates and normalizes incoming data before passing it to the calculation engine.

### 2. Calculation Engine

The central component responsible for executing risk assessment algorithms:

- **Equipment Risk Calculator** - Assesses individual equipment risk based on multiple factors
- **Compliance Evaluator** - Evaluates NFPA 70B and 70E compliance
- **Facility Aggregator** - Rolls up equipment metrics to facility level
- **Trend Analyzer** - Processes historical data to identify trends
- **Forecast Generator** - Projects future risk levels based on current data

The engine is designed to be horizontally scalable and can process calculations in parallel.

### 3. Algorithm Repository

Stores and versions all calculation algorithms:

- **Risk Factor Formulas** - Mathematical expressions for risk evaluation
- **Weighting Coefficients** - Factors for adjusting relative importance of different risks
- **Threshold Values** - Boundaries between risk categories (Low, Medium, High, Critical)
- **Version History** - Complete tracking of algorithm changes over time

### 4. Result Storage

Caches calculation results to avoid redundant processing:

- **Risk Score Cache** - Stores calculated risk scores with TTL
- **Compliance Evaluations** - Caches compliance status evaluations
- **Aggregate Metrics** - Stores facility-level aggregated data
- **Calculation Metadata** - Tracks which algorithm versions were used for each calculation

### 5. Time-Series Database

Specialized storage for historical trend data:

- **Equipment History** - Risk scores over time for each equipment item
- **Facility Trends** - Facility-level risk metrics over time
- **Compliance History** - Changes in compliance status
- **Seasonal Patterns** - Identified cyclical patterns in risk factors

### 6. Notification Service

Communicates calculation completion and status updates to MasterBus:

- **Calculation Completion Webhooks** - Notifies when requested calculations are complete
- **Critical Risk Alerts** - Pushes notifications for newly identified critical risks
- **Processing Status Updates** - Reports on long-running calculation progress

## Data Flow

1. MasterBus sends raw equipment and facility data to the Input API
2. Input API normalizes and validates the data
3. Calculation Engine processes the data using algorithms from the Algorithm Repository
4. Results are stored in the Result Storage and Time-Series Database
5. Notification Service informs MasterBus that calculations are complete
6. MasterBus retrieves processed results through the Output API

## Technical Stack

- **Language**: Python for core calculation engine
- **API Framework**: FastAPI for Input/Output interfaces
- **Caching**: Redis for Result Storage
- **Time-Series**: InfluxDB or TimescaleDB for historical data
- **Algorithm Storage**: Git-backed versioned storage
- **Container Orchestration**: Kubernetes for horizontal scaling
- **Message Queue**: RabbitMQ for asynchronous processing

## Scaling Approach

VoltMetrics is designed to scale horizontally at multiple levels:

1. **Calculation Workers** - Multiple instances process calculations in parallel
2. **Data Partitioning** - Calculations are partitioned by facility or geographical region
3. **Priority Queuing** - Critical calculations are prioritized over routine updates
4. **Scheduled Background Processing** - Non-urgent trend analysis runs during off-peak hours

## Development Phases

1. **Phase 1**: Core algorithm development and baseline architecture
2. **Phase 2**: Caching and performance optimization
3. **Phase 3**: Trend analysis and forecasting capabilities
4. **Phase 4**: Advanced machine learning risk models
5. **Phase 5**: Real-time monitoring and alerting

## Next Steps

1. Define detailed data models for engine input/output
2. Research and document risk calculation formulas
3. Develop proof of concept for core calculation engine
4. Design algorithm versioning approach
5. Create initial API specifications for MasterBus integration 