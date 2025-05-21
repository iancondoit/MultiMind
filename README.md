# MultiMind

Version: 0.3.1

A modular orchestration tool for coordinating multiple, interdependent software projects with AI agent support.

## Overview

MultiMind synchronizes requirements, roadmaps, status reports, and coding standards across multiple project directories, creating a coordinated development environment. It's designed specifically to enhance collaboration between AI agents or human developers working on separate but related components.

## Features

- **Central Project Management**: Coordinate multiple projects from a single PM directory
- **Automated File Synchronization**: Distribute requirements and collect status reports
- **Inter-Project Communication**: Formalized handoff protocol for cross-project requests
- **Standardized Rules**: Shared coding standards and protocols across projects
- **AI Agent Integration**: Specialized instructions for AI coding assistants in each project
- **Project Initialization**: Quickly scaffold new projects with correct structure
- **Completion Reporting**: Formalized process for reporting project phase completions
- **Project-Specific Roadmaps**: Support for individual project roadmaps alongside the main roadmap

## Directory Structure

```
/MultiMindPM/                      # Project Manager directory
  ├── config.json                  # Configuration for project paths and files
  ├── roadmap.md                   # Master project roadmap
  ├── roadmaps/                    # Project-specific roadmaps
  ├── README.md                    # Project overview
  ├── .cursor-ai-instructions.md   # Instructions for the PM AI agent
  ├── directives/                  # Specific tasks for each subproject
  ├── reports/                     # Status reports collected from each project
  ├── rules/                       # Coding standards and protocols
  ├── handoffs/                    # Inter-project coordination requests
  ├── completions/                 # Project phase completion reports
  └── .cursor-ai-templates/        # Templates for AI instructions

/output/                           # Shared output directory
  ├── completions/                 # Completion markers from projects
  └── handoffs/                    # Handoff requests between projects

/ProjectName/                      # Individual project directories
  ├── directives/                  # Project-specific directives
  ├── reports/                     # Status reports
  ├── rules/                       # Shared coding standards
  ├── src/                         # Project source code
  └── ...                          # Other project-specific directories
```

## Commands

```bash
# Push documents from PM to subprojects
./multimind.py sync

# Collect status reports from subprojects
./multimind.py gather

# Process and track inter-project handoffs
./multimind.py handoffs

# Process project phase completion reports
./multimind.py complete [project_name] [phase_id]

# Initialize a new project with standard structure
./multimind.py init ProjectName
```

## Getting Started

1. Clone this repository
2. Configure project directories in `MultiMindPM/config.json`
3. Create directives for each project in `MultiMindPM/directives/`
4. (Optional) Create project-specific roadmaps in `MultiMindPM/roadmaps/`
5. Run `./multimind.py sync` to distribute files
6. For each project, implement required functionality
7. Update status reports in each project
8. Run `./multimind.py gather` to collect status updates
9. Use handoffs for inter-project coordination
10. Report phase completions with `./multimind.py complete`

## Completion Reporting

MultiMind includes a robust completion reporting system that allows projects to notify the Project Manager when they complete a phase:

1. When a project finishes a significant phase, run the completion command **from the root directory**:
   ```
   ./multimind.py complete [ProjectName] [PhaseID]
   ```

2. Important: The multimind.py command must be run from the root directory of the workspace, not from your project directory.

3. This will:
   - Create a completion marker in the PM's completions directory
   - Copy your latest status report to the PM
   - Signal to the PM that you're ready for the next phase

4. The PM will then:
   - Review the completion and status report
   - Update the roadmap and directives
   - Sync the updated directives back to your project

5. If your project has a specific roadmap, it will be updated in `MultiMindPM/roadmaps/projectname_roadmap.md`

6. Detailed completion reporting instructions are included in each project's directives file.

## AI Integration

MultiMind includes special support for AI coding assistants:

- `.cursor-ai-instructions.md` files provide context and guidance to AI agents
- Each project directory includes AI onboarding instructions
- AI agents can understand their role in the larger system
- Communication protocols for cross-project coordination are standardized
- Completion reporting process for notifying the PM of completed phases

## Example Use Case

MultiMind is designed for situations where multiple components need to work together as part of a larger system:

- **Data Processing Pipeline**: One project generates data, another processes it, and a third visualizes the results
- **Microservices Architecture**: Multiple services each with a specific responsibility that need to interact
- **AI Systems**: Components for data preparation, model training, inference, and user interface working together

The system ensures that all components understand their responsibilities, interfaces, and dependencies.

## Extending MultiMind

To use MultiMind for your own projects:

1. Fork this repository
2. Create your own projects with `./multimind.py init ProjectName`
3. Update the configuration in `MultiMindPM/config.json`
4. Create appropriate directives and roadmaps for your projects
5. Follow the established protocols for handoffs and completion reporting

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.
