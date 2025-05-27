#!/usr/bin/env python3
"""
Universal Newspaper Processing Pipeline

This script provides a unified pipeline for processing newspaper issues from archive.org:
1. Fetch OCR text from archive.org
2. Clean and normalize the OCR text
3. Split the text into articles
4. Classify the articles
5. Format and save in the HSA-ready format

The pipeline creates a clean directory structure in the format:
output/hsa-ready-final/publication/year/month/day/

This script can process:
- A single issue with --issue
- Multiple issues from a file with --issues-file
- Supports various publications, not just Atlanta Constitution

Usage:
    python scripts/universal_newspaper_pipeline.py --issue ISSUE_ID [--output OUTPUT_DIR]
    python scripts/universal_newspaper_pipeline.py --issues-file ISSUES_FILE [--output OUTPUT_DIR]

Example:
    python scripts/universal_newspaper_pipeline.py --issue per_atlanta-constitution_1922-01-01_54_203
    python scripts/universal_newspaper_pipeline.py --issues-file data/issue_list.txt --output output/hsa-ready-final
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
from src.fetcher.archive_fetcher import ArchiveFetcher
from src.cleaner.ocr_cleaner import OCRCleaner
from src.splitter.article_splitter import ArticleSplitter
from src.classifier.article_classifier import ArticleClassifier
from src.formatter.hsa_formatter import HSAFormatter
from src.utils.progress import ProgressReporter
from src.utils.errors import StoryDredgeError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path("logs") / f"universal_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("universal_pipeline")

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


def process_issue(issue_id: str, output_dir: Path) -> bool:
    """
    Process a single newspaper issue through the entire pipeline.
    
    Args:
        issue_id: The archive.org identifier for the newspaper issue
        output_dir: Base output directory
        
    Returns:
        True if processing was successful, False otherwise
    """
    try:
        logger.info(f"Processing issue: {issue_id}")
        
        # Parse issue_id to extract publication and date info
        publication, year, month, day = parse_issue_id(issue_id)
        
        if not publication or not year or not month or not day:
            logger.error(f"Could not extract publication or date info from issue ID: {issue_id}")
            return False
        
        # Create output directory
        issue_dir = create_output_directory(output_dir, publication, year, month, day)
        
        # Initialize pipeline components
        fetcher = ArchiveFetcher()
        cleaner = OCRCleaner()
        splitter = ArticleSplitter()
        classifier = ArticleClassifier()
        
        # STEP 1: Fetch OCR from archive.org
        logger.info(f"Fetching OCR for issue {issue_id}")
        raw_ocr = fetcher.fetch_issue(issue_id)
        
        if not raw_ocr:
            logger.error(f"Failed to fetch OCR for issue {issue_id}")
            return False
        
        # STEP 2: Clean OCR text
        logger.info("Cleaning OCR text")
        cleaned_text = cleaner.clean_text(raw_ocr)
        
        # STEP 3: Split into articles
        logger.info("Splitting text into articles")
        articles = splitter.split_articles(cleaned_text)
        
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


def process_issues_from_file(issues_file: str, output_dir: Path) -> Dict[str, Any]:
    """
    Process multiple newspaper issues from a file.
    
    Args:
        issues_file: Path to a file containing issue IDs (one per line)
        output_dir: Base output directory
        
    Returns:
        Dictionary with processing results
    """
    logger.info(f"Processing issues from file: {issues_file}")
    
    # Read issues from file
    issues_path = Path(issues_file)
    
    if not issues_path.exists():
        logger.error(f"Issues file not found: {issues_file}")
        return {"successful": [], "failed": []}
    
    with open(issues_path, 'r', encoding='utf-8') as f:
        issues = [line.strip() for line in f if line.strip()]
    
    logger.info(f"Found {len(issues)} issues to process")
    
    # Track results
    results = {
        "successful": [],
        "failed": [],
        "total": len(issues),
        "start_time": time.time()
    }
    
    # Set up progress tracking
    progress = ProgressReporter(total=len(issues), desc="Processing Issues")
    
    # Process each issue
    for i, issue_id in enumerate(issues):
        logger.info(f"Processing issue {i+1}/{len(issues)}: {issue_id}")
        
        if process_issue(issue_id, output_dir):
            results["successful"].append(issue_id)
        else:
            results["failed"].append(issue_id)
        
        # Update progress
        progress.update(i + 1)
    
    # Calculate processing time
    elapsed_time = time.time() - results["start_time"]
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    logger.info(f"Processing complete:")
    logger.info(f"  Total issues: {results['total']}")
    logger.info(f"  Successful: {len(results['successful'])}")
    logger.info(f"  Failed: {len(results['failed'])}")
    logger.info(f"  Processing time: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    return results


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Universal newspaper processing pipeline")
    parser.add_argument("--issue", help="Issue ID to process")
    parser.add_argument("--issues-file", help="File containing list of issues to process (one per line)")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    
    args = parser.parse_args()
    
    if not args.issue and not args.issues_file:
        parser.error("Either --issue or --issues-file must be specified")
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Set up output directory
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Ensure config is loaded
    config_manager = get_config_manager()
    config_manager.load()
    
    # Process based on input type
    if args.issue:
        # Process a single issue
        success = process_issue(args.issue, output_dir)
        sys.exit(0 if success else 1)
    
    elif args.issues_file:
        # Process multiple issues from a file
        results = process_issues_from_file(args.issues_file, output_dir)
        
        # Write results to a report file
        report_dir = Path("reports")
        report_dir.mkdir(exist_ok=True)
        
        report_path = report_dir / f"pipeline_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to {report_path}")
        
        # Exit with success only if all issues were processed successfully
        success = len(results["failed"]) == 0
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 