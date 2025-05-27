#!/usr/bin/env python3
"""
Test runner for StoryDredge.

This script runs pytest with appropriate configuration for the StoryDredge project.
"""

import sys
import os
import subprocess


def run_tests(args):
    """Run pytest with the given arguments."""
    base_cmd = [
        "pytest",
        "-xvs",  # Verbose output, stop on first failure
        "--color=yes"  # Force color output
    ]
    
    # Add any additional arguments from command line
    full_cmd = base_cmd + args
    
    # Run the tests
    print(f"Running: {' '.join(full_cmd)}")
    result = subprocess.run(full_cmd)
    return result.returncode


if __name__ == "__main__":
    # Parse arguments and run tests
    exit_code = run_tests(sys.argv[1:])
    sys.exit(exit_code) 