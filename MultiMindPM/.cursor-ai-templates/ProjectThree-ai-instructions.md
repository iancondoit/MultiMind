# ProjectThree Developer Instructions

You are working on the **ProjectThree** subproject, which is part of the larger system managed by MultiMind.

## Your Role

You are responsible for creating the final component in the data processing pipeline that:
1. Takes structured data from ProjectOne
2. Takes processed data from ProjectTwo
3. Generates formatted output for presentation

## Important Files to Understand

- `/directives/project_three.md`: Contains your current tasks and requirements
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

The inputs to your work come from `/output/data.json` (created by ProjectOne) and `/output/processed.json` (created by ProjectTwo). Your output is `/output/output.md`, the final product of the processing pipeline.

## Process

1. Read `/directives/project_three.md` for your current tasks
2. Read `/rules/` to understand coding standards and processes
3. Implement the required functionality according to the specifications
4. Update `/reports/status.md` with your progress
5. For integration with other components:
   - Create handoff documents in `/output/handoffs/` if you need changes to the input formats
   - Follow the API contracts described in your directive 