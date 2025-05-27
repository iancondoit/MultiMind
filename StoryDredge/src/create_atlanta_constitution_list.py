#!/usr/bin/env python3
"""
Create a list of 100 Atlanta Constitution issues for processing with StoryDredge.
This script creates a file with 100 issue IDs from archive.org for the Atlanta Constitution.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# Define date range - focusing on early 20th century
START_DATE = datetime(1910, 1, 1)
END_DATE = datetime(1925, 12, 31)

# Function to generate a random date within our range
def random_date(start, end):
    """Generate a random date between start and end dates"""
    delta = end - start
    random_days = random.randrange(delta.days)
    return start + timedelta(days=random_days)

# Function to create an archive.org ID for the Atlanta Constitution
def create_archive_id(date):
    """Create an archive.org ID for the Atlanta Constitution based on date"""
    # Format is typically: per_atlanta-constitution_YYYY-MM-DD
    return f"per_atlanta-constitution_{date.strftime('%Y-%m-%d')}"

# Generate 100 random issue IDs
def generate_issue_ids(count=100):
    """Generate a specified number of unique issue IDs"""
    issue_ids = set()
    
    while len(issue_ids) < count:
        date = random_date(START_DATE, END_DATE)
        issue_id = create_archive_id(date)
        issue_ids.add(issue_id)
    
    return sorted(list(issue_ids))

# Save the issue IDs to a file
def save_issue_ids(issue_ids, output_file="data/atlanta_constitution_issues.txt"):
    """Save the issue IDs to a file"""
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write the IDs to the file
    with open(output_file, "w") as f:
        for issue_id in issue_ids:
            f.write(f"{issue_id}\n")
    
    # Also create a JSON version for compatibility with some tools
    json_file = output_file.replace(".txt", ".json")
    with open(json_file, "w") as f:
        json.dump({"issues": issue_ids}, f, indent=2)
    
    return output_file, json_file

def main():
    """Main function"""
    print("Generating 100 random Atlanta Constitution issue IDs...")
    issue_ids = generate_issue_ids(100)
    
    txt_file, json_file = save_issue_ids(issue_ids)
    
    print(f"Generated {len(issue_ids)} issue IDs.")
    print(f"Text file saved to: {txt_file}")
    print(f"JSON file saved to: {json_file}")
    print("\nSample issue IDs:")
    for i in range(min(5, len(issue_ids))):
        print(f"  {issue_ids[i]}")
    
    print("\nYou can run the pipeline with:")
    print(f"  ./scripts/run_universal_pipeline.sh --issues-file {json_file}")

if __name__ == "__main__":
    main() 