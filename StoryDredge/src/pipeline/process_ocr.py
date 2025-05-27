#!/usr/bin/env python3
"""
process_ocr.py - Process OCR text through the pipeline

This module provides functionality for processing OCR text through
the pipeline components, with an option to skip the fetch step.
This is useful when the OCR text is already available locally.
"""

import os
import sys
import argparse
import logging
import re
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

# Ensure we can import from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cleaner.ocr_cleaner import OCRCleaner
from src.splitter.article_splitter import ArticleSplitter
from src.classifier.article_classifier import ArticleClassifier
from src.formatter.hsa_formatter import HSAFormatter
from src.utils.progress import ProgressReporter
from src.utils.config import get_config_manager
from src.utils.archive import fetch_ocr_for_issue
from src.extractor.article_extractor import ArticleExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("process_ocr")

# Try to import our simplified progress reporter
try:
    from src.utils.simplified_progress import ProgressReporter
except ImportError:
    try:
        from src.utils.progress import ProgressReporter
    except ImportError:
        # Simple dummy progress reporter
        class ProgressReporter:
            def __init__(self, *args, **kwargs): pass
            def update(self, *args, **kwargs): pass
            def complete(self): pass
            def __enter__(self): return self
            def __exit__(self, *args, **kwargs): pass


def process_ocr(
    issue_id: str,
    output_dir: str = "output",
    skip_fetch: bool = False,
    skip_extraction: bool = False,
    skip_classification: bool = False,
    skip_formatting: bool = False,
    fast_mode: bool = False
) -> bool:
    """
    Process OCR data for a newspaper issue.
    
    Args:
        issue_id: Archive.org identifier for the issue
        output_dir: Directory to store output files
        skip_fetch: Skip fetching OCR data from archive.org
        skip_extraction: Skip article extraction
        skip_classification: Skip article classification
        skip_formatting: Skip HSA formatting
        fast_mode: Use fast rule-based classification instead of LLM
        
    Returns:
        True if processing was successful, False otherwise
    """
    logger.info(f"Processing OCR data for issue: {issue_id}")
    start_time = time.time()
    
    # Setup paths
    base_output_dir = Path(output_dir)
    
    # Create a temporary directory for the intermediate files
    temp_dir = base_output_dir / "temp" / issue_id
    temp_dir.mkdir(exist_ok=True, parents=True)
    
    articles_dir = temp_dir / "articles"
    articles_dir.mkdir(exist_ok=True)
    
    classified_dir = temp_dir / "classified"
    classified_dir.mkdir(exist_ok=True)
    
    # Step 1: Fetch OCR data
    raw_text_path = temp_dir / "raw.txt"
    
    if not skip_fetch and not raw_text_path.exists():
        logger.info(f"Fetching OCR data for issue: {issue_id}")
        try:
            fetch_ocr_for_issue(issue_id, raw_text_path)
            logger.info(f"OCR data fetched and saved to: {raw_text_path}")
        except Exception as e:
            logger.error(f"Failed to fetch OCR data: {e}")
            return False
    elif raw_text_path.exists():
        logger.info(f"Using existing OCR data from: {raw_text_path}")
    else:
        logger.error(f"OCR data not found at: {raw_text_path}")
        return False
    
    # Step 2: Extract articles
    if not skip_extraction:
        logger.info("Extracting articles from OCR text")
        try:
            # Initialize article extractor
            extractor = ArticleExtractor()
            
            # Read OCR text
            with open(raw_text_path, 'r', encoding='utf-8') as f:
                raw_text = f.read()
            
            # Extract articles
            articles = extractor.extract_articles(raw_text)
            
            # Add metadata to articles
            for i, article in enumerate(articles):
                article["source_issue"] = issue_id
                article["_file_name"] = f"article_{i:04d}.json"
            
            # Save extracted articles
            logger.info(f"Saving {len(articles)} extracted articles")
            for article in articles:
                article_path = articles_dir / article["_file_name"]
                extractor.save_article(article, article_path)
                
            logger.info(f"Article extraction completed. Found {len(articles)} articles")
            
        except Exception as e:
            logger.error(f"Failed to extract articles: {e}")
            return False
    else:
        logger.info("Skipping article extraction")
    
    # Step 3: Classify articles
    if not skip_classification:
        logger.info("Classifying articles")
        try:
            # Initialize classifier with appropriate settings
            if fast_mode:
                classifier = ArticleClassifier(skip_classification=True)
                logger.info("Using fast rule-based classification (skipping LLM)")
            else:
                classifier = ArticleClassifier() 
                logger.info("Using hybrid classification approach with caching")
            
            # Classify all articles in the articles directory
            results = classifier.classify_directory(
                input_dir=articles_dir,
                output_dir=classified_dir
            )
            
            logger.info(f"Classification completed. Processed {len(results)} articles")
            
        except Exception as e:
            logger.error(f"Failed to classify articles: {e}")
            return False
    else:
        logger.info("Skipping article classification")
    
    # Step 4: Format articles for HSA
    if not skip_formatting:
        logger.info("Formatting articles for HSA")
        try:
            # Initialize formatter with the proper output directory
            formatter = HSAFormatter(output_dir=base_output_dir)
            
            # Format all classified articles
            results = formatter.format_issue(issue_id, classified_dir)
            
            logger.info(f"Formatting completed. Processed {len(results)} articles")
            
        except Exception as e:
            logger.error(f"Failed to format articles: {e}")
            return False
    else:
        logger.info("Skipping HSA formatting")
    
    # Done
    elapsed_time = time.time() - start_time
    logger.info(f"Processing completed in {elapsed_time:.2f} seconds")
    
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Process OCR data for a newspaper issue")
    parser.add_argument("--issue", required=True, help="Archive.org identifier for the issue")
    parser.add_argument("--output-dir", default="output", help="Directory to store output files")
    parser.add_argument("--skip-fetch", action="store_true", help="Skip fetching OCR data")
    parser.add_argument("--skip-extraction", action="store_true", help="Skip article extraction")
    parser.add_argument("--skip-classification", action="store_true", help="Skip article classification")
    parser.add_argument("--skip-formatting", action="store_true", help="Skip HSA formatting")
    parser.add_argument("--fast-mode", action="store_true", help="Use fast rule-based classification only")
    
    args = parser.parse_args()
    
    success = process_ocr(
        issue_id=args.issue,
        output_dir=args.output_dir,
        skip_fetch=args.skip_fetch,
        skip_extraction=args.skip_extraction,
        skip_classification=args.skip_classification,
        skip_formatting=args.skip_formatting,
        fast_mode=args.fast_mode
    )
    
    if not success:
        logger.error("Processing failed")
        sys.exit(1)
    
    logger.info("Processing completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main() 