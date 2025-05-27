"""
version.py - Version information for StoryDredge

This module provides version information and utility functions
for StoryDredge.
"""

import json
from pathlib import Path

# Version information
VERSION_MAJOR = 1
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

# Build status
BUILD_STATUS = "stable"

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

def get_version():
    """Return the current version string."""
    return VERSION

def get_version_tuple():
    """Return the current version as a tuple of (major, minor, patch)."""
    return (VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)

def get_version_info():
    """Return a dictionary with version information."""
    return {
        "version": VERSION,
        "build_status": BUILD_STATUS,
        "timestamp": None  # Will be filled in at build time
    }

def print_version_info():
    """Print version information to the console."""
    print(f"StoryDredge v{VERSION} ({BUILD_STATUS})")
    print(f"Improved entity extraction and rule-based classification")
    print(f"Directory structure optimized")

def save_version_info():
    """Save version information to a JSON file."""
    version_file = PROJECT_ROOT / "version.json"
    
    version_info = {
        "name": "StoryDredge",
        "version": VERSION,
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH,
        "build_status": BUILD_STATUS
    }
    
    with open(version_file, 'w') as f:
        json.dump(version_info, f, indent=2)
    
    print(f"Version information saved to {version_file}")

if __name__ == "__main__":
    # If run directly, display version information
    print_version_info()
    
    # Also save version info to JSON
    save_version_info() 