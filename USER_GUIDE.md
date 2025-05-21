# MultiMind User Guide

Version: 0.6.1

## Introduction

MultiMind is a project orchestration tool designed to coordinate multiple interdependent software projects. Whether you're managing a team of developers or a group of AI agents, MultiMind provides the structure and protocols needed for effective collaboration.

This guide will walk you through setting up, configuring, and using MultiMind for your projects.

## Installation

### Prerequisites

- Python 3.7 or higher
- Git (for cloning the repository)

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/multimind.git
   cd multimind
   ```

2. Make the multimind script executable:
   ```bash
   chmod +x multimind.py
   ```

3. Initialize the directory structure:
   ```bash
   mkdir -p output/completions output/handoffs
   ```

## Configuration

### Project Configuration

The `MultiMindPM/config.json` file defines all projects managed by MultiMind. Each project has the following properties:

- `name`: The project name
- `path`: The relative path to the project directory
- `directive_file`: The filename for project directives
- `status_file`: The filename for project status reports

Example config.json:
```json
{
  "projects": [
    {
      "name": "ProjectOne",
      "path": "ProjectOne",
      "directive_file": "project_one.md",
      "status_file": "project_one-status.md"
    },
    {
      "name": "ProjectTwo",
      "path": "ProjectTwo",
      "directive_file": "project_two.md",
      "status_file": "project_two-status.md"
    }
  ]
}
```

### Creating a New Project

To create a new project:

```bash
./multimind.py init ProjectName
```

This will:
1. Create the project directory structure
2. Add the project to config.json
3. Create basic template files

## Core Workflows

### 1. Project Manager Workflow

As a Project Manager, your workflow typically involves:

1. **Planning**: Create directives and roadmaps for each project
2. **Distribution**: Run `./multimind.py sync` to distribute files to projects
3. **Monitoring**: Use `./multimind.py gather` to collect status reports
4. **Coordination**: Process handoffs with `./multimind.py handoffs`
5. **Completion**: Handle phase completions with `./multimind.py complete`

### 2. Developer/AI Agent Workflow

As a developer or AI agent working on a specific project, your workflow involves:

1. **Onboarding**: Read the project directives and roadmap
2. **Implementation**: Develop the required functionality
3. **Status Updates**: Keep your status.md file up to date
4. **Handoffs**: Create handoff requests when needed
5. **Completion Reports**: Report phase completions when finished

## Commands in Depth

### sync

The `sync` command distributes files from the PM directory to all project directories:

```bash
./multimind.py sync
```

This copies:
- README.md (main project overview)
- roadmap.md or project-specific roadmap
- Project-specific directives
- AI instructions templates
- Rules and protocols
- Advisory responses

Example output:
```
🔄 Syncing files from PM to projects...

📂 Syncing to ProjectName...
  ✓ README.md → ProjectName/README.md
  ✓ roadmap.md → ProjectName/roadmap.md
  ✓ MultiMindPM/directives/projectname.md → ProjectName/directives/projectname.md
  ✓ Copied 3 rule files to ProjectName/rules/
  ✅ Synced 4 items to ProjectName

✅ Sync complete! Synced files to all active projects.
   Run './multimind.py gather' to collect status reports and advisories from projects.
```

### gather

The `gather` command collects status reports and advisories from all projects:

```bash
./multimind.py gather
```

This copies status reports from each project into the PM's reports directory and processes any advisories.

Example output:
```
📥 Gathering status reports from projects...

📋 Gathering report from ProjectName...
  ✓ ProjectName/reports/status.md → MultiMindPM/reports/projectname-status.md

✅ Gather complete! Collected 1 status reports and processed 0 advisories.
   Review the reports in MultiMindPM/reports/ to check project progress.
```

### handoffs

The `handoffs` command processes inter-project coordination requests:

```bash
./multimind.py handoffs
```

This:
1. Checks for new handoff files in `/output/handoffs/`
2. Copies them to the PM's handoffs directory
3. Lists all current handoffs and their status

Example output:
```
🔄 Processing handoffs between projects...
  ✓ New handoff: ProjectOne-to-ProjectTwo-data-format.md

📋 Current handoffs:
  • ProjectOne-to-ProjectTwo-data-format.md ⏳ [PENDING]

📌 Tip: Update handoff statuses by editing the files in MultiMindPM/handoffs
   Then run './multimind.py sync' to distribute the updated handoffs.

✅ Handoff processing complete! 1 new handoffs found.
```

### complete

The `complete` command processes project phase completions:

```bash
./multimind.py complete ProjectName PhaseID
```

Arguments:
- `ProjectName`: The name of the project reporting completion
- `PhaseID`: The identifier for the completed phase (e.g., "Phase1")

This:
1. Looks for a completion marker file in `/output/completions/`
2. Copies it to the PM's completions directory
3. Updates the project's status report
4. Lists all current phase completions
5. Archives the phase materials

Example output:
```
Processing completion report for ProjectName - Phase1...
  ✓ Completion marker copied: output/completions/ProjectName-Phase1-complete.md → MultiMindPM/completions/ProjectName-Phase1-complete.md
  ⟳ Collecting status report...
  ✓ Status report updated: ProjectName/reports/status.md → MultiMindPM/reports/projectname-status.md

📋 Current phase completions:
  • ProjectName-Phase1-complete.md [2023-06-01]

📦 Archiving phase materials for ProjectName - Phase1...
  ✓ Archived completion report
  ✓ Archived directive
  ✓ Archived status report
  ✓ Created phase summary template
✅ Phase archiving complete! Archived 4 items to MultiMindPM/archives/ProjectName/Phase1

✅ Completion report processed!

📌 Next steps:
  1. The PM will review your completion and update the roadmap
  2. Run './multimind.py sync' later to receive updated directives
  3. Begin work on the next phase once new directives are available
```

### init

The `init` command creates a new project:

```bash
./multimind.py init ProjectName
```

This creates a new project with the standard directory structure and adds it to the configuration.

### version

The `version` command displays the current version of MultiMind:

```bash
./multimind.py version
```

Example output:
```
MultiMind v0.6.1
Project Orchestration Tool
https://github.com/yourusername/multimind
```

### create-scripts

The `create-scripts` command generates local completion scripts for each project:

```bash
./multimind.py create-scripts
# Or for a specific project:
./multimind.py create-scripts --project ProjectName
```

This creates a custom `complete_phase.py` script in each project's `scripts` directory that can be run locally from within the project.

Example output:
```
🔧 Creating completion scripts...
  ✓ Created completion script for ProjectName at ProjectName/scripts/complete_phase.py
✅ Successfully created 1 completion scripts
   Projects can now use their local scripts/complete_phase.py to report completions
```

### archive

The `archive` command explicitly archives a project phase:

```bash
./multimind.py archive ProjectName PhaseID
```

This collects all materials related to the phase and stores them in an organized archive structure.

Example output:
```
📦 Archiving phase materials for ProjectName - Phase1...
  ✓ Archived completion report
  ✓ Archived directive
  ✓ Archived status report
  ✓ Archived 2 advisories
  ✓ Created phase summary template
✅ Phase archiving complete! Archived 5 items to MultiMindPM/archives/ProjectName/Phase1
ℹ️ Tip: Don't forget to complete the phase summary document with lessons learned and decisions made.
```

## Key Directories and Files

### MultiMindPM/

This is the Project Manager's directory, containing:

- `config.json`: Configuration file
- `roadmap.md`: Main project roadmap
- `roadmaps/`: Project-specific roadmaps
- `directives/`: Task descriptions for each project
- `reports/`: Status reports collected from projects
- `rules/`: Coding standards and protocols
- `handoffs/`: Inter-project requests
- `completions/`: Project phase completion reports
- `.cursor-ai-templates/`: AI instruction templates

### Project Directories

Each project directory contains:

- `directives/`: Synced task descriptions
- `reports/`: Status reports
- `rules/`: Synced coding standards
- `src/`: Project source code
- `.cursor-ai-instructions.md`: AI agent instructions

### output/

The shared output directory:

- `completions/`: Completion markers from projects
- `handoffs/`: Handoff requests between projects

## Completion Reporting

### When to Create a Completion Report

Create a completion report when:
- You've completed all tasks in the current phase
- You've reached a significant milestone
- You've implemented all requirements in your directive

### Creating a Completion Report

1. Update your project's status report in `reports/status.md`
2. Create a completion marker file in `/output/completions/`:
   ```
   ProjectName-PhaseID-complete.md
   ```
3. Use the format described in `rules/completion_reporting.md`
4. Run the completion command:
   ```bash
   ./multimind.py complete ProjectName PhaseID
   ```

### Completion Marker Format

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

## Project Roadmaps

### Main Roadmap

The main roadmap (`roadmap.md`) provides an overview of the entire project's timeline and is maintained by the Project Manager.

### Project-Specific Roadmaps

Each project can have its own roadmap in `MultiMindPM/roadmaps/projectname_roadmap.md`. These are synchronized to each project directory during the sync operation.

To create a project-specific roadmap:
1. Create a file named `projectname_roadmap.md` in the `MultiMindPM/roadmaps/` directory
2. Follow the standard roadmap format with phases and milestones
3. Run `./multimind.py sync` to distribute it to the project

## AI Integration

### AI Instruction Files

Each project should include a `.cursor-ai-instructions.md` file that provides AI agents with:
- Project context and purpose
- Role within the larger system
- Key files and directories
- Workflow and process information

### AI Templates

The PM directory includes `.cursor-ai-templates/` with templates for each project's AI instructions. These are copied to projects during initialization.

## Troubleshooting

### Sync Issues

If files aren't syncing properly:
1. Check that project paths in `config.json` are correct
2. Ensure source files exist in the PM directory
3. Verify directory permissions

### Completion Report Issues

If completion reports aren't processing:
1. Check that the completion marker file exists in `/output/completions/`
2. Verify the project name matches what's in `config.json`
3. Make sure the phase ID is consistent with the roadmap

### Status Report Issues

If status reports aren't being gathered:
1. Verify that `reports/status.md` exists in the project directory
2. Check that the project is correctly configured in `config.json`
3. Ensure file permissions allow reading/writing

## Best Practices

1. **Frequent Synchronization**: Run sync regularly to keep all projects updated
2. **Clear Directives**: Write detailed, unambiguous directives
3. **Regular Status Updates**: Keep status reports current
4. **Descriptive Completion Reports**: Include all completed items and next steps
5. **Consistent Phase IDs**: Use consistent phase identifiers across all documents
6. **Project-Specific Roadmaps**: Create dedicated roadmaps for complex projects

## Example Workflow

Here's a typical workflow for using MultiMind with multiple projects:

1. The PM creates directives and roadmaps for each project
2. The PM runs `./multimind.py sync` to distribute them
3. Each project team works on their assigned tasks
4. Projects update their status reports regularly
5. The PM runs `./multimind.py gather` to collect updates
6. When a project needs input from another, it creates a handoff request
7. The PM processes handoffs with `./multimind.py handoffs`
8. When a project completes a phase, it creates a completion report
9. The PM processes completions with `./multimind.py complete`
10. The PM updates directives and roadmaps for the next phase
11. The cycle continues with another sync operation 

## Template System

MultiMind uses a standardized template system with placeholders to generate project-specific files:

### Template Placeholders

Templates use these special placeholders:

- `{{PROJECT_NAME}}`: Replaced with the actual project name

### Template Locations

- Advisory templates: `MultiMindPM/templates/advisories/`
- Archive templates: `MultiMindPM/templates/archives/`
- Decision templates: `MultiMindPM/templates/decisions/`
- Completion script template: `MultiMindPM/templates/complete_phase.py`

These templates are used to generate standardized documents across all projects while keeping project-specific information consistent.

## Active vs. Template Projects

MultiMind distinguishes between template projects and active projects:

- **Template Projects**: ProjectOne, ProjectTwo, and ProjectThree are considered template projects
- **Active Projects**: Any other project, or template projects that have a status.md file

Commands like `sync`, `gather`, and `create-scripts` automatically skip inactive template projects, focusing only on projects with actual development activity. 