# MultiMind - Project Orchestration Tool

Version: 0.2.0

## Overview

MultiMind is a local orchestration tool for coordinating multiple projects that depend on one another. It syncs roadmaps, READMEs, directives, rules, and status reports between a Project Manager (PM) directory and multiple development directories.

## Implementation Example

This implementation can be used with any set of interdependent projects. The example configuration includes three sample projects:

1. **ProjectOne**: First component in the workflow
2. **ProjectTwo**: Second component that consumes ProjectOne's output
3. **ProjectThree**: Final component that integrates all components

The data flows from ProjectOne → ProjectTwo → ProjectThree, creating a complete workflow pipeline.

## Directory Structure

```
/MultiMindPM/                      # Project Manager directory
  ├── config.json                  # Configuration for project paths and files
  ├── roadmap.md                   # Master project roadmap
  ├── README.md                    # This file
  ├── .cursor-ai-instructions.md   # Instructions for the PM AI agent
  ├── directives/                  # Specific tasks for each subproject
  │     ├── project_one.md
  │     ├── project_two.md
  │     └── project_three.md
  ├── reports/                     # Status reports collected from each project
  │     ├── project_one-status.md
  │     ├── project_two-status.md
  │     └── project_three-status.md
  ├── rules/                       # Coding standards and protocols
  │     ├── coding_standards.md
  │     ├── handoff_protocol.md
  │     ├── status_format.md
  │     └── roadmap_updates.md
  ├── handoffs/                    # Inter-project coordination requests
  │     └── [date]-[from]_[to]-[description].md
  └── .cursor-ai-templates/        # Templates for AI instructions
        ├── ProjectOne-ai-instructions.md
        ├── ProjectTwo-ai-instructions.md
        └── ProjectThree-ai-instructions.md

Each project directory has a similar structure with their own files synced from the PM.
```

## Commands

MultiMind provides the following commands:

### Sync

Pushes master roadmap, README, rules, and directives to each subproject:

```bash
./multimind.py sync
```

### Gather

Collects status reports from each subproject back to the PM directory:

```bash
./multimind.py gather
```

### Handoffs

Processes and tracks inter-project coordination requests:

```bash
./multimind.py handoffs
```

### Init

Initializes a new project with the standard directory structure:

```bash
./multimind.py init ProjectName
```

## How It Works

### Core Functionality

1. The config.json file defines which projects are managed and their paths
2. The `sync` command distributes central documents to each project
3. The `gather` command collects status reports from each project
4. The `handoffs` command processes inter-project coordination
5. Each subproject maintains its own copy of relevant documents

### AI Agent Integration

MultiMind includes special `.cursor-ai-instructions.md` files in each project directory that:

1. Provide immediate context to AI agents about their role in the system
2. Direct agents to relevant files and directories
3. Explain how to update status reports and create handoffs
4. Define boundaries between projects

### Project Coordination

1. **Directives**: PM defines tasks in directive files
2. **Status Reports**: Projects report progress in standardized format
3. **Handoffs**: Projects request changes from other components via handoff protocol
4. **Rules**: All projects follow shared coding standards and protocols

## Getting Started

1. Ensure all project directories exist (or create with `init`)
2. Run `./multimind.py sync` to distribute initial files
3. Make changes to projects according to rules and directives
4. Update status.md in each project following the format in rules
5. Create handoffs when cross-project changes are needed
6. Run `./multimind.py gather` to collect status reports
7. Run `./multimind.py handoffs` to process handoff requests 