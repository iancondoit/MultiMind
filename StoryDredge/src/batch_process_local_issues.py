#!/usr/bin/env python3
"""
Batch process all downloaded issues in the temp_downloads directory
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import argparse
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("batch_processor")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Process multiple newspaper issues in batch")
    parser.add_argument("--issues-file", type=str, default="data/batch_issues.json",
                       help="JSON file containing issue IDs to process")
    parser.add_argument("--output", type=str, default="output/atlanta-constitution",
                       help="Output directory for processed issues")
    parser.add_argument("--ocr-dir", type=str, default="temp_downloads",
                       help="Directory containing OCR text files")
    return parser.parse_args()

def load_issues(issues_file):
    """Load issue IDs from a JSON file"""
    try:
        with open(issues_file, 'r') as f:
            data = json.load(f)
            return data.get('issues', [])
    except Exception as e:
        logger.error(f"Error loading issues file: {e}")
        return []

def process_issue(issue_id, ocr_dir, output_dir):
    """Process a single issue using process_local_issue.py"""
    ocr_file = os.path.join(ocr_dir, f"{issue_id}.txt")
    
    if not os.path.exists(ocr_file):
        logger.warning(f"OCR file not found for issue {issue_id}: {ocr_file}")
        return False
    
    logger.info(f"Processing issue: {issue_id}")
    
    try:
        cmd = [
            sys.executable,  # Use the current Python interpreter
            "scripts/process_local_issue.py",
            "--issue", issue_id,
            "--ocr-file", ocr_file,
            "--output", output_dir
        ]
        
        # Use Popen instead of run to have more control over the process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Get output while process is running
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info(f"Successfully processed issue {issue_id}")
            return True
        else:
            logger.error(f"Error processing issue {issue_id}")
            logger.error(f"STDOUT: {stdout}")
            logger.error(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Unexpected error processing issue {issue_id}: {e}")
        return False

def main():
    args = parse_args()
    
    # Load issues from JSON file
    issues = load_issues(args.issues_file)
    
    if not issues:
        logger.error(f"No issues found in {args.issues_file}")
        return
    
    logger.info(f"Found {len(issues)} issues to process")
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Process each issue
    successful = 0
    failed = 0
    
    start_time = time.time()
    
    for i, issue_id in enumerate(issues, 1):
        logger.info(f"Processing issue {i}/{len(issues)}: {issue_id}")
        
        if process_issue(issue_id, args.ocr_dir, args.output):
            successful += 1
        else:
            failed += 1
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    logger.info("=" * 40)
    logger.info(f"Batch processing complete in {duration:.2f} seconds")
    logger.info(f"Successfully processed: {successful}/{len(issues)} issues")
    logger.info(f"Failed to process: {failed}/{len(issues)} issues")
    logger.info("=" * 40)
    
    if successful > 0:
        logger.info(f"Processed articles can be found in: {args.output}")

if __name__ == "__main__":
    main() 