#!/usr/bin/env python3
"""
Project-specific phase completion script.

This script allows project teams to report phase completions without leaving their project directory.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Set project-specific variables
PROJECT_NAME = "MasterBus"  # This will be replaced during customization
ROOT_DIR = Path(__file__).parent.parent.parent  # Assumes this script is in PROJECT/scripts/
OUTPUT_DIR = ROOT_DIR / "output" / "completions"

def report_completion(phase_id):
    """
    Report completion of a phase by calling the root multimind.py script.
    
    Args:
        phase_id: Identifier for the completed phase (e.g., "Phase1")
    """
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Build the path to the root multimind.py script
    multimind_script = ROOT_DIR / "multimind.py"
    
    if not multimind_script.exists():
        print(f"Error: Could not find multimind.py at {multimind_script}")
        sys.exit(1)
    
    # Run the completion command
    try:
        print(f"Reporting completion of {phase_id} for {PROJECT_NAME}...")
        cmd = [sys.executable, str(multimind_script), "complete", PROJECT_NAME, phase_id]
        
        # Use --only-project flag to only report on this project
        cmd.append("--only-project")
        
        result = subprocess.run(cmd, cwd=ROOT_DIR)
        
        if result.returncode == 0:
            print(f"\nSuccess! Completion of {PROJECT_NAME} - {phase_id} has been reported.")
            print("The Project Manager will review your completion and update directives.")
        else:
            print(f"\nError: Command failed with exit code {result.returncode}")
            sys.exit(result.returncode)
    except Exception as e:
        print(f"Error executing completion command: {e}")
        sys.exit(1)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description=f"Report phase completion for {PROJECT_NAME}"
    )
    parser.add_argument(
        "phase_id", 
        help="Identifier for the completed phase (e.g., 'Phase1', 'Phase2')"
    )
    
    args = parser.parse_args()
    report_completion(args.phase_id)

if __name__ == "__main__":
    main() 