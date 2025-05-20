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
    """
    print("Syncing files from PM to projects...")
    
    for project in config["projects"]:
        project_name = project["name"]
        project_path = project["path"]
        directive_file = project["directive_file"]
        
        print(f"Syncing to {project_name}...")
        
        # Ensure directories exist
        ensure_dirs(project_path, "directives")
        ensure_dirs(project_path, "reports")
        ensure_dirs(project_path, "rules")
        
        # Copy README.md
        try:
            shutil.copy("MultiMindPM/README.md", os.path.join(project_path, "README.md"))
            print(f"  - README.md → {project_path}/README.md")
        except FileNotFoundError:
            print(f"  ! Warning: MultiMindPM/README.md not found")
        
        # Copy roadmap.md
        try:
            shutil.copy("MultiMindPM/roadmap.md", os.path.join(project_path, "roadmap.md"))
            print(f"  - roadmap.md → {project_path}/roadmap.md")
        except FileNotFoundError:
            print(f"  ! Warning: MultiMindPM/roadmap.md not found")
        
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


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="MultiMind - Project Orchestration Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # sync command
    sync_parser = subparsers.add_parser("sync", help="Push files to projects")
    
    # gather command
    gather_parser = subparsers.add_parser("gather", help="Collect status reports")
    
    # handoffs command
    handoffs_parser = subparsers.add_parser("handoffs", help="Process handoffs between projects")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("project_name", help="Name of the new project")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config = load_config()
    
    if args.command == "sync":
        sync_files(config)
    elif args.command == "gather":
        gather_reports(config)
    elif args.command == "handoffs":
        handle_handoffs(config)
    elif args.command == "init":
        init_project(config, args.project_name)


if __name__ == "__main__":
    main() 