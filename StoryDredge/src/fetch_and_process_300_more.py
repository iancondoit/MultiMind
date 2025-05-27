#!/usr/bin/env python3
"""
Fetch and process 300 more Atlanta Constitution issues
Enhanced version with better error handling and rate limiting for larger batches
"""

import os
import sys
import json
import requests
import time
import subprocess
import logging
import random
import signal
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"atlanta_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("atlanta_processor")

# Set up paths
TEMP_DOWNLOADS = Path("temp_downloads")
TEMP_DOWNLOADS.mkdir(exist_ok=True)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

OUTPUT_DIR = Path("output/atlanta-constitution")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Track processed issues for resume capability
PROGRESS_FILE = DATA_DIR / "processing_progress.json"

# Global flag for graceful shutdown
shutdown_requested = False

def signal_handler(sig, frame):
    """Handle interrupt signals to allow graceful shutdown"""
    global shutdown_requested
    logger.warning("Interrupt received, finishing current tasks before shutting down...")
    shutdown_requested = True

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Fetch and process 300 more Atlanta Constitution issues")
    parser.add_argument("--start-date", type=str, default="1926-01-01",
                       help="Start date for issue search (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="1935-12-31",
                       help="End date for issue search (YYYY-MM-DD)")
    parser.add_argument("--max-issues", type=int, default=300,
                       help="Maximum number of issues to process")
    parser.add_argument("--threads", type=int, default=4,
                       help="Number of threads for parallel downloads")
    parser.add_argument("--batch-size", type=int, default=50,
                       help="Number of issues to process in each batch")
    parser.add_argument("--resume", action="store_true",
                       help="Resume from last processing point")
    return parser.parse_args()

def load_progress():
    """Load progress from previous run"""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading progress file: {e}")
    
    return {
        "completed_issues": [],
        "failed_issues": [],
        "last_batch": 0,
        "last_date": None
    }

def save_progress(progress_data):
    """Save progress for potential resume"""
    try:
        with open(PROGRESS_FILE, "w") as f:
            json.dump(progress_data, f, indent=2)
        logger.info(f"Progress saved to {PROGRESS_FILE}")
    except Exception as e:
        logger.error(f"Error saving progress: {e}")

def search_newspaper_collection(collection, date_range, limit=300):
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
        "fl[]": "identifier,date",
        "sort[]": "date asc",
        "rows": limit,
        "page": 1,
        "output": "json"
    }
    
    try:
        # Add a small delay to respect rate limits
        time.sleep(1)
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
    if shutdown_requested:
        logger.warning(f"Shutdown requested, skipping download of {issue_id}")
        return None
        
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
        if shutdown_requested:
            logger.warning(f"Shutdown requested during download attempt {attempt+1} for {issue_id}")
            return None
            
        try:
            # Add a small random delay to avoid hitting rate limits
            time.sleep(random.uniform(0.5, 2.0))
            
            # Use requests to download the file
            response = requests.get(ocr_url, timeout=90)
            
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
                    wait_time = retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        except Exception as e:
            logger.error(f"Error downloading OCR: {e}")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    
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
                
            if shutdown_requested:
                logger.warning("Shutdown requested, cancelling remaining downloads")
                for f in future_to_issue:
                    if not f.done():
                        f.cancel()
                break
    
    logger.info(f"Successfully downloaded {len(successful_issues)} issues")
    logger.info(f"Failed to download {len(failed_issues)} issues")
    
    return successful_issues, failed_issues

def process_batch(batch_ids, output_dir=OUTPUT_DIR, batch_num=1):
    """
    Process a batch of downloaded issues using the StoryDredge pipeline
    
    Args:
        batch_ids: List of issue identifiers for this batch
        output_dir: Output directory for processed issues
        batch_num: Batch number for logging
    
    Returns:
        Number of successfully processed issues
    """
    if not batch_ids:
        logger.warning(f"Batch {batch_num} is empty, skipping")
        return 0
        
    # Create a temporary issues file for this batch
    issues_file = DATA_DIR / f"batch_{batch_num}_issues.json"
    with open(issues_file, "w") as f:
        json.dump({"issues": batch_ids}, f, indent=2)
    
    logger.info(f"Processing batch {batch_num} with {len(batch_ids)} issues...")
    
    try:
        cmd = [
            "python", "batch_process_local_issues.py",
            "--issues-file", str(issues_file),
            "--output", str(output_dir),
            "--ocr-dir", str(TEMP_DOWNLOADS)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Batch {batch_num} processing complete")
        return len(batch_ids)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error processing batch {batch_num}: {e}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error processing batch {batch_num}: {e}")
        return 0

def main():
    args = parse_args()
    
    # Load progress if resuming
    progress = load_progress()
    
    if args.resume and progress["last_date"]:
        logger.info(f"Resuming from {progress['last_date']}")
        args.start_date = progress["last_date"]
    
    # Search for issues
    issue_ids = search_newspaper_collection(
        collection="pub_atlanta-constitution",
        date_range=(args.start_date, args.end_date),
        limit=args.max_issues
    )
    
    if not issue_ids:
        logger.error("No issues found. Exiting.")
        return
    
    # Filter out already processed issues if resuming
    if args.resume:
        issue_ids = [issue_id for issue_id in issue_ids if issue_id not in progress["completed_issues"]]
        logger.info(f"After filtering already processed issues, {len(issue_ids)} issues remain")
    
    if not issue_ids:
        logger.info("All discovered issues have already been processed. Exiting.")
        return
    
    # Process in batches to avoid overwhelming the system
    total_processed = 0
    batch_size = args.batch_size
    starting_batch = progress["last_batch"] + 1 if args.resume else 1
    
    for batch_num, i in enumerate(range(0, len(issue_ids), batch_size), starting_batch):
        if shutdown_requested:
            logger.warning(f"Shutdown requested, stopping after batch {batch_num-1}")
            break
            
        batch_issue_ids = issue_ids[i:i+batch_size]
        logger.info(f"Processing batch {batch_num} of {len(issue_ids)//batch_size + 1}")
        
        # Download OCR text for this batch
        successful_downloads, failed_downloads = download_issues_parallel(
            batch_issue_ids, 
            max_workers=args.threads
        )
        
        # Update progress
        progress["failed_issues"].extend(failed_downloads)
        
        if not successful_downloads:
            logger.error(f"No issues were downloaded successfully in batch {batch_num}. Moving to next batch.")
            continue
        
        # Process the batch
        processed_count = process_batch(successful_downloads, batch_num=batch_num)
        total_processed += processed_count
        
        # Update progress
        if processed_count > 0:
            progress["completed_issues"].extend(successful_downloads)
            progress["last_batch"] = batch_num
            
            # Find latest date processed
            if batch_issue_ids:
                date_parts = batch_issue_ids[-1].split('_')
                if len(date_parts) > 2:
                    progress["last_date"] = date_parts[2]
                    
            save_progress(progress)
        
        # Pause between batches to be kind to archive.org
        if i + batch_size < len(issue_ids) and not shutdown_requested:
            pause_time = random.uniform(30, 60)
            logger.info(f"Pausing for {pause_time:.1f} seconds before next batch...")
            time.sleep(pause_time)
    
    # Run the summary update script
    try:
        logger.info("Updating summary statistics...")
        subprocess.run(["python", "update_summary.py"], check=True)
    except Exception as e:
        logger.error(f"Error updating summary: {e}")
    
    # Print final summary
    logger.info("=" * 60)
    logger.info("Processing Summary")
    logger.info("=" * 60)
    logger.info(f"Date Range: {args.start_date} to {args.end_date}")
    logger.info(f"Issues Found: {len(issue_ids)}")
    logger.info(f"Issues Processed: {total_processed}")
    logger.info(f"Issues Failed: {len(progress['failed_issues'])}")
    logger.info(f"Processed articles can be found in: {OUTPUT_DIR}")
    logger.info("=" * 60)
    
    # Update the summary markdown
    logger.info("Full log available at: " + str(log_file))

if __name__ == "__main__":
    start_time = time.time()
    try:
        main()
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Total execution time: {elapsed_time:.2f} seconds ({timedelta(seconds=int(elapsed_time))})") 