#!/usr/bin/env python3
"""
Test script to verify the HSAFormatter format_issue method.

This script creates dummy article data and passes it to the HSAFormatter
to verify that the articles are correctly processed into the publication/year/month/day
directory structure.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Ensure we can import from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.formatter.hsa_formatter import HSAFormatter


def create_test_data(output_dir: Path, issue_id: str, num_articles: int = 5):
    """
    Create dummy classified article data for testing.
    
    Args:
        output_dir: Directory to store the test data
        issue_id: The archive.org identifier to use
        num_articles: Number of dummy articles to create
    
    Returns:
        Path to the classified directory
    """
    # Create directory structure
    issue_dir = output_dir / issue_id
    classified_dir = issue_dir / "classified"
    classified_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract date from issue_id (e.g., per_atlanta-constitution_1922-01-01_54_203)
    date_part = issue_id.split('_')[2] if len(issue_id.split('_')) > 2 else "1922-01-01"
    
    # Create some dummy articles
    for i in range(num_articles):
        article = {
            "title": f"Test Article {i+1}",
            "raw_text": f"This is the content of test article {i+1}. It contains sample text for testing the formatter.",
            "source_issue": issue_id,
            "category": ["news", "sports", "business", "opinion", "entertainment"][i % 5],
            "metadata": {
                "topic": "Politics",
                "people": ["John Doe", "Jane Smith"],
                "organizations": ["Acme Corp", "Government"],
                "locations": ["Atlanta", "Georgia"]
            }
        }
        
        # Save the article
        article_file = classified_dir / f"article_{i:04d}.json"
        with open(article_file, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=2)
    
    return classified_dir


def verify_output(output_dir: Path, issue_id: str):
    """
    Verify that the output follows the expected directory structure.
    
    Args:
        output_dir: Base output directory
        issue_id: The issue ID used for the test
    
    Returns:
        True if verification passes, False otherwise
    """
    # Extract date from issue_id (e.g., per_atlanta-constitution_1922-01-01_54_203)
    date_parts = issue_id.split('_')
    if len(date_parts) > 2:
        date_str = date_parts[2]  # 1922-01-01
        date_components = date_str.split('-')
        if len(date_components) == 3:
            year, month, day = date_components
            
            # Expected directory structure: output_dir/hsa-ready/YYYY/MM/DD/*.json
            expected_dir = output_dir / "hsa-ready" / year / month / day
            
            # Check if the directory exists
            if not expected_dir.exists():
                print(f"ERROR: Expected directory {expected_dir} does not exist")
                return False
            
            # Check if there are any JSON files
            json_files = list(expected_dir.glob("*.json"))
            if not json_files:
                print(f"ERROR: No JSON files found in {expected_dir}")
                return False
            
            # Verify content of a JSON file
            sample_file = json_files[0]
            try:
                with open(sample_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                
                # Check required fields
                for field in ["headline", "body", "tags", "section", "timestamp", 
                              "publication", "source_issue", "source_url"]:
                    if field not in article:
                        print(f"ERROR: Missing field '{field}' in output JSON")
                        return False
                
                # Verify date formatting in timestamp
                if not article["timestamp"].startswith(f"{year}-{month}-{day}"):
                    print(f"ERROR: Expected timestamp to start with {year}-{month}-{day}, got {article['timestamp']}")
                    return False
                
                print(f"SUCCESS: Verification passed. Found {len(json_files)} articles in {expected_dir}")
                return True
            
            except Exception as e:
                print(f"ERROR: Failed to validate JSON file: {e}")
                return False
    
    print(f"ERROR: Could not extract date from issue_id: {issue_id}")
    return False


def main():
    """Run the test script."""
    # Create a temporary directory for testing
    test_dir = Path("test_formatter_output")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir(parents=True)
    
    try:
        # Test issue ID
        issue_id = "per_atlanta-constitution_1922-01-01_54_203"
        
        print(f"Creating test data for issue: {issue_id}")
        classified_dir = create_test_data(test_dir, issue_id)
        
        print(f"Initializing HSAFormatter with output directory: {test_dir}")
        formatter = HSAFormatter(output_dir=test_dir)
        
        print("Processing articles with format_issue method")
        result_paths = formatter.format_issue(issue_id, classified_dir)
        
        print(f"Processed {len(result_paths)} articles")
        
        # Debug: Show what files and directories were actually created
        print("\nDEBUG: Actual directories created:")
        for path in sorted(Path(test_dir).glob("**/")):
            print(f"  {path}")
        
        print("\nDEBUG: Actual JSON files created:")
        for path in sorted(Path(test_dir).glob("**/*.json")):
            print(f"  {path}")
            # Print the first few lines of each JSON file
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    print(f"    headline: {data.get('headline', 'N/A')}")
                    print(f"    timestamp: {data.get('timestamp', 'N/A')}")
                    print(f"    publication: {data.get('publication', 'N/A')}")
                    print(f"    source_issue: {data.get('source_issue', 'N/A')}")
            except:
                print("    Error reading JSON file")
        
        print("\nVerifying output directory structure")
        if verify_output(test_dir, issue_id):
            print("\nTEST PASSED: HSAFormatter is correctly structuring the output")
        else:
            print("\nTEST FAILED: Output directory structure is incorrect")
        
    finally:
        # Uncomment to clean up
        # if test_dir.exists():
        #     shutil.rmtree(test_dir)
        pass


if __name__ == "__main__":
    main() 