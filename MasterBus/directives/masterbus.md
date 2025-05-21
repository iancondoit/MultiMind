# MasterBus Directives

Version: 0.1.0

## Project Context

MasterBus is an API layer designed to connect the Condoit electrical infrastructure data collection system with the ThreatMap risk visualization dashboard. It must transform detailed electrical system data into risk assessments and compliance metrics while being scalable for future additional consumers.

## Current Tasks - Phase 1: Discovery

1. **Analyze Condoit codebase**
   - Identify data structures and models
   - Document available API endpoints or data access methods
   - Map electrical infrastructure data fields relevant to risk assessment
   - Document authentication mechanisms

2. **Analyze ThreatMap requirements**
   - Review the JSON format expected by ThreatMap
   - Document visualization requirements
   - Identify which Condoit data fields map to ThreatMap requirements
   - Understand how ThreatMap calculates risk levels

3. **Create architecture document**
   - Define technology stack for MasterBus
   - Create component architecture diagram
   - Document data flow between systems
   - Define API standards and practices
   - Save to `docs/architecture.md`

4. **Define data transformation requirements**
   - Document which Condoit data needs transformation
   - Define algorithms for risk assessment calculations
   - Create data mapping documentation
   - Save to `docs/data-models.md`

5. **Create API specification**
   - Define endpoints for ThreatMap to consume
   - Document request/response formats
   - Define authentication and security requirements
   - Create OpenAPI/Swagger specification
   - Save to `docs/api-spec.md`

## Completion Criteria

This phase will be considered complete when:
- Both codebases have been analyzed and documented
- Architecture document is complete
- Data transformation requirements are defined
- Initial API specification is created

## Next Phase Preview

Phase 2 will focus on the implementation of data models and core API structure once the architecture and specifications are approved.

## Dependencies

- Access to Condoit and ThreatMap codebases
- Understanding of electrical risk assessment factors
- Knowledge of NFPA 70B and 70E standards for evaluating compliance
