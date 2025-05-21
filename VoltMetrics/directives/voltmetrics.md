# VoltMetrics Directives

Version: 0.2.0
Updated: 2025-05-22

## Project Context

VoltMetrics is the specialized analysis engine component of the Condoit-MasterBus-ThreatMap architecture. It is responsible for the computationally intensive risk assessment, compliance evaluation, and trend analysis of electrical infrastructure data. VoltMetrics receives raw data from the MasterBus API, performs complex calculations, and returns processed risk metrics that are then served to ThreatMap via MasterBus.

## Current Status

**Phase 1: Architecture and Algorithm Design** has been completed successfully. The team has defined risk assessment algorithms, created API specifications, designed the engine architecture, and established compliance evaluation methodologies. The foundation is now in place to begin implementation.

## Current Tasks - Phase 2: Core Implementation

1. **Implement Data Models**
   - Create Python classes for equipment, facility, and maintenance data
   - Implement Pydantic models for API request/response validation
   - Develop SQLAlchemy ORM models for database storage
   - Create serialization/deserialization methods for data interchange

2. **Develop Core Calculation Engine**
   - Implement algorithm classes based on the defined risk formulas
   - Create the weighting system for different risk factors
   - Develop formula versioning and tracking capabilities
   - Implement basic caching for calculation results

3. **Create API Endpoints** 
   - Set up FastAPI framework with project structure
   - Implement data ingestion endpoints (equipment, facility, maintenance)
   - Create job management API for tracking calculation status
   - Develop basic result retrieval endpoints

4. **Testing Framework**
   - Implement comprehensive unit tests for calculation accuracy
   - Create integration tests for API endpoints
   - Develop mock data generator for realistic electrical equipment
   - Implement test coverage reporting

5. **Integration Preparation**
   - Coordinate with MasterBus team on API interface details
   - Document any changes or refinements to the API specification
   - Create authentication mechanism compatible with MasterBus
   - Develop webhook implementation for notifying MasterBus of calculation completion

## Implementation Guidelines

1. **Technology Stack**
   - Programming Language: Python 3.10+
   - API Framework: FastAPI
   - ORM: SQLAlchemy 2.0
   - Database: PostgreSQL (primary), Redis (caching)
   - Testing: pytest with pytest-cov
   - CI/CD: GitHub Actions

2. **Development Approach**
   - Follow test-driven development for all calculation algorithms
   - Implement incremental development with frequent PR submissions
   - Focus on core calculation accuracy before optimization
   - Separate algorithmic logic from data access and API concerns
   - Document all significant design decisions

3. **Performance Considerations**
   - Defer optimization until basic functionality is complete
   - Focus on algorithm correctness first, then performance
   - Implement basic caching early to establish patterns
   - Use profiling to identify bottlenecks rather than premature optimization

## Deliverables

1. **Functional Core Engine**
   - Implementation of core risk calculation algorithms
   - Basic API endpoints for data ingestion and retrieval
   - Algorithm versioning system

2. **Documentation**
   - Updated API specification with any refinements
   - Algorithm implementation details
   - Test data documentation
   - Implementation architecture document

3. **Test Suite**
   - Unit tests for calculation formulas
   - API integration tests
   - Test data generator

## Timeline

Phase 2 should be completed within 3-4 weeks, with priority given to the core calculation engine and API endpoints to facilitate early integration testing with MasterBus.

## Phase Completion Protocol

**IMPORTANT**: For ALL phases (including Phase 1, 2, 3, and future phases), follow the standard completion protocol as defined in `rules/completion_reporting.md`:

1. Update your status report in `reports/status.md` with all completed tasks
2. Create a completion marker file in `/output/completions/VoltMetrics-Phase{N}-complete.md` (where {N} is the phase number)
3. Run the completion command from the project root: `./multimind.py complete VoltMetrics Phase{N}`

For your current Phase 2 completion when ready, you would follow these steps:
```bash
# 1. Update status.md (already part of your regular process)

# 2. Create a completion marker file
# Example content for Phase 2:
# ----------------------------
# Project Completion: VoltMetrics - Phase2
# 
# Version: [your current version]
# Completed: [current date]
# Project: VoltMetrics
# Phase: Core Implementation
# 
# ## Completed Directives
# 
# * Implemented Data Models (Pydantic & SQLAlchemy)
# * Developed Core Calculation Engine
# * Created API Endpoints with FastAPI
# * Built Testing Framework
# * Prepared for MasterBus Integration
# 
# ## Notes
# 
# [Any relevant notes]
# 
# ## Next Phase
# 
# Ready to begin Phase 3: Advanced Analysis Features
# ----------------------------

# 3. Run the completion command
./multimind.py complete VoltMetrics Phase2
```

This completion process is identical for each phase - simply update the phase number and details accordingly.

## Coordination with Other Components

Regular coordination with the MasterBus team is essential during this phase to ensure API compatibility. This includes:

1. Sharing mock data formats for testing
2. Confirming authentication mechanisms
3. Validating webhook notification formats
4. Checking for any potential breaking changes to the API

## Next Phase Preview

Phase 3 will focus on implementing advanced analysis features including NFPA compliance evaluation, facility-level aggregation, and historical trend analysis.
