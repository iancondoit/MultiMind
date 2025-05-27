#!/usr/bin/env python3
"""
Test script to run the OCR processing pipeline on a sample file.
"""

import os
import sys
import json
import shutil
from pathlib import Path

# Issue to process
ISSUE_ID = "per_atlanta-constitution_1922-01-01_54_203"
TEMP_FILE = f"temp_downloads/{ISSUE_ID}.txt"
OUTPUT_DIR = "output"

def setup_directories():
    """Set up the required directory structure."""
    # Create output directories
    issue_dir = Path(OUTPUT_DIR) / ISSUE_ID
    issue_dir.mkdir(parents=True, exist_ok=True)
    
    # Create articles and classified directories
    articles_dir = issue_dir / "articles"
    classified_dir = issue_dir / "classified"
    articles_dir.mkdir(exist_ok=True)
    classified_dir.mkdir(exist_ok=True)
    
    # Copy the raw OCR file
    raw_file = issue_dir / "raw.txt"
    if not raw_file.exists():
        print(f"Copying OCR file from {TEMP_FILE} to {raw_file}")
        shutil.copy(TEMP_FILE, raw_file)
    else:
        print(f"Raw OCR file already exists at {raw_file}")
    
    return True

def run_pipeline():
    """Run the OCR processing pipeline."""
    from pipeline.process_ocr import process_ocr
    
    success = process_ocr(
        issue_id=ISSUE_ID,
        skip_fetch=True,
        output_dir=OUTPUT_DIR
    )
    
    if success:
        print("Pipeline completed successfully!")
    else:
        print("Pipeline failed!")
    
    return success

def test_formatter_byline():
    """Test the HSA formatter's handling of bylines."""
    from src.formatter.hsa_formatter import HSAFormatter
    
    print("Testing byline extraction...")
    
    formatter = HSAFormatter()
    
    # Test case 1: Article with byline in title
    test_article1 = {
        "title": "BY HENSON TATUM",
        "raw_text": "BUILDING BOOM CONTINUES\n\nwing an unprecedented building boom in Atlanta, contractors report...",
        "section": "news",
        "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
        "publication": "The Atlanta Constitution"
    }
    
    # Test case 2: Article with separate byline
    test_article2 = {
        "headline": "MAYOR ANNOUNCES NEW CITY PLAN",
        "byline": "John Smith",
        "raw_text": "The mayor announced a new city planning initiative yesterday...",
        "section": "news",
        "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
        "publication": "The Atlanta Constitution"
    }
    
    # Format and display results
    result1 = formatter.format_article(test_article1)
    result2 = formatter.format_article(test_article2)
    
    print("\nTest Case 1 (Byline in title):")
    print(f"Headline: {result1['headline']}")
    print(f"Byline: {result1['byline']}")
    
    print("\nTest Case 2 (Separate byline):")
    print(f"Headline: {result2['headline']}")
    print(f"Byline: {result2['byline']}")
    
    # Save examples to file
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    
    with open(examples_dir / "byline_example1.json", "w") as f:
        json.dump(result1, f, indent=2)
    
    with open(examples_dir / "byline_example2.json", "w") as f:
        json.dump(result2, f, indent=2)
    
    print(f"\nExample files saved to {examples_dir}/")
    return True

if __name__ == "__main__":
    # Make sure we can import from the current directory
    sys.path.insert(0, os.path.abspath("."))
    
    # Choose the test to run
    if len(sys.argv) > 1 and sys.argv[1] == "format":
        test_formatter_byline()
    else:
        # Set up directories
        if not setup_directories():
            print("Failed to set up directories!")
            sys.exit(1)
        
        # Run the pipeline
        success = run_pipeline()
        
        # Exit with appropriate code
        sys.exit(0 if success else 1) 