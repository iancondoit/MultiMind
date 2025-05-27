#!/usr/bin/env python3
"""
HSA Formatter Example

This script demonstrates how to use the HSAFormatter to process articles into
HSA-ready format, both individually and in batch mode.
"""

import sys
import os
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.formatter.hsa_formatter import HSAFormatter


def create_sample_article(index=1):
    """Create a sample article for demonstration."""
    return {
        "headline": f"Sample Article {index}",
        "body": f"This is the content of sample article {index}. It demonstrates the HSA formatting capabilities.",
        "raw_text": "This field should be removed in the final output",
        "section": "news",
        "tags": ["sample", "demonstration", f"article-{index}"],
        "date": "2023-08-15",
        "publication": "The Daily Example",
        "source_issue": "daily-example-2023-08-15",
        "source_url": "https://example.com/issues/2023-08-15",
        "byline": "By Example Author",
        "dateline": "SAMPLE CITY, AUGUST 15",
        "extra_field": "This field should be excluded from the HSA output"
    }


def demonstrate_single_article():
    """Demonstrate processing a single article."""
    print("\n=== Processing a Single Article ===\n")
    
    # Create formatter with a custom output directory
    output_dir = Path("examples/output/hsa-ready")
    formatter = HSAFormatter(output_dir=output_dir)
    
    # Create a sample article
    article = create_sample_article()
    
    # Format and display the article
    print("Original article:")
    print(json.dumps(article, indent=2))
    
    formatted = formatter.format_article(article)
    print("\nFormatted article:")
    print(json.dumps(formatted, indent=2))
    
    # Save the article
    saved_path = formatter.save_article(article)
    if saved_path:
        print(f"\nArticle saved to: {saved_path}")
    else:
        print("\nFailed to save article")


def demonstrate_batch_processing():
    """Demonstrate batch processing of articles."""
    print("\n=== Processing a Batch of Articles ===\n")
    
    # Create formatter with a custom output directory
    output_dir = Path("examples/output/hsa-ready")
    formatter = HSAFormatter(output_dir=output_dir)
    
    # Create a batch of sample articles
    articles = [create_sample_article(i) for i in range(1, 6)]
    
    print(f"Processing {len(articles)} articles...")
    
    # Process the batch
    results = formatter.process_batch(articles)
    
    print(f"\nSuccessfully processed {len(results)} of {len(articles)} articles")
    for path in results:
        print(f" - {path}")


def demonstrate_invalid_article():
    """Demonstrate handling of invalid articles."""
    print("\n=== Handling Invalid Articles ===\n")
    
    # Create formatter
    formatter = HSAFormatter()
    
    # Create an invalid article (missing required fields)
    invalid_article = {
        "headline": "Invalid Article",
        # Missing body
        "section": "invalid-section",  # Invalid section
        # Missing tags, timestamp, etc.
    }
    
    print("Invalid article:")
    print(json.dumps(invalid_article, indent=2))
    
    # Validate the article
    valid, errors = formatter.validate_article(invalid_article)
    
    print(f"\nValidation result: {'Valid' if valid else 'Invalid'}")
    if not valid:
        print("Validation errors:")
        for error in errors:
            print(f" - {error}")
    
    # Try to save the invalid article
    result = formatter.save_article(invalid_article)
    print(f"\nSave result: {'Succeeded' if result else 'Failed'}")


def main():
    """Main function to run the example."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="HSA Formatter example script")
    parser.add_argument("--example", choices=["single", "batch", "invalid", "all"], 
                        default="all", help="Example to run")
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path("examples/output/hsa-ready")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Run the requested example(s)
    if args.example in ["single", "all"]:
        demonstrate_single_article()
    
    if args.example in ["batch", "all"]:
        demonstrate_batch_processing()
    
    if args.example in ["invalid", "all"]:
        demonstrate_invalid_article()
    
    print("\nExample completed. Check the output directory for results.")


if __name__ == "__main__":
    main() 