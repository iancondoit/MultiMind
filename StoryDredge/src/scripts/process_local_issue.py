#!/usr/bin/env python3
"""
Process Local Newspaper Issue

This script processes a newspaper issue from a local OCR file using the universal pipeline.
It skips the fetching step and uses a local file instead.

Usage:
    python scripts/process_local_issue.py --issue ISSUE_ID --ocr-file PATH [--output OUTPUT_DIR]

Example:
    python scripts/process_local_issue.py --issue per_atlanta-constitution_1922-01-06_54_208 \
        --ocr-file temp_downloads/per_atlanta-constitution_1922-01-06_54_208.txt
"""

import os
import sys
import json
import logging
import argparse
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.config import get_config_manager
from src.cleaner.ocr_cleaner import OCRCleaner
from src.splitter.article_splitter import ArticleSplitter
from src.classifier.article_classifier import ArticleClassifier
from src.utils.progress import ProgressReporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path("logs") / f"local_process_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("local_processor")

# Default output directory
DEFAULT_OUTPUT_DIR = Path("output/hsa-ready-final")

# Publication name cleaning regex
PUBLICATION_CLEAN_REGEX = re.compile(r'[^\w\s-]')


def clean_publication_name(publication: str) -> str:
    """
    Convert publication name to a clean format for directory names.
    
    Args:
        publication: Raw publication name
        
    Returns:
        Cleaned publication name
    """
    # Replace spaces with hyphens and remove special characters
    clean_name = PUBLICATION_CLEAN_REGEX.sub('', publication)
    clean_name = re.sub(r'\s+', '-', clean_name)
    return clean_name.lower().strip()


def parse_issue_id(issue_id: str) -> Tuple[str, str, str, str]:
    """
    Parse the issue_id to extract publication and date info.
    
    Args:
        issue_id: Archive.org identifier (e.g., per_atlanta-constitution_1922-01-01_54_203)
        
    Returns:
        Tuple of (publication, year, month, day)
    """
    # Default values
    publication = "unknown"
    year, month, day = "", "", ""
    
    # Try to extract information from issue_id
    pattern = re.compile(r'^(?:pub_|per_)?([a-zA-Z0-9-]+)_(\d{4})-(\d{2})-(\d{2})')
    match = pattern.search(issue_id)
    
    if match:
        publication, year, month, day = match.groups()
        # Clean the publication name for directory structure
        publication = clean_publication_name(publication)
    else:
        # Alternative pattern for other formats
        parts = issue_id.split("_")
        if len(parts) >= 3:
            # Extract publication
            publication = clean_publication_name(parts[1])
            
            # Look for date pattern in remaining parts
            for part in parts[2:]:
                date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', part)
                if date_match:
                    year, month, day = date_match.groups()
                    break
    
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


def generate_article_filename(article: Dict[str, Any], year: str, month: str, day: str) -> str:
    """
    Generate a filename for the article based on its headline.
    
    Args:
        article: The article data
        year: Year
        month: Month
        day: Day
        
    Returns:
        Filename for the article
    """
    headline = article.get("headline", "untitled")
    
    # Create a slug from the headline
    slug = headline.lower()
    # Clean the slug to be filename-friendly
    slug = re.sub(r'[^a-z0-9]', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    
    # Make sure slug isn't too long
    if len(slug) > 50:
        slug = slug[:50]
    
    # Generate a unique filename with date prefix
    return f"{year}-{month}-{day}--{slug}.json"


def process_local_issue(issue_id: str, ocr_file: Path, output_dir: Path) -> bool:
    """
    Process a local newspaper issue through the pipeline.
    
    Args:
        issue_id: The archive.org identifier for the newspaper issue
        ocr_file: Path to the local OCR file
        output_dir: Base output directory
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        logger.info(f"Processing issue: {issue_id} from local file {ocr_file}")
        
        # Check if the OCR file exists
        if not ocr_file.exists():
            logger.error(f"OCR file not found: {ocr_file}")
            return False
        
        # Parse issue_id to extract publication and date info
        publication, year, month, day = parse_issue_id(issue_id)
        
        if not publication or not year or not month or not day:
            logger.error(f"Could not extract publication or date info from issue ID: {issue_id}")
            return False
        
        # Create output directory
        issue_dir = create_output_directory(output_dir, publication, year, month, day)
        
        # Initialize pipeline components
        cleaner = OCRCleaner()
        splitter = ArticleSplitter()
        classifier = ArticleClassifier()
        
        # STEP 1: Read the local OCR file
        logger.info(f"Reading OCR from {ocr_file}")
        with open(ocr_file, 'r', encoding='utf-8', errors='replace') as f:
            raw_ocr = f.read()
        
        # STEP 2: Clean OCR text
        logger.info("Cleaning OCR text")
        cleaned_text = cleaner.clean_text(raw_ocr)
        
        # STEP 3: Split into articles
        logger.info("Detecting headlines")
        headlines = splitter.detect_headlines(cleaned_text)
        
        logger.info(f"Detected {len(headlines)} headlines")
        
        logger.info("Extracting articles")
        articles = splitter.extract_articles(cleaned_text, headlines)
        
        if not articles:
            logger.warning(f"No articles extracted from issue {issue_id}")
            return False
            
        logger.info(f"Extracted {len(articles)} articles")
        
        # STEP 4: Classify articles and format for HSA
        logger.info(f"Classifying and formatting {len(articles)} articles")
        
        # Process each article
        for i, article in enumerate(articles):
            # Simple progress display
            if (i + 1) % 10 == 0 or i == 0 or i == len(articles) - 1:
                progress_pct = (i + 1) / len(articles) * 100
                logger.info(f"Processing article {i+1}/{len(articles)} ({progress_pct:.1f}%)")
            
            # Classify the article
            classified_article = classifier.classify_article(article)
            
            # Format for HSA
            hsa_article = {
                "headline": classified_article.get("title", "Untitled Article"),
                "body": classified_article.get("raw_text", "").strip(),
                "section": classified_article.get("category", "news").lower(),
                "tags": [],
                "timestamp": f"{year}-{month}-{day}T00:00:00.000Z",
                "publication": publication.replace("-", " ").title(),
                "source_issue": issue_id,
                "source_url": f"https://archive.org/details/{issue_id}"
            }
            
            # Extract tags from metadata if available
            if "metadata" in classified_article:
                metadata = classified_article["metadata"]
                tags = []
                
                # Add category as a tag
                category = classified_article.get("category", "")
                if category and category not in tags:
                    tags.append(category)
                
                # Add entities as tags
                for entity_type in ["people", "organizations", "locations", "tags"]:
                    if entity_type in metadata and metadata[entity_type]:
                        for entity in metadata[entity_type]:
                            if entity and entity not in tags:
                                tags.append(entity)
                
                hsa_article["tags"] = tags
            
            # Generate filename and save
            filename = generate_article_filename(hsa_article, year, month, day)
            file_path = issue_dir / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(hsa_article, f, indent=2)
        
        logger.info(f"Successfully processed issue {issue_id} - saved {len(articles)} articles to {issue_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing issue {issue_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Process a local newspaper issue")
    parser.add_argument("--issue", required=True, help="Issue ID to process")
    parser.add_argument("--ocr-file", required=True, help="Path to the local OCR file")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    
    args = parser.parse_args()
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Set up output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Ensure config is loaded
    config_manager = get_config_manager()
    config_manager.load()
    
    # Process the local issue
    ocr_file = Path(args.ocr_file)
    success = process_local_issue(args.issue, ocr_file, output_dir)
    
    # Write results to a report file
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    report_path = report_dir / f"local_process_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "issue_id": args.issue,
            "ocr_file": str(ocr_file),
            "output_dir": str(output_dir),
            "success": success,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    logger.info(f"Results saved to {report_path}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 