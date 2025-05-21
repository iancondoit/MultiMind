# MultiMind

Version: 0.6.1

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
- **Advisory Protocol**: Formalized Q&A mechanism between projects and PM
- **Project History and Archiving**: Comprehensive tracking of project phases and decisions
- **Local Completion Scripts**: Project-specific scripts for reporting phase completions
- **Clear Project Boundaries**: Defined operational boundaries between PM and project teams
- **PM Workflow Formalization**: Standardized processes for PM responsibilities
- **Enhanced User Experience**: Intuitive command output with emoji indicators and actionable guidance
- **Robust Template System**: Standardized template handling with placeholders
- **Improved Project Filtering**: Better distinction between template and active projects

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
  ├── advisories/                  # PM-Project communication channel
  ├── archives/                    # Historical project phase materials
  └── templates/                   # Templates for various documents
        ├── advisories/            # Templates for advisory documents
        ├── archives/              # Templates for archiving
        ├── decisions/             # Templates for decision tracking
        └── complete_phase.py      # Template for completion scripts

/output/                           # Shared output directory
  ├── completions/                 # Completion markers from projects
  └── handoffs/                    # Handoff requests between projects

/ProjectName/                      # Individual project directories
  ├── directives/                  # Project-specific directives
  ├── reports/                     # Status reports
  ├── rules/                       # Shared coding standards
  ├── advisories/                  # Project-PM communication channel
  ├── scripts/                     # Project-specific utility scripts
  ├── src/                         # Project source code
  └── ...                          # Other project-specific directories
```

## Commands

```bash
# Set up all required directories
./multimind.py setup

# Initialize a new project with standard structure
./multimind.py init ProjectName

# Push documents from PM to subprojects
./multimind.py sync

# Collect status reports from subprojects
./multimind.py gather

# Process and track inter-project handoffs
./multimind.py handoffs

# Process project phase completion reports
./multimind.py complete [project_name] [phase_id] [--only-project]

# Process advisories between PM and projects
./multimind.py advisories

# Archive a completed phase
./multimind.py archive [project_name] [phase_id]

# Create completion scripts for projects
./multimind.py create-scripts [--project ProjectName]

# Display version information
./multimind.py version
```

## Getting Started

1. Clone this repository
2. Run `./multimind.py setup` to create the necessary directory structure
3. Configure project directories in `MultiMindPM/config.json`
4. Create directives for each project in `MultiMindPM/directives/`
5. (Optional) Create project-specific roadmaps in `MultiMindPM/roadmaps/`
6. Run `./multimind.py sync` to distribute files
7. For each project, implement required functionality
8. Update status reports in each project
9. Run `./multimind.py gather` to collect status updates
10. Use handoffs for inter-project coordination
11. Report phase completions with `./multimind.py complete`

## Completion Reporting

MultiMind includes a robust completion reporting system that allows projects to notify the Project Manager when they complete a phase:

1. When a project finishes a significant phase, it creates a completion marker file in the `/output/completions/` directory
2. The marker follows a standardized format defined in `/MultiMindPM/rules/completion_reporting.md`
3. The project then runs `./multimind.py complete [ProjectName] [PhaseID]` to notify the PM
4. The PM reviews the completion, updates the roadmap, and provides new directives
5. Project-specific roadmaps can be created in `MultiMindPM/roadmaps/projectname_roadmap.md`
6. Each project has a local script at `scripts/complete_phase.py` for convenience

## Advisory Protocol

MultiMind implements a formalized advisory protocol for communication between projects and the PM:

1. A project creates an advisory document in their `/advisories/` directory
2. The advisory is synced to the PM during `gather`
3. The PM responds in the `Response` section of the advisory
4. The updated advisory is synced back to the project during `sync`
5. The project team resolves the advisory based on PM guidance

## Project History and Archiving

MultiMind provides comprehensive tracking of project history:

1. When a phase is completed, all relevant materials are automatically archived
2. Archives are stored in `/MultiMindPM/archives/[ProjectName]/[PhaseID]/`
3. Each archive includes directives, completion reports, status reports, and advisories
4. A phase summary document is created for the PM to document key insights and decisions

## AI Integration

MultiMind includes special support for AI coding assistants:

- `.cursor-ai-instructions.md` files provide context and guidance to AI agents
- Each project directory includes AI onboarding instructions
- AI agents can understand their role in the larger system
- Communication protocols for cross-project coordination are standardized
- Advisory protocol for requesting PM guidance on architectural decisions
- Boundary enforcement prevents accidental changes outside project scope

## Example Use Case

MultiMind is designed for situations where multiple components need to work together as part of a larger system:

- **Data Processing Pipeline**: One project generates data, another processes it, and a third visualizes the results
- **Microservices Architecture**: Multiple services each with a specific responsibility that need to interact
- **AI Systems**: Components for data preparation, model training, inference, and user interface working together

The system ensures that all components understand their responsibilities, interfaces, and dependencies.

## Extending MultiMind

To use MultiMind for your own projects:

1. Fork this repository
2. Run `./multimind.py setup` to initialize the directory structure
3. Create your own projects with `./multimind.py init ProjectName`
4. Update the configuration in `MultiMindPM/config.json`
5. Create appropriate directives and roadmaps for your projects
6. Follow the established protocols for handoffs, advisories and completion reporting

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.
