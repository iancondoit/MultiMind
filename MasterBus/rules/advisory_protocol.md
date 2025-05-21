# PM-Project Advisory Protocol

Version: 0.1.0
Created: 2025-05-22

## Overview

This document defines the standardized protocol for advisory communications between the Project Manager (PM) and individual projects in the MultiMind system. Advisories allow projects to ask questions and get guidance from the PM to resolve blockers and clarify requirements.

## Advisory File Structure

Advisories are stored as Markdown files in the following locations:

1. **PM Advisory Directory**: `/MultiMindPM/advisories/{project_name}/`
   - Contains all advisories organized by project
   - Named format: `NNN-brief-description.md` (where NNN is a sequential number)
   - Example: `001-technology-stack-guidance.md`

2. **Project Advisory Directory**: `/{project_name}/advisories/`
   - Contains advisories relevant to the specific project
   - Uses the same naming convention as PM advisories

## Advisory Document Format

Each advisory document must follow this structure:

```markdown
# Advisory: [Brief Description]

Version: [version]
Status: [ASKED | ANSWERED | RESOLVED]
Project: [Project Name]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]

## Question

[Project's question or blocker description]

## Context

[Background information explaining why this is needed]

## Response

[To be filled by the PM]

## Resolution

[Actions taken based on the advisory]
```

## Advisory Process

1. **Question Submission**
   - Project identifies a blocker or needs guidance
   - Creates an advisory document in their project advisory directory
   - Sets status to "ASKED"
   - Includes clear question and context
   - The document gets synced to the PM directory during gather

2. **PM Response**
   - PM reviews the advisory
   - Provides detailed guidance in the "Response" section
   - Updates status to "ANSWERED"
   - The document gets synced back to the project directory during sync

3. **Resolution**
   - Project implements the guidance
   - Documents the actions taken in the "Resolution" section
   - Updates status to "RESOLVED"
   - The document gets synced back to the PM directory during gather

## Advisory Lifecycle

```
ASKED → ANSWERED → RESOLVED
```

## Example Advisory

```markdown
# Advisory: Technology Stack Selection

Version: 0.1.0
Status: ANSWERED
Project: ProjectOne
Created: 2023-06-15
Last Updated: 2023-06-16

## Question

What technology stack should be used for ProjectOne?

## Context

We need to decide on a technology stack for ProjectOne implementation. The choice will affect performance, maintenance, and integration capabilities.

## Response

Based on the project requirements, use the following stack:

1. **Backend**: Node.js with Express
   - Good performance for API development
   - Large ecosystem of libraries
   - Easy to integrate with data sources

2. **Database**: MongoDB
   - Schema flexibility for evolving data structures
   - High read performance for our use case
   - Simple setup and maintenance

3. **Frontend**: React with TypeScript
   - Type safety reduces bugs
   - Component reusability
   - Good performance for interactive interfaces

## Resolution

Implemented the recommended technology stack. Created initial project setup with Node.js, Express, MongoDB, and React with TypeScript. Set up development environment with Docker for consistent deployment.
```

## Important Notes

- Always raise advisories for blockers identified in status reports
- Keep advisories focused on a single question or related set of questions
- Include sufficient context to explain why the guidance is needed
- Document detailed resolution actions for knowledge sharing
- Use the sync/gather process to keep advisories updated between PM and projects 