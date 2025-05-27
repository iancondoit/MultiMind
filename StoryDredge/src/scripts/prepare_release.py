#!/usr/bin/env python
"""
prepare_release.py - Prepare StoryDredge for version 1.0.0 release

This script prepares release artifacts for StoryDredge, including:
1. A zip file with the source code
2. Release notes
3. Version information
"""

import sys
import os
import json
import datetime
import shutil
import zipfile
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.version import get_version, get_version_info, save_version_info

def create_dist_directory():
    """Create or clean the dist directory."""
    dist_dir = Path("dist")
    
    # Create the directory if it doesn't exist
    if not dist_dir.exists():
        dist_dir.mkdir()
        print(f"Created dist directory: {dist_dir}")
    else:
        # Clean the directory
        for item in dist_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print(f"Cleaned dist directory: {dist_dir}")
    
    return dist_dir

def create_release_archive(dist_dir):
    """Create a zip archive of the source code."""
    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get version
    version = get_version()
    
    # Define the release filename
    release_filename = f"storydredge-{version}-{timestamp}.zip"
    release_path = dist_dir / release_filename
    
    # Create the zip file
    with zipfile.ZipFile(release_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # List of directories to include
        dirs_to_include = ["src", "scripts", "config", "docs", "pipeline", "tests"]
        
        # List of files to include
        files_to_include = ["README.md", "LICENSE", "requirements.txt"]
        
        # Add directories
        for dir_name in dirs_to_include:
            dir_path = Path(dir_name)
            if dir_path.exists():
                for file_path in dir_path.glob('**/*'):
                    if file_path.is_file():
                        # Use arcname to specify the path inside the zip file
                        zipf.write(file_path, arcname=str(file_path))
        
        # Add individual files
        for file_name in files_to_include:
            file_path = Path(file_name)
            if file_path.exists():
                zipf.write(file_path, arcname=str(file_path))
    
    print(f"Created release archive: {release_path}")
    return release_path

def create_manifest_file(dist_dir, release_path):
    """Create a manifest file with release information."""
    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create the manifest
    manifest = {
        "name": "StoryDredge",
        "version": get_version(),
        "release_date": timestamp,
        "release_file": str(release_path.name),
        "release_size": release_path.stat().st_size,
        "description": "StoryDredge pipeline for processing newspaper OCR text",
        "repository": "https://github.com/yourusername/storydredge",
        "authors": ["StoryDredge Team"],
        "license": "MIT"
    }
    
    # Write the manifest to a file
    manifest_path = dist_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Created manifest file: {manifest_path}")
    return manifest

def create_release_notes(dist_dir, manifest):
    """Create release notes for the current version."""
    # Get the version history from CHANGELOG.md
    changelog_path = Path("docs/CHANGELOG.md")
    changelog_content = ""
    if changelog_path.exists():
        with open(changelog_path, 'r') as f:
            changelog_content = f.read()
    
    # Create the release notes
    release_notes = f"""# StoryDredge {manifest['version']} Release Notes

## Overview

StoryDredge {manifest['version']} is a complete implementation of the newspaper OCR processing pipeline
designed to extract structured articles from historical newspapers.

## Key Features

1. **Fast Rule-based Classification**: Articles are now classified using a high-performance rule-based system by default, processing hundreds of articles in under a second.

2. **Enhanced Entity Extraction**: The system now extracts people, organizations, and locations from articles and adds them to the tags array in the HSA-ready output.

3. **Improved Directory Structure**: The pipeline now uses a cleaner directory structure with temporary files stored in a dedicated temp directory and final output in the properly organized hsa-ready folder.

4. **Comprehensive Testing**: New test scripts verify all aspects of the pipeline, including directory structure, rule-based classification, and entity tag extraction.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/storydredge.git
cd storydredge

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Release Information

- **Version**: {manifest['version']}
- **Release Date**: {manifest['release_date']}
- **License**: {manifest['license']}

## Changelog

{changelog_content}
"""
    
    # Write the release notes to a file
    release_notes_path = dist_dir / f"RELEASE_NOTES_{manifest['version']}.md"
    with open(release_notes_path, 'w') as f:
        f.write(release_notes)
    
    print(f"Created release notes: {release_notes_path}")
    return release_notes_path

def main():
    """Main function to prepare the release."""
    print("\nPreparing StoryDredge Release")
    print("============================\n")
    
    # Save version information
    save_version_info()
    
    # Create or clean the dist directory
    dist_dir = create_dist_directory()
    
    # Create the release archive
    release_path = create_release_archive(dist_dir)
    
    # Create the manifest file
    manifest = create_manifest_file(dist_dir, release_path)
    
    # Create the release notes
    release_notes_path = create_release_notes(dist_dir, manifest)
    
    print("\nRelease preparation complete!")
    print(f"Version: {get_version()}")
    print(f"Release archive: {release_path}")
    print(f"Release notes: {release_notes_path}")
    print("\nNext steps:")
    print("1. Review the release notes")
    print("2. Tag the release in git:")
    print(f"   git tag -a v{get_version()} -m \"Version {get_version()} release\"")
    print(f"   git push origin v{get_version()}")

if __name__ == "__main__":
    main() 