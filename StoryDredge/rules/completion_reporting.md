# Project Completion Reporting Protocol

Version: 0.2.0

## Overview

This document defines the standardized protocol for reporting project phase completions to the Project Manager. This ensures the PM can accurately track progress and coordinate work across projects.

**IMPORTANT: This protocol applies to ALL project phases, not just Phase 1. The same process should be followed for every phase completion.**

## Completion Report Structure

When a project completes a significant phase or all current directives, the project team should:

1. Update their `status.md` file with completed items
2. Create a special completion marker file

## Completion Marker Format

Completion markers are stored as Markdown files in the following location:

```
/output/completions/[ProjectName]-[PhaseIdentifier]-complete.md
```

Example: `output/completions/ProjectOne-Phase1-complete.md`

## Completion Marker Content

Each completion marker file must follow this structure:

```markdown
# Project Completion: [ProjectName] - [PhaseID]

Version: 0.1.0
Completed: [YYYY-MM-DD]
Project: [ProjectName]
Phase: [PhaseID]

## Completed Directives

* [List of completed directives with brief descriptions]
* [Include reference to specific tasks that were implemented]

## Deliverables

* [List of key deliverables produced]
* [Include file paths, API endpoints, or other relevant references]

## Known Issues

* [Any known limitations or issues that remain]
* [Include any technical debt incurred]

## Notes

[Any additional notes or context about the implementation]

## Next Phase

[Suggestions or requirements for the next phase]
```

## Completion Reporting Process

To report a phase completion:

1. **Create the completion marker file** in the `output/completions/` directory following the format above
2. **Update your project's status report** with the latest status
3. **Run the completion command** using one of the following methods:
   
   a. From the root directory:
   ```bash
   ./multimind.py complete [ProjectName] [PhaseID]
   ```
   
   b. From your project directory:
   ```bash
   python scripts/complete_phase.py [PhaseID]
   ```

4. **Wait for PM review** - The PM will review your completion and:
   - Archive the completed phase materials
   - Update the roadmap
   - Provide directives for the next phase

## Phase Identifier Conventions

Phase identifiers should follow one of these formats:

- Sequential numbering: `Phase1`, `Phase2`, `Phase3`
- Semantic versioning: `v0.1`, `v0.2`, `v1.0`
- Feature-based: `AuthFeature`, `DataProcessing`, `UILayer`

Be consistent with the phase naming convention used in your project directives.

## Important Notes

- This protocol applies to **ALL phases** of your project, not just the first phase
- Always create the completion marker file before running the completion command
- Ensure the status report is up-to-date before reporting completion
- Always list all completed items and deliverables in the marker file
- Use the local completion script from your project directory for convenience
- If you're unsure whether to report completion, consult with the PM through an advisory

## Example Completion Marker

```markdown
# Project Completion: DataProcessor - Phase2

Version: 0.1.0
Completed: 2025-06-12
Project: DataProcessor
Phase: Phase2

## Completed Directives

* Implemented stream processing for real-time data analysis
* Added support for CSV and JSON input formats
* Created data validation module with schema enforcement
* Implemented error handling and retry mechanisms
* Added performance metrics collection

## Deliverables

* Stream processor module: src/processor/stream_processor.py
* Format converters: src/converters/csv.py, src/converters/json.py
* Validation engine: src/validation/engine.py
* Error handling framework: src/utils/error_handling.py
* Metrics collector: src/metrics/collector.py

## Known Issues

* CSV parser has limited support for escape characters
* Large files (>1GB) may cause memory issues during processing
* Performance metrics are collected but not yet visualized

## Notes

The stream processor implementation follows the reactive design pattern
and can be easily extended to support additional input formats.

## Next Phase

The next phase should focus on:
* Addressing the memory usage issues
* Implementing a metrics visualization dashboard
* Adding support for additional input formats (XML, Parquet)
```

## PM Response Process

After receiving a completion notification, the PM will:

1. Review the completion marker and status report
2. Update the master roadmap to reflect the completion
3. Provide new directives for the next phase if appropriate
4. Sync the updated roadmap and directives to all projects 