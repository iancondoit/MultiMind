# MasterBus Project Context

Version: 0.1.0
Created: 2025-05-20

## Project Overview

MasterBus is an API layer connecting two existing systems:

1. **Condoit**: A software platform for electrical contractors to collect detailed information about electrical infrastructure. This includes:
   - Equipment data (panels, switchboards, transformers)
   - Connection information (conduit, cable tray, bus duct)
   - Photographic documentation
   - NFPA 70B compliance data (preventative maintenance standards)
   - NFPA 70E compliance data (arc flash analysis)
   - Detailed specifications (makes, models, settings, wire types, gauges, lengths)
   - Facility location information

2. **ThreatMap**: A dashboard for facilities maintenance organizations and commercial insurance providers that visualizes:
   - Overall risk assessments of facility portfolios
   - Equipment risk levels (including specific risks like aluminum conductors)
   - Compliance percentages for NFPA 70B and 70E standards
   - Interactive visualization of risks and compliance status

3. **MasterBus** (to be developed): The API layer connecting these systems, designed to:
   - Extract relevant data from Condoit
   - Transform it into formats usable by ThreatMap
   - Be scalable for future additional consumers beyond ThreatMap
   - Handle significant data volume (though speed is not the primary concern)

## Development Approach

We are using the MultiMind architecture to coordinate development. This project will progress in phases:

1. Initially focus solely on MasterBus development
2. Later coordinate across all three systems with multiple AI agents
3. Use the Project Manager agent to oversee the entire integration

## Current System States

### Condoit
- Functional production software
- Unknown API documentation state
- Will require code analysis to understand data structures and endpoints

### ThreatMap
- Mock-up stage software
- Consumes facility data as JSON files
- Early stage development

### MasterBus
- To be developed from scratch
- Must be built for scale
- Will serve as foundation for multiple future data consumers

## Technical Considerations

1. **Architecture**: MasterBus should be designed with scalability as the primary concern

2. **Authentication/Security**:
   - There are likely existing security measures in Condoit
   - We have a branch of the codebase where we can potentially bypass security for testing
   - ThreatMap security protocols are currently unknown

3. **Performance**:
   - Must handle considerable data volume
   - Speed is not a primary concern at this stage
   - Should be optimized for large data sets rather than rapid response time

## Project Plan Summary

The project is organized into five phases:
1. Setup and Discovery
2. Analysis and Planning
3. Core Development
4. Integration and Refinement
5. Deployment and Future Planning

Detailed steps for each phase are defined in the project roadmap document.

## Decisions and Questions

*This section will be updated as project decisions are made and questions are answered.*

## Key Stakeholders

- Electrical contractors (Condoit users)
- Facilities maintenance organizations (ThreatMap users)
- Potential commercial insurance providers (future ThreatMap users)
- Future systems that may connect to MasterBus 