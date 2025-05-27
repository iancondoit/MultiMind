#!/usr/bin/env python
"""
show_version.py - Display StoryDredge version information

This script displays the current version of StoryDredge and saves
the version information to a JSON file.
"""

import sys
import os
import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.version import (
    get_version, 
    get_version_tuple, 
    print_version_info, 
    save_version_info
)

def main():
    """Display version information and save to a file."""
    print("\nStoryDredge Version Information")
    print("==============================\n")
    
    # Print version information
    print_version_info()
    
    # Save version information to a JSON file
    save_version_info()
    
    # Print additional information
    print("\nVersion History:")
    print("- v1.0.0: First stable release with improved pipeline")
    print("  - Rule-based classification for faster processing")
    print("  - Enhanced entity extraction in tags")
    print("  - Improved directory structure")
    print("  - Comprehensive test suite")
    
    print("\nFor full details, see docs/CHANGELOG.md")
    
    # Print instructions for tagging a release
    print("\nTo tag this version for release:")
    print(f"git tag -a v{get_version()} -m \"Version {get_version()} release\"")
    print(f"git push origin v{get_version()}")

if __name__ == "__main__":
    main() 