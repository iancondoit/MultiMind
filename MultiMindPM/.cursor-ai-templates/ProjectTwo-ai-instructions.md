# ProjectTwo Developer Instructions

You are working on the **ProjectTwo** subproject, which is part of the larger system managed by MultiMind.

## Your Role

You are responsible for creating the second component in the data processing pipeline that:
1. Takes structured data from ProjectOne
2. Performs analysis and transformation
3. Outputs processed data in JSON format

## Important Files to Understand

- `/directives/project_two.md`: Contains your current tasks and requirements
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

The input to your work comes from `/output/data.json` (created by ProjectOne), and your output (`/output/processed.json`) will be consumed by the ProjectThree module.

## Process

1. Read `/directives/project_two.md` for your current tasks
2. Read `/rules/` to understand coding standards and processes
3. Implement the required functionality according to the specifications
4. Update `/reports/status.md` with your progress
5. For integration with other components:
   - Create handoff documents in `/output/handoffs/` if you need changes to the input format
   - Follow the API contracts described in your directive 