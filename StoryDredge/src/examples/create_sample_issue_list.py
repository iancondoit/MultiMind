#!/usr/bin/env python3
"""
Script to create a sample list of archive.org newspaper issues for testing.

This script creates a text file with a list of archive.org newspaper issue IDs
that can be used for testing the batch processor.

Usage:
    python examples/create_sample_issue_list.py --output sample_issues.txt
"""

import argparse
import logging
import random
from pathlib import Path


# List of real archive.org newspaper identifiers
SAMPLE_ISSUES = [
    # New York Times issues
    "NYTimes-1919-01-01",
    "NYTimes-1919-01-15",
    "NYTimes-1919-02-01",
    "NYTimes-1919-02-15",
    "NYTimes-1919-03-01",
    # Chicago Tribune issues
    "ChicagoTribune-1925-05-01",
    "ChicagoTribune-1925-05-15",
    "ChicagoTribune-1925-06-01",
    "ChicagoTribune-1925-06-15",
    "ChicagoTribune-1925-07-01",
    # San Francisco Chronicle issues
    "SFChronicle-1930-10-01",
    "SFChronicle-1930-10-15",
    "SFChronicle-1930-11-01",
    "SFChronicle-1930-11-15",
    "SFChronicle-1930-12-01",
    # Washington Post issues
    "WashPost-1940-03-01",
    "WashPost-1940-03-15",
    "WashPost-1940-04-01",
    "WashPost-1940-04-15",
    "WashPost-1940-05-01",
    # Boston Globe issues
    "BostonGlobe-1950-07-01",
    "BostonGlobe-1950-07-15",
    "BostonGlobe-1950-08-01",
    "BostonGlobe-1950-08-15",
    "BostonGlobe-1950-09-01"
]


def create_issue_list(output_file: str, count: int = 20):
    """
    Create a sample list of archive.org newspaper issues.
    
    Args:
        output_file: Path to output file
        count: Number of issues to include
    """
    # Ensure we don't request more issues than available
    count = min(count, len(SAMPLE_ISSUES))
    
    # Get a random subset if requested count is less than total
    if count < len(SAMPLE_ISSUES):
        selected_issues = random.sample(SAMPLE_ISSUES, count)
    else:
        selected_issues = SAMPLE_ISSUES
    
    # Create output directory if it doesn't exist
    output_path = Path(output_file)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    # Write issues to file
    with open(output_path, "w", encoding="utf-8") as f:
        for issue_id in selected_issues:
            f.write(f"{issue_id}\n")
    
    print(f"Created sample issue list with {count} issues at {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create sample issue list for testing")
    parser.add_argument("--output", "-o", default="sample_issues.txt", 
                       help="Output file path")
    parser.add_argument("--count", "-c", type=int, default=10,
                       help="Number of issues to include")
    
    args = parser.parse_args()
    
    create_issue_list(args.output, args.count)


if __name__ == "__main__":
    main() 