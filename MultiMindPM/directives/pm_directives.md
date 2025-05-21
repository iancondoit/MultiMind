# Project Manager Directives

Version: 1.0.0
Created: 2025-05-23
Updated: 2025-05-24

## Overview

This document outlines the Project Manager's responsibilities and processes for managing the MultiMind project ecosystem. It formalizes the workflow for handling phase completions, responding to advisories, and updating project directives.

## Core Responsibilities

1. **Phase Completion Management**
   - Monitor and process project phase completions
   - Review status reports for completeness and quality
   - Address blockers and questions raised during completion
   - Update directives for the next phase

2. **Advisory Response System**
   - Review and respond to advisories from project teams
   - Create new advisories when necessary to provide guidance
   - Ensure responses align with overall project architecture and goals
   - Sync advisory responses to project repositories

3. **Directive Maintenance**
   - Keep project directives updated with current status and tasks
   - Ensure directives clearly specify completion reporting requirements
   - Align directives with the overall project roadmap
   - Incorporate lessons learned from previous phases

4. **Cross-Project Coordination**
   - Facilitate communication between dependent projects
   - Ensure API contracts and integration points are clearly defined
   - Identify and address potential conflicts between projects
   - Manage project dependencies and timelines

5. **Boundary Enforcement**
   - Strictly adhere to project boundaries as defined in the rules
   - Never work directly on code in project subdirectories
   - Only operate through established communication channels
   - Refer to `MultiMindPM/rules/project_boundaries.md` for complete boundary definitions

## Phase Completion Management Process

### 1. Monitor Phase Completion

- Run weekly check for new completion reports:
  ```
  ./multimind.py gather
  ```

- Check the MultiMindPM/completions directory for new completion markers
- Review completion dates and ensure they align with the project timeline

### 2. Review Project Status

For each completed phase:

- Review the status report in MultiMindPM/reports/{project}-status.md
- Check for:
  - Completed tasks aligned with directives
  - Quality of implementation and documentation
  - Test coverage and validation
  - Remaining blockers or questions
  - Alignment with project timeline
  - Integration with dependent projects

### 3. Address Blockers and Questions

If blockers or questions are identified:

- Create advisory responses in the appropriate project advisory directory:
  ```
  MultiMindPM/advisories/{project_name}/{advisory-name}.md
  ```

- Structure advisories according to the established format:
  ```markdown
  # Advisory: [Brief Description]

  Version: [version]
  Status: ANSWERED
  Project: [Project Name]
  Created: [YYYY-MM-DD]
  Last Updated: [YYYY-MM-DD]

  ## Question
  [Project's question or blocker description]

  ## Context
  [Background information explaining why this is needed]

  ## Response
  [Your detailed response]

  ## Resolution
  [Expected actions based on the advisory]
  ```

- Ensure advisories provide clear, actionable guidance
- Reference related documentation or external resources when appropriate
- Address technical questions with concrete examples

### 4. Update Project Directives

- Update the project's directive file for the next phase:
  ```
  MultiMindPM/directives/{project}_directives.md
  ```

- Include:
  - Clear acknowledgment of completed phase
  - Detailed tasks for the next phase
  - Implementation guidelines
  - Dependencies and integration requirements
  - Clear completion reporting instructions

### 5. Sync Updates to Projects

- Distribute updates to all projects:
  ```
  ./multimind.py sync
  ```

- Confirm that advisories and updated directives are properly synced
- Monitor for project feedback on the updates

## Advisory Management Process

### 1. Regular Advisory Checks

- Check for new advisories at least twice weekly:
  ```
  ./multimind.py gather
  ./multimind.py advisories
  ```

- Review new advisories in order of creation date
- Prioritize advisories that block project progress

### 2. Advisory Response Framework

- For technology questions:
  - Provide specific recommendations with reasoning
  - Include code examples when appropriate
  - Reference industry best practices and standards
  - Consider future scalability and maintenance

- For integration questions:
  - Define clear API contracts and data formats
  - Specify authentication and security requirements
  - Document communication patterns (sync/async)
  - Coordinate with both sides of the integration

- For architecture questions:
  - Align recommendations with overall system design
  - Consider performance, scalability, and maintainability
  - Document trade-offs and reasoning
  - Provide diagrams when helpful

- For timeline/scope questions:
  - Align with project roadmap
  - Consider dependencies between projects
  - Set realistic expectations
  - Document risk factors

### 3. Update and Sync

- After creating or updating advisories:
  ```
  ./multimind.py sync
  ```

- Ensure timely delivery of responses
- Check that project teams have received and implemented guidance

## Directive Maintenance Best Practices

1. **Clear Phase Delineation**
   - Clearly mark current and completed phases
   - Set explicit criteria for phase completion
   - Include completion reporting instructions in every phase

2. **Task Specificity**
   - Break down tasks into manageable components
   - Specify acceptance criteria for each task
   - Link tasks to overall project goals

3. **Integration Guidance**
   - Specify interfaces between components
   - Document communication protocols
   - Define data formats and validation requirements

4. **Timeline Management**
   - Set realistic phase durations
   - Account for dependencies between projects
   - Allow buffer for unexpected challenges

5. **Completion Instructions**
   - Include a dedicated "Completion Reporting" section
   - Specify the exact command to run:
     ```
     ./multimind.py complete [ProjectName] [PhaseID]
     ```
   - Emphasize that commands must be run from the root directory

## Project Manager Checklist

### Daily
- Check for new advisories
- Monitor project status updates
- Respond to urgent queries

### Weekly
- Process any phase completions
- Create advisory responses
- Update project directives as needed
- Sync updates to projects
- Review project progress against roadmap

### Monthly
- Conduct holistic review of all projects
- Update roadmap if necessary
- Document lessons learned
- Identify process improvements

## Example Workflow

1. **Project completes a phase**
   - Team runs: `./multimind.py complete ProjectName phase1`
   - Completion marker created in MultiMindPM/completions

2. **PM reviews completion**
   - Run: `./multimind.py gather`
   - Review status report for blockers and questions
   - Check implementation quality and documentation

3. **PM addresses blockers via advisories**
   - Create advisory responses in MultiMindPM/advisories/ProjectName/
   - Provide detailed technical guidance and next steps

4. **PM updates directives for next phase**
   - Update the project's directive file with new tasks
   - Include clear completion reporting instructions
   - Ensure alignment with overall roadmap

5. **PM distributes updates**
   - Run: `./multimind.py sync`
   - Project team receives updated directives and advisory responses
   - Project begins next phase

This workflow ensures a smooth transition between phases and provides clear guidance to project teams throughout the development process. 