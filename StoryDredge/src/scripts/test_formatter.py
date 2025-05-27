#!/usr/bin/env python3
"""
Test HSA Formatter

This script tests the HSA formatter with a sample article to ensure proper functionality.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Ensure we can import from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.formatter.hsa_formatter import HSAFormatter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_formatter")

def create_sample_article(article_id: int = 1) -> dict:
    """Create a sample article for testing."""
    sample_articles = [
        {
            "title": "AND SAVE MONEY",
            "raw_text": "AND SAVE MONEY. \nSANTA CLAUS left another carload of oil \nstocks in your chimney...",
            "category": "news",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
            "publication": "Atlanta Constitution"
        },
        {
            "title": "BY JOHN SMITH",
            "raw_text": "MAJOR DEVELOPMENT IN CITY. The mayor announced yesterday that a new building will be constructed downtown.",
            "category": "news",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
            "publication": "Atlanta Constitution"
        },
        {
            "raw_text": "Article with minimal fields that should be populated with defaults by the formatter.",
            "source_issue": "per_atlanta-constitution_1922-01-01_54_203"
        }
    ]
    
    if article_id < 1 or article_id > len(sample_articles):
        article_id = 1
    
    return sample_articles[article_id - 1]

def main():
    """Run the formatter test."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the HSA formatter with sample articles")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--sample", type=int, default=0, help="Sample article ID (1, 2, or 3), 0 for all")
    parser.add_argument("--strict", action="store_true", help="Use strict validation")
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Create test output directory
    test_output_dir = output_dir / "formatter_test"
    test_output_dir.mkdir(exist_ok=True, parents=True)
    
    # Create formatter
    formatter = HSAFormatter(output_dir=test_output_dir)
    formatter.strict_validation = args.strict
    formatter.add_default_values = not args.strict
    
    logger.info(f"Testing formatter with strict_validation={formatter.strict_validation}, add_default_values={formatter.add_default_values}")
    
    # Process sample articles
    if args.sample > 0:
        # Process only the specified sample
        logger.info(f"Processing sample article {args.sample}")
        article = create_sample_article(args.sample)
        
        # Format and save the article
        logger.info("Input article:")
        logger.info(json.dumps(article, indent=2))
        
        formatted = formatter.format_article(article)
        logger.info("Formatted article:")
        logger.info(json.dumps(formatted, indent=2))
        
        # Validate the formatted article
        valid, errors = formatter.validate_article(formatted)
        if valid:
            logger.info("✓ Article validation successful")
        else:
            logger.warning(f"✗ Article validation failed: {errors}")
        
        # Save the article
        output_path = formatter.save_article(article)
        if output_path:
            logger.info(f"✓ Article saved to {output_path}")
        else:
            logger.error("✗ Failed to save article")
    else:
        # Process all sample articles
        logger.info("Processing all sample articles")
        
        for i in range(1, 4):
            logger.info(f"\n--- Sample Article {i} ---")
            article = create_sample_article(i)
            
            # Format and save the article
            formatted = formatter.format_article(article)
            
            # Print summary of the formatted article
            logger.info(f"Title: {formatted.get('headline', 'N/A')}")
            logger.info(f"Section: {formatted.get('section', 'N/A')}")
            logger.info(f"Byline: {formatted.get('byline', 'N/A')}")
            logger.info(f"Tags: {formatted.get('tags', [])}")
            
            # Save the article
            output_path = formatter.save_article(article)
            if output_path:
                logger.info(f"✓ Article saved to {output_path}")
            else:
                logger.error("✗ Failed to save article")
    
    # Print output directory
    logger.info(f"\nTest output directory: {test_output_dir}")
    
    # List all output files
    output_files = list(test_output_dir.glob("**/*.json"))
    if output_files:
        logger.info(f"Generated {len(output_files)} output files:")
        for file in output_files:
            logger.info(f"  - {file.relative_to(test_output_dir)}")
    else:
        logger.warning("No output files were generated")

if __name__ == "__main__":
    main() 