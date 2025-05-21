# Project Boundaries

Version: 1.0.0
Created: 2025-05-24

## Overview

This document defines the project boundaries and operational constraints for the MultiMind system. Clear boundaries ensure that each component operates within its designated scope and follows proper communication protocols.

## Project Manager Boundaries

### Scope of PM Operations

The Project Manager (PM):

1. **Must NOT directly work on or modify code in project subdirectories**
   - PM operates exclusively through the MultiMindPM directory
   - PM must never directly edit code, fix bugs, or implement features in subdirectories
   - All PM influence must flow through the established channels (directives, advisories, etc.)

2. **Must use established communication channels**
   - Directives for task assignments and requirements
   - Advisories for guidance and answering questions
   - Roadmaps for planning and timeline management
   - Rules for establishing standards and protocols

3. **Maintains the orchestration infrastructure only**
   - May update MultiMind system files and documentation
   - May create and update templates
   - May improve the MultiMind coordination protocol

## Project Boundaries

### Scope of Project Operations

Individual projects:

1. **Own their implementation details**
   - Projects have full autonomy over implementation approaches that satisfy directives
   - Projects make their own technical decisions within established guidelines
   - Projects are responsible for the quality of their deliverables

2. **Must use established communication channels**
   - Status reports for progress updates
   - Advisories for questions and guidance requests
   - Handoffs for cross-project coordination
   - Completion reports for phase completion notifications

3. **Must respect other project boundaries**
   - Projects may not directly modify code in other project directories
   - Cross-project coordination must happen through handoffs
   - Shared concerns must be addressed through the PM

## Communication Protocols

### Two-Way Communication

1. **PM to Projects**
   - Directives: Task descriptions and requirements
   - Rules: Coding standards and protocols
   - Advisory responses: Guidance on specific questions
   - Roadmap updates: Planning and timeline adjustments

2. **Projects to PM**
   - Status reports: Progress updates
   - Advisory requests: Questions and guidance needs
   - Completion reports: Phase completion notifications

3. **Project to Project**
   - Handoffs: Requests for coordination and integration
   - Must be tracked through the handoff protocol

## Violation Handling

If a boundary violation occurs:

1. **Document the violation**
   - Note what boundary was crossed
   - Document the circumstances and impact

2. **Restore proper boundaries**
   - Revert unauthorized changes
   - Re-establish correct communication channels

3. **Clarify the boundary**
   - Update this document if the boundary was unclear
   - Add specific examples if needed for clarity

## Rationale

These boundaries ensure:

1. **Clear responsibility**: Each component knows exactly what it's responsible for
2. **Proper coordination**: All communication follows established protocols
3. **System integrity**: Changes to one project don't unexpectedly impact others
4. **Architectural clarity**: The system structure remains clean and understandable 