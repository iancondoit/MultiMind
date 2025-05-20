# MultiMind

Version: 0.2.0

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

## Directory Structure

```
/MultiMindPM/                      # Project Manager directory
  ├── config.json                  # Configuration for project paths and files
  ├── roadmap.md                   # Master project roadmap
  ├── README.md                    # Project overview
  ├── .cursor-ai-instructions.md   # Instructions for the PM AI agent
  ├── directives/                  # Specific tasks for each subproject
  ├── reports/                     # Status reports collected from each project
  ├── rules/                       # Coding standards and protocols
  ├── handoffs/                    # Inter-project coordination requests
  └── .cursor-ai-templates/        # Templates for AI instructions
```

## Commands

```bash
# Push documents from PM to subprojects
./multimind.py sync

# Collect status reports from subprojects
./multimind.py gather

# Process and track inter-project handoffs
./multimind.py handoffs

# Initialize a new project with standard structure
./multimind.py init ProjectName
```

## Getting Started

1. Clone this repository
2. Configure project directories in `MultiMindPM/config.json`
3. Create directives for each project in `MultiMindPM/directives/`
4. Run `./multimind.py sync` to distribute files
5. For each project, implement required functionality
6. Update status reports in each project
7. Run `./multimind.py gather` to collect status updates
8. Use handoffs for inter-project coordination

## AI Integration

MultiMind includes special support for AI coding assistants:

- `.cursor-ai-instructions.md` files provide context and guidance to AI agents
- Each project directory includes AI onboarding instructions
- AI agents can understand their role in the larger system
- Communication protocols for cross-project coordination are standardized

## License

This project is licensed under the GPL-3.0 License - see the LICENSE file for details.
