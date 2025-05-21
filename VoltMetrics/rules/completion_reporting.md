# Project Completion Reporting Protocol

Version: 0.1.0

## Overview

This document defines the standardized protocol for reporting project phase completions to the Project Manager. This ensures the PM can accurately track progress and coordinate work across projects.

## Completion Report Structure

When a project completes a significant phase or all current directives, the project team should:

1. Update their `status.md` file with completed items
2. Create a special completion marker file

## Completion Marker Format

Completion markers are stored as Markdown files in the following location:

```
/output/completions/[ProjectName]-[PhaseIdentifier]-complete.md
```

Example: `output/completions/IngredientEngine-Phase1-complete.md`

## Completion Marker Content

Each completion marker file must follow this structure:

```markdown
# Project Completion: [Project Name] - [Phase/Task Identifier]

Version: [version]
Completed: [YYYY-MM-DD]
Project: [Project Name]
Phase: [Phase Name or Identifier]

## Completed Directives

* [Directive 1 description]
* [Directive 2 description]
* ...

## Notes

[Any additional information about the completion]

## Next Phase

[Brief description of what comes next, if known]
```

## Reporting Process

1. **Update Status**
   - Update your project's `reports/status.md` file with completed items
   - Mark all relevant tasks as completed

2. **Create Completion Marker**
   - Create the completion marker file in your project directory
   - Copy it to the `output/completions/` directory

3. **Notification Command**
   - Run the completion notification command:
   ```bash
   ./multimind.py complete [ProjectName] [PhaseIdentifier]
   ```
   - This will notify the PM of your completion

4. **Wait for PM Acknowledgment**
   - The PM will acknowledge the completion
   - The PM will update the roadmap and provide new directives
   - Run `./multimind.py sync` to receive updated directives

## Example Completion Report

```markdown
# Project Completion: IngredientEngine - Phase1

Version: 0.1.0
Completed: 2023-06-20
Project: IngredientEngine
Phase: Foundation

## Completed Directives

* Implemented prompt-to-recipe converter
* Created JSON schema for recipe output
* Added basic validation for ingredient format
* Wrote unit tests for core functionality

## Notes

All tests are passing with 92% code coverage. The implementation handles basic recipe requirements but will need enhancement in Phase 2 for more complex dietary restrictions.

## Next Phase

Ready to begin work on advanced parsing features and integration with external recipe databases.
```

## PM Response Process

After receiving a completion notification, the PM will:

1. Review the completion marker and status report
2. Update the master roadmap to reflect the completion
3. Provide new directives for the next phase if appropriate
4. Sync the updated roadmap and directives to all projects 