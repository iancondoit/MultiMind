#!/usr/bin/env python3
"""
Fetch a list of 100 actual Atlanta Constitution issues from archive.org
for processing with StoryDredge using the built-in fetcher component.
"""

import os
import sys
import json
from pathlib import Path
import logging

# Add the project root to the path to import StoryDredge modules
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fetcher_script")

# Import the fetcher component from StoryDredge
try:
    from src.fetcher.archive_fetcher import ArchiveFetcher
except ImportError:
    logger.error("Could not import ArchiveFetcher. Make sure you're running this script from the StoryDredge root directory.")
    sys.exit(1)

def fetch_issues(count=100, output_dir="data"):
    """
    Fetch a specified number of Atlanta Constitution issues from archive.org
    
    Args:
        count: Number of issues to fetch
        output_dir: Directory to save the issue lists
        
    Returns:
        Path to the JSON file containing the issue IDs
    """
    logger.info(f"Fetching {count} Atlanta Constitution issues from archive.org")
    
    # Initialize the fetcher
    fetcher = ArchiveFetcher()
    
    # Search for Atlanta Constitution issues
    # The collection ID for the Atlanta Constitution is "pub_atlanta-constitution"
    collection = "pub_atlanta-constitution"
    
    # We'll look for issues from 1910-1925 (early 20th century)
    date_range = ("1910-01-01", "1925-12-31")
    
    # Request more than we need in case some are duplicates or have issues
    fetch_count = min(count * 2, 200)  # Get up to 200 issues
    
    logger.info(f"Searching for {fetch_count} issues in collection {collection} from {date_range[0]} to {date_range[1]}")
    
    # Fetch the issues
    try:
        issues = fetcher.get_newspaper_issues(
            collection=collection,
            date_range=date_range,
            limit=fetch_count
        )
        
        if not issues:
            logger.error(f"No issues found for collection {collection}")
            sys.exit(1)
            
        logger.info(f"Found {len(issues)} issues")
        
        # Extract just the identifiers and limit to the number requested
        issue_ids = [issue.get("identifier", "") for issue in issues if "identifier" in issue]
        issue_ids = [id for id in issue_ids if id]  # Remove any empty IDs
        issue_ids = issue_ids[:count]  # Limit to requested count
        
        if len(issue_ids) < count:
            logger.warning(f"Only found {len(issue_ids)} valid issues, which is less than the requested {count}")
        
        # Create the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the issue IDs to text and JSON files
        txt_file = os.path.join(output_dir, "atlanta_constitution_issues.txt")
        json_file = os.path.join(output_dir, "atlanta_constitution_issues.json")
        
        # Write the IDs to the text file
        with open(txt_file, "w") as f:
            for issue_id in issue_ids:
                f.write(f"{issue_id}\n")
        
        # Write the IDs to the JSON file
        with open(json_file, "w") as f:
            json.dump({"issues": issue_ids}, f, indent=2)
        
        logger.info(f"Saved {len(issue_ids)} issue IDs to {txt_file} and {json_file}")
        
        # Close the fetcher
        fetcher.close()
        
        return json_file
        
    except Exception as e:
        logger.error(f"Error fetching issues: {e}")
        sys.exit(1)

def main():
    """Main function"""
    json_file = fetch_issues(100)
    
    print("\nYou can now run the pipeline with:")
    print(f"  ./scripts/run_universal_pipeline.sh --issues-file {json_file}")
    print("\nOr to process a single issue, run:")
    print("  ./scripts/run_universal_pipeline.sh --issue ISSUE_ID")
    print("\nWhere ISSUE_ID is one of the IDs from the file.")

if __name__ == "__main__":
    main() 