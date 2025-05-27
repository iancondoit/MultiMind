#!/usr/bin/env python3
"""
Rebuild HSA Output Script

This script processes all classified articles and regenerates the HSA-ready JSON output.
It's useful after making changes to the formatter to update all the output files.

Features:
- Processes all classified articles from the output directory
- Automatically extracts dates from archive.org identifiers
- Organizes output by date in YYYY/MM/DD directory structure
- Handles validation and error reporting
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import json
import re

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.formatter.hsa_formatter import HSAFormatter
from src.utils.date_utils import extract_date_from_archive_id, format_iso_date


def setup_logging():
    """Configure logging for the script."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "formatter.log"),
            logging.StreamHandler()
        ]
    )


def process_classified_directory(input_dir: Path, output_dir: Path):
    """
    Process all JSON files in the specified classified directory.
    
    Args:
        input_dir: Path to the directory with classified articles
        output_dir: Path to the output directory for HSA-ready JSON
    """
    logger = logging.getLogger(__name__)
    
    if not input_dir.exists():
        logger.error(f"Input directory {input_dir} does not exist.")
        return False
    
    logger.info(f"Processing classified articles from {input_dir}")
    formatter = HSAFormatter(output_dir=output_dir)
    
    # Count successful and failed conversions
    success_count = 0
    error_count = 0
    
    # Track distribution of articles by date
    date_counts = {}
    
    # Process each issue directory
    for issue_dir in input_dir.glob("per_*"):
        if not issue_dir.is_dir():
            continue
        
        classified_dir = issue_dir / "classified"
        if not classified_dir.exists() or not classified_dir.is_dir():
            logger.warning(f"No classified directory found for issue {issue_dir.name}")
            continue
        
        # Extract date from issue directory name
        issue_name = issue_dir.name
        logger.info(f"Processing articles for issue: {issue_name}")
        
        # Extract date from archive ID
        date_parts = extract_date_from_archive_id(issue_name)
        if date_parts:
            year, month, day = date_parts
            logger.info(f"Extracted date from archive ID: {year}-{month}-{day}")
            
            # Update date count
            date_key = f"{year}-{month}-{day}"
            if date_key not in date_counts:
                date_counts[date_key] = 0
        else:
            logger.warning(f"Could not extract date from issue name: {issue_name}")
        
        # Process all JSON files in the classified directory
        article_files = list(classified_dir.glob("*.json"))
        if not article_files:
            logger.warning(f"No articles found in {classified_dir}")
            continue
        
        logger.info(f"Found {len(article_files)} articles to process")
        
        # Process each article individually
        for article_file in article_files:
            try:
                # Read the article
                with open(article_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                
                # Add source information based on issue directory
                article["source_issue"] = issue_name
                
                # Save the article
                result = formatter.save_article(article)
                if result:
                    success_count += 1
                    logger.debug(f"Successfully processed {article_file.name}")
                    
                    # Update date count if we have date information
                    if date_parts:
                        date_counts[date_key] += 1
                else:
                    error_count += 1
                    logger.warning(f"Failed to process {article_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing file {article_file}: {e}")
                error_count += 1
        
    logger.info(f"Completed processing with {success_count} successful conversions and {error_count} errors")
    
    # Log date distribution
    if date_counts:
        logger.info("Distribution of articles by date:")
        for date, count in sorted(date_counts.items()):
            logger.info(f"  {date}: {count} articles")
    
    return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Rebuild HSA-ready output from classified articles")
    parser.add_argument("--input-dir", default="output", help="Base input directory containing issue folders")
    parser.add_argument("--output-dir", default="output/hsa-ready", help="Output directory for HSA-ready JSON")
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True, parents=True)
    
    logger.info(f"Starting rebuild of HSA-ready output")
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    success = process_classified_directory(input_dir, output_dir)
    
    if success:
        logger.info("Successfully rebuilt HSA-ready output")
    else:
        logger.error("Failed to rebuild HSA-ready output")
        sys.exit(1)


if __name__ == "__main__":
    main() 