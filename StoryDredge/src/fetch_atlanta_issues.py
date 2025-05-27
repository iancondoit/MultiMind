#!/usr/bin/env python3
"""
Fetch 100 Atlanta Constitution issues and save their IDs to a JSON file
for processing with the StoryDredge pipeline.
"""
import os
import json
import sys
from pathlib import Path

# Ensure the project root is in the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.fetcher.archive_fetcher import ArchiveFetcher
except ImportError:
    print("Error: Could not import ArchiveFetcher. Make sure you're running this script from the StoryDredge root directory.")
    sys.exit(1)

# Create output directory
os.makedirs("data", exist_ok=True)

# Initialize fetcher
fetcher = ArchiveFetcher()

try:
    # Search for Atlanta Constitution issues from 1910-1925
    print("Searching for Atlanta Constitution issues...")
    issues = fetcher.search_newspaper_collection(
        collection='pub_atlanta-constitution',
        date_range=('1910-01-01', '1925-12-31'),
        limit=100
    )
    
    if not issues:
        print("Error: No issues found. Check if the collection ID is correct.")
        sys.exit(1)
    
    print(f"Found {len(issues)} issues")
    
    # Extract identifiers
    issue_ids = [issue.get('identifier') for issue in issues if 'identifier' in issue]
    
    # Save to JSON file
    output_file = "data/atlanta_constitution_issues.json"
    with open(output_file, 'w') as f:
        json.dump({"issues": issue_ids}, f, indent=2)
    
    print(f"Saved {len(issue_ids)} issue IDs to {output_file}")
    print("\nYou can now run the pipeline with:")
    print(f"  ./scripts/run_universal_pipeline.sh --issues-file {output_file} --output-dir output/atlanta-constitution")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    # Always close the fetcher
    fetcher.close() 