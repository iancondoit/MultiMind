"""
Archive.org Utilities

This module provides functions for interacting with Archive.org,
particularly for fetching OCR text for newspaper issues.
"""

import logging
import os
import requests
import time
from pathlib import Path
from typing import Optional

# Configure logger
logger = logging.getLogger(__name__)

def fetch_ocr_for_issue(issue_id: str, output_path: Path) -> bool:
    """
    Fetch OCR text for a newspaper issue from Archive.org.
    
    Args:
        issue_id: Archive.org identifier for the issue
        output_path: Path to save the OCR text
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Fetching OCR for issue: {issue_id}")
    
    # Check if we already have this in the temp directory
    temp_dir = Path("temp_downloads")
    temp_dir.mkdir(exist_ok=True)
    temp_file = temp_dir / f"{issue_id}.txt"
    
    if temp_file.exists():
        logger.info(f"Using cached OCR from: {temp_file}")
        try:
            with open(temp_file, 'r', encoding='utf-8', errors='replace') as src, \
                 open(output_path, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
            return True
        except Exception as e:
            logger.warning(f"Failed to use cached OCR: {e}")
    
    # Construct the URL for the OCR text
    ocr_url = f"https://archive.org/download/{issue_id}/{issue_id}_djvu.txt"
    
    # Add some delay to respect rate limits
    time.sleep(1)
    
    try:
        # Fetch the OCR text
        response = requests.get(ocr_url, timeout=60)
        response.raise_for_status()
        
        # Save to temp file and output path
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        logger.info(f"OCR fetched and saved to: {output_path}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch OCR: {e}")
        return False
    except Exception as e:
        logger.error(f"Error saving OCR text: {e}")
        return False 