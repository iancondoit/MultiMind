#!/usr/bin/env python3
"""
MultiMind - Project Orchestration Tool

A local orchestration tool for coordinating multiple projects that depend on one another.
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Configuration file path
CONFIG_FILE = "MultiMindPM/config.json"
VERSION = "0.6.1"  # Updated version number

# Template project names
TEMPLATE_PROJECTS = ["ProjectOne", "ProjectTwo", "ProjectThree"]


def load_config() -> Dict:
    """Load the configuration from the config file."""
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {CONFIG_FILE}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Config file {CONFIG_FILE} is not valid JSON")
        sys.exit(1)


def is_template_project(project_name: str) -> bool:
    """Check if a project is a template project."""
    return project_name in TEMPLATE_PROJECTS


def is_active_project(project_name: str, project_path: str) -> bool:
    """
    Check if a project is an active project with content.
    
    A project is considered active if it has a status report or other meaningful content.
    """
    # Skip template projects completely if they don't have actual content
    if is_template_project(project_name):
        status_path = os.path.join(project_path, "reports/status.md")
        return os.path.exists(status_path)
    return True


def ensure_dirs(project_path: str, dir_name: str) -> None:
    """Ensure that the required directories exist."""
    path = os.path.join(project_path, dir_name)
    os.makedirs(path, exist_ok=True)


def sync_files(config: Dict) -> None:
    """
    Synchronize files from the PM directory to the project directories.
    
    This includes:
    - README.md
    - roadmap.md
    - Project-specific directive files
    - .cursor-ai-instructions.md (for AI onboarding)
    - rules/ directory (coding standards, etc.)
    - advisories/ directory (PM responses to project questions)
    """
    print("🔄 Syncing files from PM to projects...")
    
    total_synced = 0
    
    for project in config["projects"]:
        project_name = project["name"]
        project_path = project["path"]
        directive_file = project["directive_file"]
        
        # Skip inactive template projects
        if not is_active_project(project_name, project_path):
            continue
        
        print(f"\n📂 Syncing to {project_name}...")
        project_synced = 0
        
        # Ensure directories exist
        ensure_dirs(project_path, "directives")
        ensure_dirs(project_path, "reports")
        ensure_dirs(project_path, "rules")
        ensure_dirs(project_path, "advisories")
        
        # Copy README.md
        try:
            shutil.copy("MultiMindPM/README.md", os.path.join(project_path, "README.md"))
            print(f"  ✓ README.md → {project_path}/README.md")
            project_synced += 1
        except FileNotFoundError:
            print(f"  ⚠️ Warning: MultiMindPM/README.md not found")
        except Exception as e:
            print(f"  ❌ Error copying README.md: {e}")
        
        # Copy roadmap.md
        try:
            # Check if project-specific roadmap exists
            project_roadmap = f"MultiMindPM/roadmaps/{project_name.lower()}_roadmap.md"
            if os.path.exists(project_roadmap):
                # Use project-specific roadmap
                shutil.copy(project_roadmap, os.path.join(project_path, "roadmap.md"))
                print(f"  ✓ {project_roadmap} → {project_path}/roadmap.md")
                project_synced += 1
            else:
                # Fallback to main roadmap
                main_roadmap = "MultiMindPM/roadmap.md"
                if os.path.exists(main_roadmap):
                    shutil.copy(main_roadmap, os.path.join(project_path, "roadmap.md"))
                    print(f"  ✓ roadmap.md → {project_path}/roadmap.md")
                    project_synced += 1
                else:
                    print(f"  ⚠️ Warning: No roadmap file found for {project_name}")
        except Exception as e:
            print(f"  ❌ Error copying roadmap: {e}")
        
        # Copy directive file
        try:
            source = os.path.join("MultiMindPM/directives", directive_file)
            dest = os.path.join(project_path, "directives", directive_file)
            if os.path.exists(source):
                shutil.copy(source, dest)
                print(f"  ✓ {source} → {dest}")
                project_synced += 1
            else:
                print(f"  ⚠️ Warning: Directive file {source} not found")
        except Exception as e:
            print(f"  ❌ Error copying directive file: {e}")
            
        # Copy .cursor-ai-instructions.md
        try:
            # Check if project-specific Cursor instructions exist
            cursor_instructions = f"{project_path}/.cursor-ai-instructions.md"
            if os.path.exists(cursor_instructions):
                # No need to copy, it's already in the right place
                print(f"  ℹ️ Using existing {cursor_instructions}")
            else:
                # No project-specific instructions found, let's see if there's a template
                template_path = f"MultiMindPM/.cursor-ai-templates/{project_name}-ai-instructions.md"
                if os.path.exists(template_path):
                    shutil.copy(template_path, cursor_instructions)
                    print(f"  ✓ {template_path} → {cursor_instructions}")
                    project_synced += 1
        except Exception as e:
            print(f"  ⚠️ Warning: Issue with cursor instructions: {e}")
            
        # Copy rules
        try:
            rules_dir = "MultiMindPM/rules"
            rules_copied = 0
            if os.path.exists(rules_dir) and os.path.isdir(rules_dir):
                for rule_file in os.listdir(rules_dir):
                    if rule_file.endswith(".md"):
                        source = os.path.join(rules_dir, rule_file)
                        dest = os.path.join(project_path, "rules", rule_file)
                        shutil.copy(source, dest)
                        rules_copied += 1
                if rules_copied > 0:
                    print(f"  ✓ Copied {rules_copied} rule files to {project_path}/rules/")
                    project_synced += 1
            else:
                print(f"  ⚠️ Warning: Rules directory not found")
        except Exception as e:
            print(f"  ❌ Error copying rules: {e}")
        
        total_synced += project_synced
        
        if project_synced > 0:
            print(f"  ✅ Synced {project_synced} items to {project_name}")
        else:
            print(f"  ⚠️ No files were synced to {project_name}")
    
    # Process advisories
    advisories_synced = handle_advisories(config)
    if advisories_synced > 0:
        total_synced += 1
    
    # Create completion scripts for all projects
    scripts_created = create_completion_scripts(config)
    
    if total_synced > 0:
        print(f"\n✅ Sync complete! Synced files to all active projects.")
        print(f"   Run './multimind.py gather' to collect status reports and advisories from projects.")
    else:
        print(f"\n⚠️ Sync completed but no files were synced to any projects.")
        print(f"   Check that you have active projects and that your PM files exist.")


def gather_reports(config: Dict) -> None:
    """
    Gather status reports from project directories to the PM directory.
    """
    print("📥 Gathering status reports from projects...")
    
    reports_gathered = 0
    
    for project in config["projects"]:
        project_name = project["name"]
        project_path = project["path"]
        status_file = project["status_file"]
        
        # Skip inactive template projects
        if not is_active_project(project_name, project_path):
            continue
        
        print(f"\n📋 Gathering report from {project_name}...")
        
        # Copy status.md to PM reports directory
        source = os.path.join(project_path, "reports/status.md")
        dest = os.path.join("MultiMindPM/reports", status_file)
        
        try:
            if os.path.exists(source):
                shutil.copy(source, dest)
                print(f"  ✓ {source} → {dest}")
                reports_gathered += 1
            else:
                print(f"  ⚠️ Warning: Status report not found at {source}")
                print(f"     Project should create a status report to provide updates on progress.")
        except Exception as e:
            print(f"  ❌ Error copying status report: {e}")
    
    # Process advisories (gather from projects to PM)
    advisories_synced = handle_advisories(config)
    
    if reports_gathered > 0 or advisories_synced > 0:
        print(f"\n✅ Gather complete! Collected {reports_gathered} status reports and processed {advisories_synced} advisories.")
        print(f"   Review the reports in MultiMindPM/reports/ to check project progress.")
        print(f"   Address any advisories in MultiMindPM/advisories/ that need PM attention.")
    else:
        print(f"\n⚠️ Gather completed but no reports or advisories were collected.")
        print(f"   Ensure that projects have status reports and are properly initialized.")


def handle_handoffs(config: Dict) -> None:
    """
    Process handoff documents between projects.
    
    - Checks for new handoffs in output/handoffs
    - Moves them to MultiMindPM/handoffs
    - Lists all current handoffs
    """
    print("🔄 Processing handoffs between projects...")
    
    # Ensure handoff directories exist
    pm_handoffs_dir = "MultiMindPM/handoffs"
    output_handoffs_dir = "output/handoffs"
    os.makedirs(pm_handoffs_dir, exist_ok=True)
    os.makedirs(output_handoffs_dir, exist_ok=True)
    
    # Check for new handoffs in output directory
    new_handoffs = []
    try:
        for handoff_file in os.listdir(output_handoffs_dir):
            if handoff_file.endswith(".md"):
                source = os.path.join(output_handoffs_dir, handoff_file)
                dest = os.path.join(pm_handoffs_dir, handoff_file)
                
                # Only copy if it doesn't exist in PM directory or is newer
                if (not os.path.exists(dest) or 
                    os.path.getmtime(source) > os.path.getmtime(dest)):
                    shutil.copy(source, dest)
                    new_handoffs.append(handoff_file)
                    print(f"  ✓ New handoff: {handoff_file}")
    except Exception as e:
        print(f"  ❌ Error processing handoffs: {e}")
    
    # List all current handoffs
    handoffs = []
    if os.path.exists(pm_handoffs_dir):
        for handoff_file in os.listdir(pm_handoffs_dir):
            if handoff_file.endswith(".md"):
                handoffs.append(handoff_file)
    
    if handoffs:
        print("\n📋 Current handoffs:")
        for handoff in sorted(handoffs):
            # Try to extract status from the file
            status = "UNKNOWN"
            try:
                with open(os.path.join(pm_handoffs_dir, handoff), 'r') as f:
                    for line in f:
                        if line.startswith("Status:"):
                            status = line.strip().split("Status:")[1].strip()
                            break
            except:
                pass
            
            # Apply emoji based on status
            status_icon = "❓"  # Default unknown
            if status.upper() == "PENDING":
                status_icon = "⏳"
            elif status.upper() == "COMPLETED":
                status_icon = "✅"
            elif status.upper() == "REJECTED":
                status_icon = "❌"
            elif status.upper() == "ACCEPTED":
                status_icon = "✓"
            
            print(f"  • {handoff} {status_icon} [{status}]")
        
        print(f"\n📌 Tip: Update handoff statuses by editing the files in {pm_handoffs_dir}")
        print(f"   Then run './multimind.py sync' to distribute the updated handoffs.")
    else:
        print("\n🔍 No current handoffs found.")
        print(f"   Projects can create handoffs by placing .md files in {output_handoffs_dir}")
    
    if new_handoffs:
        print(f"\n✅ Handoff processing complete! {len(new_handoffs)} new handoffs found.")
    else:
        print(f"\n✅ Handoff processing complete! No new handoffs found.")


def report_completion(config: Dict, project_name: str, phase_id: str, only_project: bool = False) -> None:
    """
    Process and record a project phase completion.
    
    This function:
    1. Creates a completion marker file
    2. Collects status reports
    3. Notifies the PM of the completion
    4. Archives the phase materials (if requested)
    
    Args:
        config: The configuration dictionary
        project_name: Name of the project that completed a phase
        phase_id: Identifier for the completed phase
        only_project: If True, only show completions for the specified project
    """
    print(f"Processing completion report for {project_name} - {phase_id}...")
    
    # Validate project exists
    project_found = False
    project_path = ""
    for project in config["projects"]:
        if project["name"].lower() == project_name.lower():
            project_found = True
            project_path = project["path"]
            project_name = project["name"]  # Use correct case
            break
    
    if not project_found:
        print(f"Error: Project '{project_name}' not found in config")
        print("Please check the project name and try again.")
        print(f"Available projects: {', '.join(p['name'] for p in config['projects'] if is_active_project(p['name'], p['path']))}")
        return
        
    # Check if the project is active
    if not is_active_project(project_name, project_path):
        print(f"Error: '{project_name}' appears to be a template project without active development")
        print("Please initialize this project with content before reporting completions.")
        print("You can add a status report at {project_path}/reports/status.md to make it active.")
        return
    
    # Ensure completions directories exist
    pm_completions_dir = "MultiMindPM/completions"
    output_completions_dir = "output/completions"
    os.makedirs(pm_completions_dir, exist_ok=True)
    os.makedirs(output_completions_dir, exist_ok=True)
    
    # Define completion filename
    completion_file = f"{project_name}-{phase_id}-complete.md"
    source_path = os.path.join(output_completions_dir, completion_file)
    dest_path = os.path.join(pm_completions_dir, completion_file)
    
    # Check if completion marker exists
    if os.path.exists(source_path):
        # Copy to PM directory
        shutil.copy(source_path, dest_path)
        print(f"  ✓ Completion marker copied: {source_path} → {dest_path}")
    else:
        # Create a basic completion marker
        today = datetime.now().strftime('%Y-%m-%d')
        with open(dest_path, 'w') as f:
            f.write(f"""# Project Completion: {project_name} - {phase_id}

Version: 0.1.0
Completed: {today}
Project: {project_name}
Phase: {phase_id}

## Completed Directives

* Completion reported via command line
* See status report for details

## Notes

Generated automatically by multimind.py complete command.

## Next Phase

Awaiting PM review and new directives.
""")
        print(f"  ✓ Created basic completion marker: {dest_path}")
        print(f"  ℹ️ Note: In the future, create your own completion marker in advance for more detailed reporting.")
        print(f"     See MultiMindPM/rules/completion_reporting.md for the proper format.")
    
    # Gather status report
    print(f"  ⟳ Collecting status report...")
    status_file = None
    for project in config["projects"]:
        if project["name"] == project_name:
            status_file = project["status_file"]
            break
    
    if status_file:
        source = os.path.join(project_path, "reports/status.md")
        dest = os.path.join("MultiMindPM/reports", status_file)
        try:
            shutil.copy(source, dest)
            print(f"  ✓ Status report updated: {source} → {dest}")
        except FileNotFoundError:
            print(f"  ⚠️ Warning: Status report not found at {source}")
            print(f"     Please create a status report to provide context for your completion.")
    
    # List all current completions
    completions = []
    if os.path.exists(pm_completions_dir):
        for file in os.listdir(pm_completions_dir):
            if file.endswith("-complete.md"):
                # Filter by project if specified
                if only_project and not file.startswith(f"{project_name}-"):
                    continue
                    
                # Get project name from filename (format: ProjectName-PhaseID-complete.md)
                file_project = file.split("-")[0]
                
                # Skip template projects that don't have active development
                project_path = ""
                for p in config["projects"]:
                    if p["name"] == file_project:
                        project_path = p["path"]
                        break
                        
                if not is_active_project(file_project, project_path):
                    continue
                        
                completions.append(file)
    
    if completions:
        print("\n📋 Current phase completions:")
        for completion in sorted(completions):
            # Try to extract date from the file
            date = "Unknown date"
            try:
                with open(os.path.join(pm_completions_dir, completion), 'r') as f:
                    for line in f:
                        if line.startswith("Completed:"):
                            date = line.strip().split("Completed:")[1].strip()
                            break
            except:
                pass
            
            print(f"  • {completion} [{date}]")
    else:
        print("\n📋 No completions found for active projects.")
    
    # Archive the phase materials
    archive_phase(config, project_name, phase_id)
    
    print("\n✅ Completion report processed!")
    print("\n📌 Next steps:")
    print("  1. The PM will review your completion and update the roadmap")
    print("  2. Run './multimind.py sync' later to receive updated directives")
    print("  3. Begin work on the next phase once new directives are available")


def init_project(config: Dict, project_name: str) -> None:
    """
    Initialize a new project with the standard directory structure.
    
    Args:
        config: The configuration dictionary
        project_name: Name of the new project
    """
    print(f"Initializing new project: {project_name}")
    
    # Create project directory
    project_path = project_name
    os.makedirs(project_path, exist_ok=True)
    
    # Create standard directories
    dirs = ["directives", "reports", "rules", "src", "src/models", 
            "src/utils", "src/tests", "advisories", "scripts"]
    
    for dir_name in dirs:
        ensure_dirs(project_path, dir_name)
    
    # Create basic files
    with open(os.path.join(project_path, "README.md"), 'w') as f:
        f.write(f"# {project_name}\n\nVersion: 0.1.0\n\n## Overview\n\nDescription of {project_name} goes here.\n")
    
    with open(os.path.join(project_path, "reports/status.md"), 'w') as f:
        f.write(f"# {project_name} Status Report\n\nVersion: 0.1.0\n\n## Last Update\n\n{datetime.now().strftime('%Y-%m-%d')}\n\n## Current Progress\n\n* Project initialized\n\n## Blockers\n\n* None at this time\n\n## Next Steps\n\n* Define project requirements\n")
    
    # Create source files
    with open(os.path.join(project_path, "src/main.py"), 'w') as f:
        f.write(f"""#!/usr/bin/env python3
\"\"\"
Main module for {project_name}.
\"\"\"

def main():
    \"\"\"Main entry point for the application.\"\"\"
    print("Hello from {project_name}!")

if __name__ == "__main__":
    main()
""")
    
    # Create PM advisory directory for this project
    pm_advisories_dir = os.path.join("MultiMindPM/advisories", project_name)
    os.makedirs(pm_advisories_dir, exist_ok=True)
    
    # Create PM archive directory for this project
    pm_archives_dir = os.path.join("MultiMindPM/archives", project_name)
    os.makedirs(pm_archives_dir, exist_ok=True)
    os.makedirs(os.path.join(pm_archives_dir, "Phase1"), exist_ok=True)
    
    print(f"Project {project_name} initialized successfully!")
    
    # Update config to include new project
    directive_file = f"{project_name.lower()}.md"
    status_file = f"{project_name.lower()}-status.md"
    
    # Create empty directive file with completion instructions
    with open(os.path.join("MultiMindPM/directives", directive_file), 'w') as f:
        f.write(f"""# {project_name} Directives

Version: 0.1.0

## Current Tasks

1. Define project requirements

## Implementation Guidelines

- Follow the coding standards defined in `/rules/coding_standards.md`
- Create appropriate unit tests for all functionality
- Document your code and APIs

## Completion Reporting - IMPORTANT

When you have completed all the tasks in this directive:

1. Update your status report in `/reports/status.md` with details of what you've accomplished
2. Create a completion marker file in `/output/completions/{project_name}-Phase1-complete.md` following the format in `/rules/completion_reporting.md`
3. Run the following command to notify the Project Manager:
   ```bash
   ./multimind.py complete {project_name} Phase1
   ```
   
   Or use the local completion script from your project directory:
   ```bash
   python scripts/complete_phase.py Phase1
   ```
   
This completion reporting is a critical part of the MultiMind workflow and must be performed when the phase is complete.
""")
    
    # Add to config
    config["projects"].append({
        "name": project_name,
        "path": project_path,
        "directive_file": directive_file,
        "status_file": status_file
    })
    
    # Save updated config
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration updated with new project: {project_name}")
    
    # Create project-specific completion script
    print(f"Creating completion script for {project_name}...")
    create_completion_scripts(config, project_name)


def handle_advisories(config: Dict) -> int:
    """
    Process advisory documents between the PM and projects.
    
    - Checks for new advisories in project directories
    - Moves them to MultiMindPM/advisories/{project_name}/
    - Lists all current advisories
    """
    print("Processing advisories...")
    
    # Ensure PM advisories directory exists
    pm_advisories_base_dir = "MultiMindPM/advisories"
    os.makedirs(pm_advisories_base_dir, exist_ok=True)
    
    # Process each project's advisories
    advisories_synced = 0
    for project in config["projects"]:
        project_name = project["name"]
        project_path = project["path"]
        
        # Skip inactive template projects
        if not is_active_project(project_name, project_path):
            continue
            
        print(f"Processing advisories for {project_name}...")
        
        # Ensure project-specific directories exist
        pm_project_advisories_dir = os.path.join(pm_advisories_base_dir, project_name)
        project_advisories_dir = os.path.join(project_path, "advisories")
        os.makedirs(pm_project_advisories_dir, exist_ok=True)
        os.makedirs(project_advisories_dir, exist_ok=True)
        
        # Check for new advisories in project directory (to PM)
        new_advisories = []
        if os.path.exists(project_advisories_dir):
            for advisory_file in os.listdir(project_advisories_dir):
                if advisory_file.endswith(".md"):
                    source = os.path.join(project_advisories_dir, advisory_file)
                    dest = os.path.join(pm_project_advisories_dir, advisory_file)
                    
                    # Only copy if it doesn't exist in PM directory or is newer
                    if (not os.path.exists(dest) or 
                        os.path.getmtime(source) > os.path.getmtime(dest)):
                        shutil.copy(source, dest)
                        new_advisories.append(advisory_file)
                        print(f"  + New advisory from project: {advisory_file}")
        
        # Check for updated advisories in PM directory (to project)
        updated_advisories = []
        if os.path.exists(pm_project_advisories_dir):
            for advisory_file in os.listdir(pm_project_advisories_dir):
                if advisory_file.endswith(".md"):
                    source = os.path.join(pm_project_advisories_dir, advisory_file)
                    dest = os.path.join(project_advisories_dir, advisory_file)
                    
                    # Only copy if newer than project's version
                    if (not os.path.exists(dest) or 
                        os.path.getmtime(source) > os.path.getmtime(dest)):
                        
                        # Always copy from PM to project, regardless of content
                        # This ensures directives, responses, and status updates flow to the project
                        shutil.copy(source, dest)
                        updated_advisories.append(advisory_file)
                        print(f"  + Updated advisory to project: {advisory_file}")
        
        advisories_synced += len(new_advisories) + len(updated_advisories)
    
    # List all current advisories organized by project and status
    print("\nCurrent advisories:")
    
    if os.path.exists(pm_advisories_base_dir):
        # Group advisories by project and status
        advisories_by_project = {}
        
        for project_dir in os.listdir(pm_advisories_base_dir):
            project_advisories_path = os.path.join(pm_advisories_base_dir, project_dir)
            if os.path.isdir(project_advisories_path):
                advisories_by_project[project_dir] = {"ASKED": [], "ANSWERED": [], "RESOLVED": []}
                
                for advisory_file in os.listdir(project_advisories_path):
                    if advisory_file.endswith(".md"):
                        # Extract status
                        status = "UNKNOWN"
                        try:
                            with open(os.path.join(project_advisories_path, advisory_file), 'r') as f:
                                for line in f:
                                    if line.startswith("Status:"):
                                        status = line.strip().split("Status:")[1].strip()
                                        if status not in ["ASKED", "ANSWERED", "RESOLVED"]:
                                            status = "UNKNOWN"
                                        break
                        except:
                            pass
                        
                        if status in advisories_by_project[project_dir]:
                            advisories_by_project[project_dir][status].append(advisory_file)
                        else:
                            advisories_by_project[project_dir]["ASKED"].append(advisory_file)
        
        # Print advisories by project and status
        for project, statuses in advisories_by_project.items():
            has_advisories = sum(len(advisories) for advisories in statuses.values()) > 0
            if has_advisories:
                print(f"  Project: {project}")
                
                for status, advisories in statuses.items():
                    if advisories:
                        print(f"    {status}:")
                        for advisory in sorted(advisories):
                            print(f"      - {advisory}")
    
    print("Advisory processing complete!")
    
    return advisories_synced


def archive_phase(config: Dict, project_name: str, phase_id: str) -> None:
    """
    Archive completed phase materials.
    
    Args:
        config: The configuration dictionary
        project_name: Name of the project
        phase_id: Identifier for the completed phase
    """
    print(f"\n📦 Archiving phase materials for {project_name} - {phase_id}...")
    
    # Ensure the project exists
    project_found = False
    project_path = ""
    for project in config["projects"]:
        if project["name"].lower() == project_name.lower():
            project_found = True
            project_path = project["path"]
            project_name = project["name"]  # Use correct case
            break
    
    if not project_found:
        print(f"  ❌ Error: Project '{project_name}' not found in config")
        return
    
    # Ensure archive directory exists
    archive_dir = f"MultiMindPM/archives/{project_name}/{phase_id}"
    os.makedirs(archive_dir, exist_ok=True)
    
    archived_items = 0
    
    # Archive completion report
    completion_file = f"{project_name}-{phase_id}-complete.md"
    completion_path = os.path.join("MultiMindPM/completions", completion_file)
    if os.path.exists(completion_path):
        shutil.copy(completion_path, os.path.join(archive_dir, "completion.md"))
        print(f"  ✓ Archived completion report")
        archived_items += 1
    else:
        print(f"  ⚠️ No completion report found to archive")
    
    # Archive current directive
    directive_file = None
    for project in config["projects"]:
        if project["name"] == project_name:
            directive_file = project["directive_file"]
            break
    
    if directive_file:
        directive_path = os.path.join("MultiMindPM/directives", directive_file)
        if os.path.exists(directive_path):
            shutil.copy(directive_path, os.path.join(archive_dir, "directive.md"))
            print(f"  ✓ Archived directive")
            archived_items += 1
        else:
            print(f"  ⚠️ No directive file found to archive")
    
    # Archive status report
    status_file = None
    for project in config["projects"]:
        if project["name"] == project_name:
            status_file = project["status_file"]
            break
    
    if status_file:
        status_path = os.path.join("MultiMindPM/reports", status_file)
        if os.path.exists(status_path):
            shutil.copy(status_path, os.path.join(archive_dir, "status.md"))
            print(f"  ✓ Archived status report")
            archived_items += 1
        else:
            print(f"  ⚠️ No status report found to archive")
    
    # Archive relevant advisories
    advisories_dir = f"MultiMindPM/advisories/{project_name}"
    if os.path.exists(advisories_dir):
        advisories_count = 0
        archive_advisories_dir = os.path.join(archive_dir, "advisories")
        os.makedirs(archive_advisories_dir, exist_ok=True)
        
        for advisory_file in os.listdir(advisories_dir):
            if advisory_file.endswith(".md"):
                source = os.path.join(advisories_dir, advisory_file)
                dest = os.path.join(archive_advisories_dir, advisory_file)
                shutil.copy(source, dest)
                advisories_count += 1
        
        if advisories_count > 0:
            print(f"  ✓ Archived {advisories_count} advisories")
            archived_items += 1
        else:
            print(f"  ℹ️ No advisories found to archive")
    
    # Create a placeholder for phase summary
    summary_template_path = "MultiMindPM/templates/archives/phase_summary_template.md"
    summary_path = os.path.join(archive_dir, "phase_summary.md")
    
    if os.path.exists(summary_template_path):
        try:
            with open(summary_template_path, 'r') as src:
                content = src.read()
                # Replace placeholders
                content = content.replace("[Project Name]", project_name)
                content = content.replace("[Phase ID]", phase_id)
                today = datetime.now().strftime('%Y-%m-%d')
                content = content.replace("[YYYY-MM-DD]", today)
                
                with open(summary_path, 'w') as dest:
                    dest.write(content)
            
            print(f"  ✓ Created phase summary template")
            archived_items += 1
        except Exception as e:
            print(f"  ❌ Error creating phase summary: {e}")
            # Create a basic summary file as fallback
            try:
                with open(summary_path, 'w') as f:
                    f.write(f"# Phase Summary: {project_name} - {phase_id}\n\n")
                    f.write(f"Completion Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
                    f.write(f"Complete this summary with key learnings and information from the phase.\n")
                print(f"  ⚠️ Created basic phase summary file (fallback)")
                archived_items += 1
            except Exception as e:
                print(f"  ❌ Could not create even a basic summary file: {e}")
    else:
        # Create a basic summary file if template doesn't exist
        try:
            with open(summary_path, 'w') as f:
                f.write(f"# Phase Summary: {project_name} - {phase_id}\n\n")
                f.write(f"Completion Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write(f"Complete this summary with key learnings and information from the phase.\n")
            
            print(f"  ⚠️ Created basic phase summary file (no template found)")
            archived_items += 1
        except Exception as e:
            print(f"  ❌ Error creating basic summary file: {e}")
    
    if archived_items > 0:
        print(f"✅ Phase archiving complete! Archived {archived_items} items to {archive_dir}")
        print(f"ℹ️ Tip: Don't forget to complete the phase summary document with lessons learned and decisions made.")
    else:
        print(f"⚠️ Phase archiving completed but no items were successfully archived.")
        print(f"   This may indicate missing project documentation or file access issues.")


def create_project_completion_script(project_name: str, project_path: str, template_content: str) -> bool:
    """
    Create a completion script for a specific project.
    
    Args:
        project_name: Name of the project
        project_path: Path to the project directory
        template_content: Content of the template script
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Create scripts directory if it doesn't exist
    scripts_dir = os.path.join(project_path, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Create the completion script
    script_path = os.path.join(scripts_dir, "complete_phase.py")
    script_content = template_content.replace("{{PROJECT_NAME}}", project_name)
    
    try:
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        print(f"  ✓ Created completion script for {project_name} at {script_path}")
        return True
    except Exception as e:
        print(f"  ❌ Error creating completion script for {project_name}: {e}")
        return False


def create_completion_scripts(config: Dict, project_name: str = None) -> int:
    """
    Create project-specific completion scripts.
    
    Args:
        config: The configuration dictionary
        project_name: Optional name of a specific project to create script for
    """
    template_path = "MultiMindPM/templates/complete_phase.py"
    
    if not os.path.exists(template_path):
        print(f"❌ Error: Completion script template not found at {template_path}")
        print(f"   Please ensure the template file exists before running this command.")
        return 0
    
    # Load template content
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
    except Exception as e:
        print(f"❌ Error reading template file: {e}")
        return 0
    
    print(f"🔧 Creating completion scripts...")
    
    # Get all projects or just the specified one
    projects = []
    if project_name:
        for project in config["projects"]:
            if project["name"].lower() == project_name.lower():
                projects.append(project)
                break
        if not projects:
            print(f"❌ Error: Project '{project_name}' not found in config")
            print(f"   Available projects: {', '.join(p['name'] for p in config['projects'] if is_active_project(p['name'], p['path']))}")
            return 0
    else:
        # Only include active projects (not template projects without content)
        projects = []
        for p in config["projects"]:
            if is_active_project(p["name"], p["path"]):
                projects.append(p)
    
    # Create scripts for each project
    success_count = 0
    for project in projects:
        if create_project_completion_script(project["name"], project["path"], template_content):
            success_count += 1
    
    if success_count > 0:
        print(f"✅ Successfully created {success_count} completion scripts")
        print(f"   Projects can now use their local scripts/complete_phase.py to report completions")
    else:
        print(f"⚠️ No completion scripts were created successfully")
    
    return success_count


def setup_directories(config: Dict) -> None:
    """
    Set up all required directories for the MultiMind system.
    
    Args:
        config: The configuration dictionary
    """
    print("Setting up MultiMind directory structure...")
    
    # Core PM directories
    pm_dirs = [
        "MultiMindPM/directives",
        "MultiMindPM/reports",
        "MultiMindPM/rules",
        "MultiMindPM/handoffs",
        "MultiMindPM/completions",
        "MultiMindPM/advisories",
        "MultiMindPM/templates",
        "MultiMindPM/templates/advisories",
        "MultiMindPM/templates/archives",
        "MultiMindPM/templates/decisions",
        "MultiMindPM/archives",
        "output/completions",
        "output/handoffs"
    ]
    
    for dir_path in pm_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  - Ensured directory exists: {dir_path}")
    
    # Project-specific directories
    for project in config["projects"]:
        project_name = project["name"]
        project_path = project["path"]
        
        # Skip inactive template projects
        if not is_active_project(project_name, project_path):
            continue
            
        project_dirs = [
            os.path.join(project_path, "directives"),
            os.path.join(project_path, "reports"),
            os.path.join(project_path, "rules"),
            os.path.join(project_path, "advisories"),
            os.path.join(project_path, "scripts"),
            os.path.join(project_path, "src"),
            os.path.join("MultiMindPM/advisories", project_name),
            os.path.join("MultiMindPM/archives", project_name)
        ]
        
        for dir_path in project_dirs:
            os.makedirs(dir_path, exist_ok=True)
            print(f"  - Ensured directory exists: {dir_path}")
    
    print("Directory setup complete!")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description=f"MultiMind v{VERSION} - Project Orchestration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ./multimind.py setup                    # Set up all required directories
  ./multimind.py init NewProject          # Initialize a new project
  ./multimind.py sync                     # Push files to all projects
  ./multimind.py gather                   # Collect status reports
  ./multimind.py complete ProjectOne Phase1  # Report phase completion
  ./multimind.py advisories               # Process advisories between PM and projects
"""
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # sync command
    sync_parser = subparsers.add_parser("sync", help="Push files to projects")
    
    # gather command
    gather_parser = subparsers.add_parser("gather", help="Collect status reports and advisories")
    
    # handoffs command
    handoffs_parser = subparsers.add_parser("handoffs", help="Process handoffs between projects")
    
    # complete command
    complete_parser = subparsers.add_parser("complete", help="Report project phase completion")
    complete_parser.add_argument("project_name", help="Name of the project reporting completion")
    complete_parser.add_argument("phase_id", help="Identifier for the completed phase (e.g., Phase1)")
    complete_parser.add_argument("--only-project", action="store_true", help="Only show completions for the specified project")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("project_name", help="Name of the new project")
    
    # advisories command
    advisories_parser = subparsers.add_parser("advisories", help="Process advisories between PM and projects")
    
    # archive command
    archive_parser = subparsers.add_parser("archive", help="Archive a completed phase")
    archive_parser.add_argument("project_name", help="Name of the project")
    archive_parser.add_argument("phase_id", help="Identifier for the completed phase (e.g., Phase1)")
    
    # setup command
    setup_parser = subparsers.add_parser("setup", help="Setup all required directories")
    
    # create-scripts command
    scripts_parser = subparsers.add_parser("create-scripts", help="Create completion scripts for projects")
    scripts_parser.add_argument("--project", help="Name of a specific project to create script for")
    
    # version command
    version_parser = subparsers.add_parser("version", help="Display version information")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Handle version command first (no config needed)
    if args.command == "version":
        print(f"MultiMind v{VERSION}")
        print("Project Orchestration Tool")
        print("https://github.com/yourusername/multimind")
        return
    
    # All other commands need config
    try:
        config = load_config()
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        print(f"   Please run './multimind.py setup' to initialize the system.")
        return
    
    if args.command == "sync":
        sync_files(config)
    elif args.command == "gather":
        gather_reports(config)
    elif args.command == "handoffs":
        handle_handoffs(config)
    elif args.command == "complete":
        report_completion(config, args.project_name, args.phase_id, args.only_project)
    elif args.command == "init":
        init_project(config, args.project_name)
    elif args.command == "advisories":
        handle_advisories(config)
    elif args.command == "archive":
        archive_phase(config, args.project_name, args.phase_id)
    elif args.command == "setup":
        setup_directories(config)
    elif args.command == "create-scripts":
        create_completion_scripts(config, args.project)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 