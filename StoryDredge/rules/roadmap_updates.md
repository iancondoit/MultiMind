# Roadmap Update Guidelines

Version: 0.1.0

## Overview

This document defines the process for updating the project roadmap in the MultiMind system. The roadmap is a critical document that guides all development efforts and must be kept current.

## Roadmap Structure

The roadmap follows this structure:

```markdown
# MultiMind Project Roadmap

Version: [version]

## Project Timeline

### Phase 1: [Name] ([Status])
- [x] Completed task
- [ ] Incomplete task

### Phase 2: [Name] ([Status])
- [ ] Future task

## Data Flow Architecture

[Diagram showing data flow between components]

## Milestones

1. **[Milestone 1]**
   - [Requirements]

## Current Focus

[Description of current priorities]
```

## Update Process

### For Project Teams

1. **Propose Changes**
   - Create a status report that includes suggested roadmap updates
   - Use the "Next Steps" section to indicate future work
   - Mark completed items in the "Current Progress" section

2. **Do Not Edit Directly**
   - Never modify the roadmap.md directly in your project repository
   - All changes must go through the PM

### For Project Manager

1. **Review Status Reports**
   - Collect status reports using `./multimind.py gather`
   - Review progress against current roadmap

2. **Update Master Roadmap**
   - Modify `/MultiMindPM/roadmap.md` with completed tasks and new tasks
   - Update the status of phases and milestones
   - Increment the version number

3. **Distribute Updates**
   - Run `./multimind.py sync` to push the updated roadmap to all projects
   - Consider notifying teams of significant roadmap changes

## Task Status Marking

- Use the following markdown format for tasks:
  - `- [ ]` for incomplete tasks
  - `- [x]` for completed tasks
  - `- [~]` for in-progress tasks (optional)

## Phase Status Indicators

Phase status should be one of:
- `(Planning)` - In planning stage
- `(Current)` - Active development
- `(Review)` - Completing final items
- `(Complete)` - All tasks finished
- `(On Hold)` - Temporarily paused

## Example Roadmap Update

Original:
```markdown
### Phase 1: Foundation (Current)
- [x] Set up project structure
- [ ] Develop basic MultiMind tool
- [ ] Create scaffolds for subprojects
```

Updated:
```markdown
### Phase 1: Foundation (Review)
- [x] Set up project structure
- [x] Develop basic MultiMind tool
- [x] Create scaffolds for subprojects
- [ ] Review directory structure
```

## Communicating Changes

When making significant roadmap updates:

1. Create a handoff document explaining the changes
2. Highlight shifts in priorities or timelines
3. Note any changes to API contracts or integration points
4. Ensure all teams acknowledge the updates

## Roadmap-Status Report Alignment

The roadmap should always align with the combined information in status reports. If there are discrepancies:

1. Prioritize actual progress reported in status reports
2. Update the roadmap to reflect reality, not aspirations
3. Document reasons for significant deviations 