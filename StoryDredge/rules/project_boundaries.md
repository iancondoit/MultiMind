# Project Boundaries

Version: 0.1.0

## Overview

This document defines the operational boundaries between the Project Manager (PM) and individual project teams within the MultiMind system. Respecting these boundaries ensures clear accountability, reduces confusion, and maintains the integrity of the project structure.

## Core Principle

The MultiMind system is based on a clear separation of concerns:

1. The **Project Manager (PM)** provides direction, coordination, and oversight.
2. **Project Teams** implement solutions based on directives and respond to coordinated requests.

This separation must be strictly maintained to ensure effective project governance.

## Project Manager Boundaries

### The PM MUST:

1. Operate exclusively through the MultiMindPM directory
2. Influence projects only through formal channels:
   - Directives
   - Advisory responses
   - Handoff coordination
   - Roadmap updates
   - Rules and standards
3. Review and process completion reports
4. Maintain the master roadmap
5. Coordinate cross-project dependencies

### The PM MUST NOT:

1. Directly modify code or files in project directories
2. Implement features on behalf of project teams
3. Bypass the formal communication channels
4. Take over implementation details that should be decided by project teams
5. Modify project status reports (other than formatting)

## Project Team Boundaries

### Project Teams MUST:

1. Implement features according to directives
2. Report status accurately and promptly
3. Use advisories to request PM guidance
4. Use handoffs to coordinate with other projects
5. Report phase completions following the established protocol
6. Follow established rules and standards

### Project Teams MUST NOT:

1. Modify files in the MultiMindPM directory
2. Modify directives or roadmaps directly
3. Modify files in other projects' directories
4. Change the MultiMind orchestration tool without PM approval
5. Bypass the formal communication channels

## Communication Channels

All communication between the PM and project teams must flow through these formal channels:

1. **Directives**: PM → Project Teams
2. **Status Reports**: Project Teams → PM
3. **Advisories**: Project Teams → PM → Project Teams
4. **Handoffs**: Project Teams → PM → Project Teams
5. **Completion Reports**: Project Teams → PM

## Boundary Violations

If a boundary violation occurs:

1. Document the violation in a special advisory
2. Revert any changes that crossed boundaries
3. Use the correct channel to accomplish the intended goal
4. Update documentation if the violation revealed a gap in the formal channels

## Rationale

These boundaries serve several critical purposes:

1. **Clarity of Responsibility**: Clear boundaries prevent confusion about who should perform specific tasks
2. **Quality Control**: The PM can ensure consistent quality across all projects
3. **Integration Management**: Formal channels ensure that cross-project dependencies are properly managed
4. **Knowledge Preservation**: Proper channels create clear records of decisions and their rationale
5. **Architectural Integrity**: Prevents ad-hoc changes that might compromise the overall system architecture 