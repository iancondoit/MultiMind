#!/usr/bin/env python3
"""
Batch Process Local Issues

This script processes multiple local OCR files from a directory, automatically
matching them with their issue IDs based on the filenames.

Usage:
    python scripts/batch_process_local_issues.py [--source-dir DIR] [--output-dir DIR] [--issues-file FILE]

Example:
    python scripts/batch_process_local_issues.py --source-dir temp_downloads --output-dir output/hsa-ready-final
"""

import os
import sys
import json
import logging
import argparse
import re
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Set

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.process_local_issue import process_local_issue
from src.utils.config import get_config_manager
from src.utils.progress import ProgressReporter


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path("logs") / f"batch_process_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("batch_processor")

# Default directories
DEFAULT_SOURCE_DIR = Path("temp_downloads")
DEFAULT_OUTPUT_DIR = Path("output/hsa-ready-final")


def find_ocr_files(source_dir: Path) -> List[Tuple[str, Path]]:
    """
    Find OCR files in the source directory and extract their issue IDs.
    
    Args:
        source_dir: Directory containing OCR files
        
    Returns:
        List of tuples (issue_id, file_path)
    """
    logger.info(f"Searching for OCR files in {source_dir}")
    
    if not source_dir.exists() or not source_dir.is_dir():
        logger.error(f"Source directory not found: {source_dir}")
        return []
    
    ocr_files = []
    
    # Look for files with patterns like:
    # - per_atlanta-constitution_1922-01-01_54_203.txt
    # - pub_chicago-tribune_19220215.txt
    pattern = re.compile(r'^((?:per|pub)_[\w-]+_[\d-]+.*?)\.txt$')
    
    for file_path in source_dir.glob("*.txt"):
        match = pattern.match(file_path.name)
        if match:
            issue_id = match.group(1)
            ocr_files.append((issue_id, file_path))
            logger.debug(f"Found OCR file: {file_path} with issue ID: {issue_id}")
    
    logger.info(f"Found {len(ocr_files)} OCR files")
    return ocr_files


def filter_issues_by_file(ocr_files: List[Tuple[str, Path]], issues_file: Path) -> List[Tuple[str, Path]]:
    """
    Filter OCR files to only include those listed in the issues file.
    
    Args:
        ocr_files: List of tuples (issue_id, file_path)
        issues_file: Path to file containing issue IDs (one per line)
        
    Returns:
        Filtered list of tuples (issue_id, file_path)
    """
    logger.info(f"Filtering issues using file: {issues_file}")
    
    if not issues_file.exists():
        logger.error(f"Issues file not found: {issues_file}")
        return ocr_files
    
    with open(issues_file, 'r', encoding='utf-8') as f:
        requested_issues = set(line.strip() for line in f if line.strip())
    
    logger.info(f"Found {len(requested_issues)} issues in the issues file")
    
    filtered_files = [(issue_id, file_path) for issue_id, file_path in ocr_files 
                     if issue_id in requested_issues]
    
    logger.info(f"Filtered to {len(filtered_files)} OCR files")
    return filtered_files


def batch_process(ocr_files: List[Tuple[str, Path]], output_dir: Path) -> Dict[str, Any]:
    """
    Process multiple OCR files.
    
    Args:
        ocr_files: List of tuples (issue_id, file_path)
        output_dir: Base output directory
        
    Returns:
        Dictionary with processing results
    """
    logger.info(f"Starting batch processing of {len(ocr_files)} OCR files")
    
    # Set up output directory
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Set up progress tracking
    progress = ProgressReporter("Processing Issues", len(ocr_files))
    
    # Track results
    results = {
        "successful": [],
        "failed": [],
        "total": len(ocr_files),
        "start_time": time.time()
    }
    
    # Process each OCR file
    for i, (issue_id, ocr_file) in enumerate(ocr_files):
        logger.info(f"Processing issue {i+1}/{len(ocr_files)}: {issue_id}")
        
        try:
            success = process_local_issue(issue_id, ocr_file, output_dir)
            
            if success:
                results["successful"].append(issue_id)
                logger.info(f"Successfully processed issue: {issue_id}")
            else:
                results["failed"].append(issue_id)
                logger.error(f"Failed to process issue: {issue_id}")
                
        except Exception as e:
            logger.error(f"Error processing issue {issue_id}: {str(e)}")
            results["failed"].append(issue_id)
        
        # Update progress
        progress.update(i + 1)
    
    # Calculate processing time
    elapsed_time = time.time() - results["start_time"]
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Log summary
    logger.info(f"Batch processing complete:")
    logger.info(f"  Total issues: {results['total']}")
    logger.info(f"  Successful: {len(results['successful'])}")
    logger.info(f"  Failed: {len(results['failed'])}")
    logger.info(f"  Processing time: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    # Add processing time to results
    results["processing_time"] = {
        "hours": int(hours),
        "minutes": int(minutes),
        "seconds": int(seconds),
        "total_seconds": elapsed_time
    }
    
    return results


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Batch process local newspaper OCR files")
    parser.add_argument("--source-dir", default=str(DEFAULT_SOURCE_DIR), help="Directory containing OCR files")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    parser.add_argument("--issues-file", help="Optional file containing issue IDs to process (one per line)")
    
    args = parser.parse_args()
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    # Ensure config is loaded
    config_manager = get_config_manager()
    config_manager.load()
    
    # Find OCR files
    source_dir = Path(args.source_dir)
    ocr_files = find_ocr_files(source_dir)
    
    if not ocr_files:
        logger.error(f"No OCR files found in {source_dir}")
        sys.exit(1)
    
    # Filter by issues file if provided
    if args.issues_file:
        issues_file = Path(args.issues_file)
        ocr_files = filter_issues_by_file(ocr_files, issues_file)
    
    # Process the OCR files
    output_dir = Path(args.output_dir)
    results = batch_process(ocr_files, output_dir)
    
    # Write results to a report file
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    report_path = report_dir / f"batch_process_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Results saved to {report_path}")
    
    # Exit with success only if all issues were processed successfully
    success = len(results["failed"]) == 0
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 