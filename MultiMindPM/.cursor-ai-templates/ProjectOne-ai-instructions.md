# ProjectOne Developer Instructions

You are working on the **ProjectOne** subproject, which is part of the larger system managed by MultiMind.

## Your Role

You are responsible for creating the first component in the data processing pipeline that:
1. Takes user input data
2. Converts it to structured JSON format

## Important Files to Understand

- `/directives/project_one.md`: Contains your current tasks and requirements
- `/reports/status.md`: Where you should document your progress
- `/rules/`: Contains coding standards and protocols
- `/roadmap.md`: The project roadmap (do not edit directly)

## MultiMind Integration

This project is managed through the MultiMind orchestration system:

- **Directives**: Your tasks are defined in the PM directory and synced to this project
- **Status Reporting**: Update `/reports/status.md` to report progress
- **File Structure**: Don't modify `/directives` files - they're managed by MultiMind
- **Rules**: Follow the standards in the `/rules/` directory
- **Handoffs**: Use the handoff protocol for requesting changes from other components

The output of your work (`/output/data.json`) will be consumed by the ProjectTwo module.

## Process

1. Read `/directives/project_one.md` for your current tasks
2. Read `/rules/` to understand coding standards and processes
3. Implement the required functionality according to the specifications
4. Update `/reports/status.md` with your progress
5. For integration with other components:
   - Create handoff documents in `/output/handoffs/` following the format in `/rules/handoff_protocol.md`
   - Follow the API contracts described in your directive

## Completion Reporting

**IMPORTANT**: When you complete a task or milestone from your directives:

1. Update your `/reports/status.md` file with:
   - Mark task as complete
   - Update "Last Update" date
   - Add details in "Current Progress" section
   - Update "Next Steps" section

2. **NOTIFY THE PM** by running:
   ```bash
   cd ..
   ./multimind.py gather
   ```

3. Include in your response to the user that you've updated the status report and notified the PM. For example:
   ```
   I've completed [task] and updated the status report. The PM has been notified via the MultiMind gather command.
   ```

This reporting process ensures the Project Manager is immediately aware of your progress. 