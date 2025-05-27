#!/usr/bin/env python3
"""
Fetch and process 100 more Atlanta Constitution issues
This script combines the functionality of fetching, downloading, and processing in one workflow
"""

import os
import sys
import json
import requests
import time
import subprocess
import logging
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("atlanta_processor")

# Set up paths
TEMP_DOWNLOADS = Path("temp_downloads")
TEMP_DOWNLOADS.mkdir(exist_ok=True)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("output/atlanta-constitution")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Fetch and process 100 more Atlanta Constitution issues")
    parser.add_argument("--start-date", type=str, default="1925-01-01",
                       help="Start date for issue search (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="1930-12-31",
                       help="End date for issue search (YYYY-MM-DD)")
    parser.add_argument("--max-issues", type=int, default=100,
                       help="Maximum number of issues to process")
    parser.add_argument("--threads", type=int, default=4,
                       help="Number of threads for parallel downloads")
    return parser.parse_args()

def search_newspaper_collection(collection, date_range, limit=100):
    """
    Search for newspaper issues in the Internet Archive
    
    Args:
        collection: Collection identifier
        date_range: Tuple of (start_date, end_date) in YYYY-MM-DD format
        limit: Maximum number of results to return
    
    Returns:
        List of issue identifiers
    """
    logger.info(f"Searching for {collection} issues from {date_range[0]} to {date_range[1]}...")
    
    # Use the Archive.org advanced search API directly
    query = f"collection:{collection} AND date:[{date_range[0]} TO {date_range[1]}]"
    
    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": query,
        "fl[]": "identifier",
        "sort[]": "date asc",
        "rows": limit,
        "page": 1,
        "output": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        
        if not docs:
            logger.warning(f"No issues found for {collection} in date range {date_range}")
            return []
        
        issue_ids = [doc.get("identifier") for doc in docs if "identifier" in doc]
        logger.info(f"Found {len(issue_ids)} issues")
        return issue_ids
        
    except Exception as e:
        logger.error(f"Error searching for issues: {e}")
        return []

def download_ocr(issue_id, output_dir=TEMP_DOWNLOADS):
    """
    Download OCR text for an issue directly from archive.org
    
    Args:
        issue_id: Archive.org identifier
        output_dir: Directory to save the OCR text
    
    Returns:
        Path to the downloaded OCR file, or None if download failed
    """
    logger.info(f"Downloading OCR for {issue_id}...")
    
    # Construct the URL for the OCR text
    ocr_url = f"https://archive.org/download/{issue_id}/{issue_id}_djvu.txt"
    
    # Set up the output file path
    output_file = output_dir / f"{issue_id}.txt"
    
    # Skip if already downloaded
    if output_file.exists():
        logger.info(f"OCR file already exists: {output_file}")
        return output_file
    
    # Download the file with retries
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Use requests to download the file
            response = requests.get(ocr_url, timeout=60)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Write the OCR text to the output file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(response.text)
                
                logger.info(f"Successfully downloaded OCR to {output_file}")
                return output_file
            else:
                logger.warning(f"Failed to download OCR: HTTP {response.status_code}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
        except Exception as e:
            logger.error(f"Error downloading OCR: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
    
    logger.error(f"Failed to download OCR after {max_retries} attempts")
    return None

def download_issues_parallel(issue_ids, max_workers=4):
    """
    Download multiple issues in parallel
    
    Args:
        issue_ids: List of issue identifiers
        max_workers: Maximum number of parallel downloads
    
    Returns:
        List of successfully downloaded issue identifiers
    """
    logger.info(f"Downloading {len(issue_ids)} issues using {max_workers} workers...")
    
    successful_issues = []
    failed_issues = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_issue = {executor.submit(download_ocr, issue_id): issue_id for issue_id in issue_ids}
        
        # Process completed tasks
        for future in as_completed(future_to_issue):
            issue_id = future_to_issue[future]
            try:
                result = future.result()
                if result:
                    successful_issues.append(issue_id)
                else:
                    failed_issues.append(issue_id)
            except Exception as e:
                logger.error(f"Download task for {issue_id} raised an exception: {e}")
                failed_issues.append(issue_id)
    
    logger.info(f"Successfully downloaded {len(successful_issues)} issues")
    logger.info(f"Failed to download {len(failed_issues)} issues")
    
    return successful_issues

def process_issues(issue_ids, output_dir=OUTPUT_DIR):
    """
    Process downloaded issues using the StoryDredge pipeline
    
    Args:
        issue_ids: List of issue identifiers
        output_dir: Output directory for processed issues
    
    Returns:
        Number of successfully processed issues
    """
    # Create a temporary issues file
    issues_file = DATA_DIR / "new_atlanta_issues.json"
    with open(issues_file, "w") as f:
        json.dump({"issues": issue_ids}, f, indent=2)
    
    logger.info(f"Processing {len(issue_ids)} issues...")
    
    try:
        cmd = [
            "python", "batch_process_local_issues.py",
            "--issues-file", str(issues_file),
            "--output", str(output_dir),
            "--ocr-dir", str(TEMP_DOWNLOADS)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Batch processing complete")
        return len(issue_ids)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error processing issues: {e}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error processing issues: {e}")
        return 0

def main():
    args = parse_args()
    
    # Search for issues
    issue_ids = search_newspaper_collection(
        collection="pub_atlanta-constitution",
        date_range=(args.start_date, args.end_date),
        limit=args.max_issues
    )
    
    if not issue_ids:
        logger.error("No issues found. Exiting.")
        return
    
    # Download OCR text for issues
    successful_downloads = download_issues_parallel(issue_ids, max_workers=args.threads)
    
    if not successful_downloads:
        logger.error("No issues were downloaded successfully. Exiting.")
        return
    
    # Process the downloaded issues
    processed_count = process_issues(successful_downloads)
    
    # Print summary
    logger.info("=" * 60)
    logger.info("Processing Summary")
    logger.info("=" * 60)
    logger.info(f"Date Range: {args.start_date} to {args.end_date}")
    logger.info(f"Issues Found: {len(issue_ids)}")
    logger.info(f"Issues Downloaded: {len(successful_downloads)}")
    logger.info(f"Issues Processed: {processed_count}")
    logger.info(f"Processed articles can be found in: {OUTPUT_DIR}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main() 