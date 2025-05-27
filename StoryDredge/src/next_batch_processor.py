#!/usr/bin/env python3
"""
Next batch processor for Atlanta Constitution
Waits for current batch to complete, then processes the next 1000 issues
"""

import os
import sys
import json
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"next_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("next_batch_processor")

# Configuration
PROGRESS_FILE = Path("data/processing_progress.json")
CHECK_INTERVAL = 300  # seconds (check every 5 minutes)
NEXT_BATCH_START_DATE = "1956-01-01"
NEXT_BATCH_END_DATE = "1965-12-31"
BATCH_SIZE = 100
MAX_ISSUES = 1000
BATCH_SCRIPT = "./fetch_and_process_300_more.py"

def is_current_process_running():
    """Check if the current processing script is still running"""
    try:
        # Look for the process by name
        result = subprocess.run(
            ["pgrep", "-f", "fetch_and_process_300_more.py"], 
            capture_output=True, 
            text=True
        )
        return len(result.stdout.strip()) > 0
    except Exception as e:
        logger.error(f"Error checking process status: {e}")
        return True  # Assume it's still running if we can't check

def check_progress_completion():
    """Check if the progress file indicates we've processed 2000 issues"""
    if not PROGRESS_FILE.exists():
        logger.warning(f"Progress file {PROGRESS_FILE} doesn't exist yet")
        return False
        
    try:
        with open(PROGRESS_FILE, "r") as f:
            progress = json.load(f)
            
        completed_issues = len(progress.get("completed_issues", []))
        logger.info(f"Current progress: {completed_issues} issues completed")
        
        # We're looking for around 1900-2000 completed issues
        # The number might not be exactly 2000 due to some failures
        return completed_issues >= 1900
    except Exception as e:
        logger.error(f"Error reading progress file: {e}")
        return False

def start_next_batch():
    """Start the next batch of 1000 issues"""
    logger.info(f"Starting next batch of {MAX_ISSUES} issues from {NEXT_BATCH_START_DATE} to {NEXT_BATCH_END_DATE}")
    
    # Back up the current progress file to preserve the history
    if PROGRESS_FILE.exists():
        backup_file = Path(f"data/processing_progress_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        try:
            with open(PROGRESS_FILE, "r") as src, open(backup_file, "w") as dst:
                dst.write(src.read())
            logger.info(f"Backed up progress file to {backup_file}")
            
            # Remove the current progress file so we start fresh
            PROGRESS_FILE.unlink()
            logger.info(f"Removed current progress file for clean processing")
        except Exception as e:
            logger.error(f"Error backing up progress file: {e}")
    
    # Start the new processing batch
    try:
        cmd = [
            BATCH_SCRIPT,
            "--start-date", NEXT_BATCH_START_DATE,
            "--end-date", NEXT_BATCH_END_DATE,
            "--max-issues", str(MAX_ISSUES),
            "--batch-size", str(BATCH_SIZE)
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        # Start the process
        subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("Next batch processing started successfully")
    except Exception as e:
        logger.error(f"Error starting next batch: {e}")

def main():
    """Monitor current processing and start next batch when complete"""
    logger.info("Starting next batch processor")
    logger.info(f"Will process {MAX_ISSUES} issues from {NEXT_BATCH_START_DATE} to {NEXT_BATCH_END_DATE}")
    logger.info(f"Checking every {CHECK_INTERVAL} seconds for completion of current process")
    
    while True:
        process_running = is_current_process_running()
        progress_complete = check_progress_completion()
        
        if not process_running and progress_complete:
            logger.info("Current process complete and progress file indicates completion")
            start_next_batch()
            logger.info("Next batch started. Monitoring complete.")
            break
        elif not process_running and not progress_complete:
            logger.warning("Current process not running but progress file incomplete")
            logger.warning("May indicate unexpected termination. Starting next batch anyway")
            start_next_batch()
            logger.info("Next batch started. Monitoring complete.")
            break
        else:
            logger.info("Current process still running, waiting...")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main() 