#!/usr/bin/env python3
"""
Complete Atlanta Constitution Processing Pipeline

This script combines all the steps required to process Atlanta Constitution issues:
1. Extract articles from OCR text
2. Classify articles
3. Convert to HSA-ready format

Usage:
    python scripts/process_constitution_pipeline.py [--issues ISSUES_FILE] [--output OUTPUT_DIR] [--issue ISSUE_ID]

Example:
    python scripts/process_constitution_pipeline.py --issue per_atlanta-constitution_1922-01-01_54_203
    python scripts/process_constitution_pipeline.py --issues data/issue_list.txt --output output/hsa-ready-final
"""

import os
import sys
import json
import logging
import argparse
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import get_config_manager
from src.splitter.article_splitter import ArticleSplitter
from src.classifier.article_classifier import ArticleClassifier
from src.utils.ocr_cleaner import OCRCleaner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("constitution_pipeline")

# Constants
DEFAULT_OUTPUT_DIR = Path("output/hsa-ready-final")
TEMP_DOWNLOADS_DIR = Path("temp_downloads")
TEST_ISSUES = [
    "per_atlanta-constitution_1922-01-01_54_203",
    "per_atlanta-constitution_1922-01-02_54_204"
]


def download_or_use_existing_ocr(issue_id: str, temp_dir: Path) -> Path:
    """
    Download the OCR file or use an existing one.
    
    Args:
        issue_id: The archive.org identifier
        temp_dir: Directory for downloads
        
    Returns:
        Path to the OCR file
    """
    ocr_file = temp_dir / f"{issue_id}.txt"
    
    if not ocr_file.exists():
        # In a real implementation, we would download from archive.org here
        logger.error(f"OCR file for {issue_id} not found in {temp_dir}")
        raise FileNotFoundError(f"OCR file {ocr_file} not found. Please download it first.")
    
    logger.info(f"Using existing OCR file for {issue_id}")
    return ocr_file


def parse_issue_id(issue_id: str) -> Tuple[str, str, str, str]:
    """
    Parse the issue_id to extract publication and date info.
    
    Args:
        issue_id: Archive.org identifier (e.g., per_atlanta-constitution_1922-01-01_54_203)
        
    Returns:
        Tuple of (publication, year, month, day)
    """
    parts = issue_id.split("_")
    
    # Default values
    publication = "atlanta-constitution"
    year, month, day = "", "", ""
    
    # Try to extract date from parts
    if len(parts) >= 3 and parts[1] and re.match(r'^\d{4}-\d{2}-\d{2}', parts[2]):
        date_parts = parts[2].split("-")
        if len(date_parts) >= 3:
            year, month, day = date_parts[0], date_parts[1], date_parts[2]
    
    return publication, year, month, day


def create_output_directory(output_dir: Path, publication: str, year: str, month: str, day: str) -> Path:
    """
    Create the output directory structure.
    
    Args:
        output_dir: Base output directory
        publication: Publication name
        year: Year
        month: Month
        day: Day
        
    Returns:
        Path to the issue directory
    """
    issue_dir = output_dir / publication / year / month / day
    issue_dir.mkdir(parents=True, exist_ok=True)
    return issue_dir


def process_ocr_file(ocr_file: Path, issue_id: str, output_dir: Path) -> bool:
    """
    Process the OCR file through the pipeline.
    
    Args:
        ocr_file: Path to the OCR file
        issue_id: The archive.org identifier
        output_dir: Base output directory
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        # Parse issue_id to create a cleaner directory structure
        publication, year, month, day = parse_issue_id(issue_id)
        
        # Create final output directory structure
        issue_dir = create_output_directory(output_dir, publication, year, month, day)
        
        # Save raw OCR to output directory
        with open(ocr_file, 'r', encoding='utf-8') as f:
            raw_text = f.read()
        
        # Clean OCR text
        logger.info("Cleaning OCR text")
        cleaner = OCRCleaner()
        cleaned_text = cleaner.clean(raw_text)
        
        # Split OCR into articles
        logger.info("Splitting OCR into articles")
        config_manager = get_config_manager()
        splitter = ArticleSplitter(config_manager)
        articles = splitter.extract_articles(cleaned_text)
        
        logger.info(f"Extracted {len(articles)} articles")
        
        # In-memory storage for articles rather than writing to intermediate files
        extracted_articles = []
        
        # Save articles
        for i, article in enumerate(articles, 1):
            article_data = {
                "headline": article.headline,
                "body": article.text
            }
            extracted_articles.append(article_data)
            
        # Classify articles
        logger.info("Classifying articles")
        classifier = ArticleClassifier(model_name="llama2")
        
        classified_articles = []
        
        # Process each article through classification
        for i, article in enumerate(extracted_articles, 1):
            # Classify the article
            classification = classifier.classify_article(article["headline"], article["body"])
            
            # Add classification data to the article
            article_with_classification = {
                **article,
                "section": classification["category"],
                "tags": classification["tags"],
                "timestamp": f"{year}-{month}-{day}T00:00:00.000Z",
                "publication": "Atlanta Constitution",
                "source_issue": issue_id,
                "source_url": f"https://archive.org/details/{issue_id}"
            }
            
            classified_articles.append(article_with_classification)
            
            if i % 5 == 0 or i == len(extracted_articles):
                logger.info(f"Classified {i}/{len(extracted_articles)} articles")
        
        # Convert to HSA format and save to final directory
        logger.info("Converting to HSA format and saving files")
        for i, article in enumerate(classified_articles, 1):
            # Generate a slug from the headline for the filename
            headline = article["headline"]
            slug = headline.lower()
            # Clean the slug to be filename-friendly
            slug = re.sub(r'[^a-z0-9]', '-', slug)
            slug = re.sub(r'-+', '-', slug).strip('-')
            # Make sure slug isn't too long
            if len(slug) > 50:
                slug = slug[:50]
                
            # Final HSA-ready filename
            filename = f"{year}-{month}-{day}--{slug}.json"
            file_path = issue_dir / filename
            
            # Write the article to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(article, f, indent=2)
            
            if i % 50 == 0 or i == len(classified_articles):
                logger.info(f"Processed {i}/{len(classified_articles)} articles to final format")
        
        logger.info(f"Successfully processed {issue_id} - created {len(classified_articles)} HSA-ready articles")
        return True
    
    except Exception as e:
        logger.error(f"Error processing {issue_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def process_issue(issue_id: str, output_dir: Path) -> bool:
    """
    Process a single newspaper issue.
    
    Args:
        issue_id: The archive.org identifier
        output_dir: Base output directory
        
    Returns:
        True if processing was successful, False otherwise
    """
    logger.info(f"Processing issue: {issue_id}")
    
    # Set up temporary directory for downloads
    temp_dir = TEMP_DOWNLOADS_DIR
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Get the OCR file
        ocr_file = download_or_use_existing_ocr(issue_id, temp_dir)
        
        # Process the OCR file
        result = process_ocr_file(ocr_file, issue_id, output_dir)
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing issue {issue_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def process_issues_from_file(issues_file: str, output_dir: Path) -> Dict[str, bool]:
    """
    Process multiple issues from a file.
    
    Args:
        issues_file: Path to the file containing issue IDs
        output_dir: Base output directory
        
    Returns:
        Dictionary of {issue_id: success}
    """
    results = {}
    
    with open(issues_file, 'r') as f:
        issues = [line.strip() for line in f if line.strip()]
    
    logger.info(f"Processing {len(issues)} issues from {issues_file}")
    
    for issue_id in issues:
        results[issue_id] = process_issue(issue_id, output_dir)
    
    return results


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Process Atlanta Constitution issues through the complete pipeline")
    parser.add_argument("--issues", help="Path to a file containing issue IDs to process")
    parser.add_argument("--issue", help="Single issue ID to process")
    parser.add_argument("--output", help="Output directory for HSA-ready data", default=str(DEFAULT_OUTPUT_DIR))
    
    args = parser.parse_args()
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Track results
    results = {
        "successful": [],
        "failed": []
    }
    
    # Determine which issues to process
    if args.issues:
        # Process issues from file
        process_results = process_issues_from_file(args.issues, output_dir)
        
        for issue_id, success in process_results.items():
            if success:
                results["successful"].append(issue_id)
            else:
                results["failed"].append(issue_id)
    
    elif args.issue:
        # Process a single issue
        success = process_issue(args.issue, output_dir)
        
        if success:
            results["successful"].append(args.issue)
        else:
            results["failed"].append(args.issue)
    
    else:
        # Use default test issues
        logger.info(f"No issue specified, using {len(TEST_ISSUES)} test issues")
        
        for issue_id in TEST_ISSUES:
            success = process_issue(issue_id, output_dir)
            
            if success:
                results["successful"].append(issue_id)
            else:
                results["failed"].append(issue_id)
    
    # Print summary
    logger.info("Pipeline completed:")
    logger.info(f"  Successful: {len(results['successful'])}")
    logger.info(f"  Failed: {len(results['failed'])}")
    
    if results["failed"]:
        logger.info("Failed issues:")
        for issue_id in results["failed"]:
            logger.info(f"  - {issue_id}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 