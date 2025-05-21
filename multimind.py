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
    - Completion scripts template
    """
    print("Syncing files from PM to projects...")
    
    # Ensure template directory exists
    template_dir = "MultiMindPM/templates"
    os.makedirs(template_dir, exist_ok=True)
    
    for project in config["projects"]:
        project_name = project["name"]
        project_path = project["path"]
        directive_file = project["directive_file"]
        
        print(f"Syncing to {project_name}...")
        
        # Ensure directories exist
        ensure_dirs(project_path, "directives")
        ensure_dirs(project_path, "reports")
        ensure_dirs(project_path, "rules")
        ensure_dirs(project_path, "advisories")
        ensure_dirs(project_path, "scripts")
        
        # Copy README.md
        try:
            shutil.copy("MultiMindPM/README.md", os.path.join(project_path, "README.md"))
            print(f"  - README.md → {project_path}/README.md")
        except FileNotFoundError:
            print(f"  ! Warning: MultiMindPM/README.md not found")
        
        # Copy roadmap.md
        try:
            # Check if project-specific roadmap exists
            project_roadmap = f"MultiMindPM/roadmaps/{project_name.lower()}_roadmap.md"
            if os.path.exists(project_roadmap):
                # Use project-specific roadmap
                shutil.copy(project_roadmap, os.path.join(project_path, "roadmap.md"))
                print(f"  - {project_roadmap} → {project_path}/roadmap.md")
            else:
                # Fallback to main roadmap
                shutil.copy("MultiMindPM/roadmap.md", os.path.join(project_path, "roadmap.md"))
                print(f"  - roadmap.md → {project_path}/roadmap.md")
        except FileNotFoundError:
            print(f"  ! Warning: Roadmap file not found")
        
        # Copy directive file
        try:
            source = os.path.join("MultiMindPM/directives", directive_file)
            dest = os.path.join(project_path, "directives", directive_file)
            shutil.copy(source, dest)
            print(f"  - {source} → {dest}")
        except FileNotFoundError:
            print(f"  ! Warning: {source} not found")
            
        # Copy .cursor-ai-instructions.md
        try:
            # Check if project-specific Cursor instructions exist
            cursor_instructions = f"{project_path}/.cursor-ai-instructions.md"
            if os.path.exists(cursor_instructions):
                # No need to copy, it's already in the right place
                print(f"  - Using existing {cursor_instructions}")
            else:
                # No project-specific instructions found, let's see if there's a template
                template_path = f"MultiMindPM/.cursor-ai-templates/{project_name}-ai-instructions.md"
                if os.path.exists(template_path):
                    shutil.copy(template_path, cursor_instructions)
                    print(f"  - {template_path} → {cursor_instructions}")
        except Exception as e:
            print(f"  ! Warning: Issue with cursor instructions: {e}")
            
        # Copy rules
        try:
            rules_dir = "MultiMindPM/rules"
            if os.path.exists(rules_dir) and os.path.isdir(rules_dir):
                for rule_file in os.listdir(rules_dir):
                    if rule_file.endswith(".md"):
                        source = os.path.join(rules_dir, rule_file)
                        dest = os.path.join(project_path, "rules", rule_file)
                        shutil.copy(source, dest)
                        print(f"  - {source} → {dest}")
            else:
                print(f"  ! Warning: Rules directory not found")
        except Exception as e:
            print(f"  ! Warning: Issue copying rules: {e}")
            
        # Copy PM advisories to the project
        try:
            pm_advisories_dir = os.path.join("MultiMindPM/advisories", project_name)
            project_advisories_dir = os.path.join(project_path, "advisories")
            
            if os.path.exists(pm_advisories_dir) and os.path.isdir(pm_advisories_dir):
                for advisory_file in os.listdir(pm_advisories_dir):
                    if advisory_file.endswith(".md"):
                        source = os.path.join(pm_advisories_dir, advisory_file)
                        dest = os.path.join(project_advisories_dir, advisory_file)
                        
                        # Only copy if it's new or has been updated by the PM
                        if (not os.path.exists(dest) or 
                            os.path.getmtime(source) > os.path.getmtime(dest)):
                            shutil.copy(source, dest)
                            print(f"  - {source} → {project_advisories_dir}/{advisory_file}")
            else:
                # Create the PM advisories directory for this project if it doesn't exist
                os.makedirs(pm_advisories_dir, exist_ok=True)
                print(f"  - Created advisory directory: {pm_advisories_dir}")
        except Exception as e:
            print(f"  ! Warning: Issue with advisories: {e}")
    
    # Create local completion scripts for each project
    print("\nCreating local completion scripts...")
    for project in config["projects"]:
        project_name = project["name"]
        # Skip template projects without active development
        if project_name in ["ProjectOne", "ProjectTwo", "ProjectThree"] and not os.path.exists(os.path.join(project["path"], "reports/status.md")):
            continue
        create_project_completion_script(config, project_name)
    
    print("Sync complete!")


def gather_reports(config: Dict) -> None:
    """
    Gather status reports from project directories to the PM directory.
    """
    print("Gathering status reports from projects...")
    
    for project in config["projects"]:
        project_name = project["name"]
        project_path = project["path"]
        status_file = project["status_file"]
        
        print(f"Gathering report from {project_name}...")
        
        # Copy status.md to PM reports directory
        source = os.path.join(project_path, "reports/status.md")
        dest = os.path.join("MultiMindPM/reports", status_file)
        
        try:
            shutil.copy(source, dest)
            print(f"  - {source} → {dest}")
        except FileNotFoundError:
            print(f"  ! Warning: {source} not found")
        
        # Gather project advisories to the PM
        try:
            project_advisories_dir = os.path.join(project_path, "advisories")
            pm_advisories_dir = os.path.join("MultiMindPM/advisories", project_name)
            
            # Ensure the PM advisories directory exists
            os.makedirs(pm_advisories_dir, exist_ok=True)
            
            if os.path.exists(project_advisories_dir) and os.path.isdir(project_advisories_dir):
                for advisory_file in os.listdir(project_advisories_dir):
                    if advisory_file.endswith(".md"):
                        source = os.path.join(project_advisories_dir, advisory_file)
                        dest = os.path.join(pm_advisories_dir, advisory_file)
                        
                        # Only copy if it's new or has been updated by the project
                        if (not os.path.exists(dest) or 
                            os.path.getmtime(source) > os.path.getmtime(dest)):
                            shutil.copy(source, dest)
                            print(f"  - {source} → {dest}")
        except Exception as e:
            print(f"  ! Warning: Issue gathering advisories: {e}")
    
    print("Gather complete!")


def handle_handoffs(config: Dict) -> None:
    """
    Process handoff documents between projects.
    
    - Checks for new handoffs in output/handoffs
    - Moves them to MultiMindPM/handoffs
    - Lists all current handoffs
    """
    print("Processing handoffs...")
    
    # Ensure handoff directories exist
    pm_handoffs_dir = "MultiMindPM/handoffs"
    output_handoffs_dir = "output/handoffs"
    os.makedirs(pm_handoffs_dir, exist_ok=True)
    os.makedirs(output_handoffs_dir, exist_ok=True)
    
    # Check for new handoffs in output directory
    new_handoffs = []
    for handoff_file in os.listdir(output_handoffs_dir):
        if handoff_file.endswith(".md"):
            source = os.path.join(output_handoffs_dir, handoff_file)
            dest = os.path.join(pm_handoffs_dir, handoff_file)
            
            # Only copy if it doesn't exist in PM directory or is newer
            if (not os.path.exists(dest) or 
                os.path.getmtime(source) > os.path.getmtime(dest)):
                shutil.copy(source, dest)
                new_handoffs.append(handoff_file)
                print(f"  + New handoff: {handoff_file}")
    
    # List all current handoffs
    handoffs = []
    if os.path.exists(pm_handoffs_dir):
        for handoff_file in os.listdir(pm_handoffs_dir):
            if handoff_file.endswith(".md"):
                handoffs.append(handoff_file)
    
    if handoffs:
        print("\nCurrent handoffs:")
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
            
            print(f"  - {handoff} [{status}]")
    else:
        print("\nNo current handoffs.")
    
    print("Handoff processing complete!")


def handle_advisories(config: Dict) -> None:
    """
    List all advisories and their statuses.
    """
    print("Processing advisories...")
    
    # Ensure PM advisories directory exists
    pm_advisories_base_dir = "MultiMindPM/advisories"
    os.makedirs(pm_advisories_base_dir, exist_ok=True)
    
    for project in config["projects"]:
        project_name = project["name"]
        project_advisories_dir = os.path.join(pm_advisories_base_dir, project_name)
        
        # Skip if this project doesn't have any advisories yet
        if not os.path.exists(project_advisories_dir) or not os.path.isdir(project_advisories_dir):
            continue
        
        advisories = []
        for advisory_file in os.listdir(project_advisories_dir):
            if advisory_file.endswith(".md"):
                # Try to extract status from the file
                status = "UNKNOWN"
                try:
                    with open(os.path.join(project_advisories_dir, advisory_file), 'r') as f:
                        for line in f:
                            if line.startswith("Status:"):
                                status = line.strip().split("Status:")[1].strip()
                                break
                except:
                    pass
                
                advisories.append((advisory_file, status))
        
        if advisories:
            print(f"\nAdvisories for {project_name}:")
            for advisory, status in sorted(advisories):
                print(f"  - {advisory} [{status}]")
    
    print("Advisory processing complete!")


def report_completion(config: Dict, project_name: str, phase_id: str, only_project: bool = False) -> None:
    """
    Process and record a project phase completion.
    
    This function:
    1. Creates a completion marker file
    2. Collects status reports
    3. Notifies the PM of the completion
    
    Args:
        config: The configuration dictionary
        project_name: Name of the project that completed a phase
        phase_id: Identifier for the completed phase
        only_project: If True, only report on the specified project (don't list all completions)
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
        return
    
    # Skip template projects (ProjectOne, ProjectTwo, ProjectThree)
    if project_name in ["ProjectOne", "ProjectTwo", "ProjectThree"] and not os.path.exists(os.path.join(project_path, "reports/status.md")):
        print(f"Error: '{project_name}' appears to be a template project without active development")
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
        print(f"  - Completion marker copied: {source_path} → {dest_path}")
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
        print(f"  - Created basic completion marker: {dest_path}")
    
    # Gather status report
    print(f"  - Collecting status report...")
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
            print(f"  - Status report updated: {source} → {dest}")
        except FileNotFoundError:
            print(f"  ! Warning: Status report not found at {source}")
    
    # If only_project is True, skip listing all completions
    if only_project:
        print(f"\nCompletion report for {project_name} - {phase_id} processed!")
        return
    
    # List active project completions (skip template projects)
    print("\nCurrent phase completions:")
    active_projects = {p["name"] for p in config["projects"] 
                       if p["name"] not in ["ProjectOne", "ProjectTwo", "ProjectThree"] 
                       or os.path.exists(os.path.join(p["path"], "reports/status.md"))}
    
    completions = []
    if os.path.exists(pm_completions_dir):
        for file in os.listdir(pm_completions_dir):
            if file.endswith("-complete.md"):
                # Extract project name from filename (format: ProjectName-PhaseID-complete.md)
                file_project = file.split("-")[0]
                # Only include if it's an active project in this workspace
                if file_project in active_projects:
                    completions.append(file)
    
    if completions:
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
            
            print(f"  - {completion} [{date}]")
    else:
        print("  No completions found for active projects.")
    
    print("\nCompletion report processed! The PM will review and update the roadmap.")
    print("Run './multimind.py sync' later to receive updated directives.")


def create_project_completion_script(config: Dict, project_name: str) -> bool:
    """
    Create a local completion script for a project.
    
    This allows project teams to report phase completion without leaving their directory.
    
    Args:
        config: The configuration dictionary
        project_name: Name of the project to create the script for
        
    Returns:
        bool: True if successful, False otherwise
    """
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
        return False
    
    # Skip template projects if they don't have active development
    if project_name in ["ProjectOne", "ProjectTwo", "ProjectThree"] and not os.path.exists(os.path.join(project_path, "reports/status.md")):
        print(f"Skipping '{project_name}' as it appears to be a template project")
        return False
    
    # Create scripts directory if it doesn't exist
    scripts_dir = os.path.join(project_path, "scripts")
    os.makedirs(scripts_dir, exist_ok=True)
    
    # Define the script path
    script_path = os.path.join(scripts_dir, "complete_phase.py")
    
    # Check if the template exists
    template_path = "MultiMindPM/templates/complete_phase.py"
    if not os.path.exists(template_path):
        print(f"Error: Template script not found at {template_path}")
        return False
    
    # Read the template
    with open(template_path, "r") as f:
        template_content = f.read()
    
    # Replace the project name in the template
    script_content = template_content.replace("{{PROJECT_NAME}}", project_name)
    
    # Write the customized script
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make the script executable
    try:
        os.chmod(script_path, 0o755)  # rwxr-xr-x
    except:
        # Chmod might fail on some platforms, that's okay
        pass
        
    print(f"Created completion script: {script_path}")
    print(f"Projects can now run: 'python scripts/complete_phase.py Phase1' from their directory")
    
    return True


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
            "src/utils", "src/tests"]
    
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
    
    print(f"Project {project_name} initialized successfully!")
    
    # Update config to include new project
    directive_file = f"{project_name.lower()}.md"
    status_file = f"{project_name.lower()}-status.md"
    
    # Create empty directive file
    with open(os.path.join("MultiMindPM/directives", directive_file), 'w') as f:
        f.write(f"# {project_name} Directives\n\nVersion: 0.1.0\n\n## Current Tasks\n\n1. Define project requirements\n")
    
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
    
    # Create local completion script for the new project
    create_project_completion_script(config, project_name)


def create_all_completion_scripts(config: Dict) -> None:
    """
    Create local completion scripts for all active projects.
    """
    print("Creating local completion scripts for all projects...")
    
    # Ensure templates directory exists
    os.makedirs("MultiMindPM/templates", exist_ok=True)
    
    # Check if template exists, create it if not
    template_path = "MultiMindPM/templates/complete_phase.py"
    if not os.path.exists(template_path):
        print(f"! Warning: Template script not found. Please run 'sync' command first.")
        return
    
    # Create scripts for each project
    success_count = 0
    for project in config["projects"]:
        project_name = project["name"]
        if create_project_completion_script(config, project_name):
            success_count += 1
    
    print(f"\nCreated completion scripts for {success_count} projects.")
    print("Each project can now report completion from their own directory.")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="MultiMind - Project Orchestration Tool")
    
    # Define subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Sync command
    sync_parser = subparsers.add_parser("sync", help="Sync files from PM to projects")
    
    # Gather command
    gather_parser = subparsers.add_parser("gather", help="Gather reports from projects to PM")
    
    # Handoffs command
    handoffs_parser = subparsers.add_parser("handoffs", help="Process handoffs between projects")
    
    # Advisories command
    advisories_parser = subparsers.add_parser("advisories", help="List all advisories and their statuses")
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Report phase completion")
    complete_parser.add_argument("project_name", help="Name of the project")
    complete_parser.add_argument("phase_id", help="Identifier for the completed phase")
    complete_parser.add_argument("--only-project", action="store_true", 
                                help="Only report on the specified project (don't list all completions)")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("project_name", help="Name of the new project")
    
    # Create local completion scripts command
    scripts_parser = subparsers.add_parser("create-scripts", 
                                         help="Create local completion scripts for projects")
    scripts_parser.add_argument("--project", help="Create script for specific project (default: all)")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Process command
    if args.command == "sync":
        sync_files(config)
    elif args.command == "gather":
        gather_reports(config)
    elif args.command == "handoffs":
        handle_handoffs(config)
    elif args.command == "advisories":
        handle_advisories(config)
    elif args.command == "complete":
        only_project = getattr(args, "only_project", False)
        report_completion(config, args.project_name, args.phase_id, only_project)
    elif args.command == "init":
        init_project(config, args.project_name)
    elif args.command == "create-scripts":
        if hasattr(args, "project") and args.project:
            create_project_completion_script(config, args.project)
        else:
            create_all_completion_scripts(config)
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 