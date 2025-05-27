#!/usr/bin/env python3
"""
Verify Pipeline

This script verifies that the entire pipeline works correctly after code cleanup.
It processes a sample issue and checks the output for correctness.
"""

import os
import sys
import json
import logging
import argparse
import time
import shutil
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.process_local_issue import process_local_issue
from src.utils.config import get_config_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path("logs") / f"verify_pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("verify_pipeline")

# Default parameters
DEFAULT_SAMPLE_ISSUE = "per_atlanta-constitution_1922-01-09_54_211"
DEFAULT_OUTPUT_DIR = Path("output/verify_pipeline_test")


def find_sample_ocr_file(issue_id: str) -> Path:
    """
    Find a sample OCR file for testing.
    
    Args:
        issue_id: Issue ID to look for
        
    Returns:
        Path to the OCR file
    """
    # Check common locations for OCR files
    locations = [
        Path("temp_downloads"),
        Path("data/ocr"),
        Path("tests/fixtures")
    ]
    
    for location in locations:
        file_path = location / f"{issue_id}.txt"
        if file_path.exists():
            logger.info(f"Found sample OCR file: {file_path}")
            return file_path
    
    # If no file is found, raise an error
    raise FileNotFoundError(f"Could not find OCR file for issue {issue_id} in any of the standard locations.")


def verify_output_structure(output_dir: Path, issue_id: str) -> bool:
    """
    Verify that the output directory structure is correct.
    
    Args:
        output_dir: Base output directory
        issue_id: Issue ID used for processing
        
    Returns:
        True if structure is valid, False otherwise
    """
    # Parse the issue ID to get publication and date
    parts = issue_id.split("_")
    if len(parts) < 3:
        logger.error(f"Invalid issue ID format: {issue_id}")
        return False
    
    # Extract publication and date
    publication = parts[1]
    date_parts = parts[2].split("-")
    if len(date_parts) != 3:
        logger.error(f"Invalid date format in issue ID: {issue_id}")
        return False
    
    year, month, day = date_parts
    
    # Check output directory structure
    issue_dir = output_dir / publication / year / month / day
    if not issue_dir.exists() or not issue_dir.is_dir():
        logger.error(f"Expected output directory not found: {issue_dir}")
        return False
    
    # Count article files
    article_files = list(issue_dir.glob("*.json"))
    if not article_files:
        logger.error(f"No article files found in {issue_dir}")
        return False
    
    logger.info(f"Found {len(article_files)} article files in {issue_dir}")
    
    # Validate a sample of article files
    for article_file in article_files[:5]:  # Check first 5 articles
        if not verify_article_format(article_file):
            return False
    
    return True


def verify_article_format(article_file: Path) -> bool:
    """
    Verify that an article file has the correct format.
    
    Args:
        article_file: Path to the article JSON file
        
    Returns:
        True if format is valid, False otherwise
    """
    try:
        with open(article_file, 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        # Check required fields
        required_fields = ["headline", "body", "section", "timestamp", "publication", "source_issue"]
        for field in required_fields:
            if field not in article:
                logger.error(f"Missing required field '{field}' in {article_file}")
                return False
        
        # Check timestamp format
        timestamp = article["timestamp"]
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            logger.error(f"Invalid timestamp format in {article_file}: {timestamp}")
            return False
        
        logger.debug(f"Article format valid: {article_file}")
        return True
    
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in {article_file}")
        return False
    except Exception as e:
        logger.error(f"Error validating article {article_file}: {str(e)}")
        return False


def run_verification(issue_id: str, output_dir: Path, cleanup: bool = True) -> bool:
    """
    Run the verification process.
    
    Args:
        issue_id: Issue ID to process
        output_dir: Output directory
        cleanup: Whether to clean up the output directory after verification
        
    Returns:
        True if verification passed, False otherwise
    """
    try:
        logger.info(f"Starting verification with issue: {issue_id}")
        
        # Find sample OCR file
        ocr_file = find_sample_ocr_file(issue_id)
        
        # Create clean output directory
        if output_dir.exists() and cleanup:
            logger.info(f"Cleaning up existing output directory: {output_dir}")
            shutil.rmtree(output_dir)
        
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Process the issue
        logger.info(f"Processing issue {issue_id} with OCR file {ocr_file}")
        start_time = time.time()
        success = process_local_issue(issue_id, ocr_file, output_dir)
        processing_time = time.time() - start_time
        
        if not success:
            logger.error(f"Failed to process issue {issue_id}")
            return False
        
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        # Verify output structure
        structure_valid = verify_output_structure(output_dir, issue_id)
        
        if structure_valid:
            logger.info("Output structure verification passed")
        else:
            logger.error("Output structure verification failed")
            return False
        
        logger.info("All verification checks passed successfully!")
        return True
    
    except Exception as e:
        logger.error(f"Verification failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up if requested
        if cleanup and output_dir.exists():
            logger.info(f"Cleaning up output directory: {output_dir}")
            shutil.rmtree(output_dir)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Verify pipeline functionality")
    parser.add_argument("--issue", default=DEFAULT_SAMPLE_ISSUE, help="Issue ID to use for verification")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for verification")
    parser.add_argument("--keep-output", action="store_true", help="Keep output files after verification")
    
    args = parser.parse_args()
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Load configuration
    config_manager = get_config_manager()
    config_manager.load()
    
    # Run verification
    output_dir = Path(args.output_dir)
    success = run_verification(args.issue, output_dir, cleanup=not args.keep_output)
    
    if success:
        logger.info("Pipeline verification completed successfully!")
        sys.exit(0)
    else:
        logger.error("Pipeline verification failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 