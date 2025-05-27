#!/usr/bin/env python3
"""
Manual processor to download Atlanta Constitution OCR text directly 
and save it for processing with StoryDredge pipeline.
"""

import os
import sys
import json
import requests
import time
from pathlib import Path

# Set up paths
temp_downloads = Path("temp_downloads")
temp_downloads.mkdir(exist_ok=True)

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# Sample issues to try
sample_issues = [
    "per_atlanta-constitution_1910-01-02_42_201",
    "per_atlanta-constitution_1910-01-10_42_209",
    "per_atlanta-constitution_1910-01-25_42_224",
    "per_atlanta-constitution_1910-01-30_42_229",
]

def download_ocr(issue_id, output_dir=temp_downloads):
    """
    Download OCR text for an issue directly from archive.org
    
    Args:
        issue_id: Archive.org identifier
        output_dir: Directory to save the OCR text
    
    Returns:
        Path to the downloaded OCR file, or None if download failed
    """
    print(f"Downloading OCR for {issue_id}...")
    
    # Construct the URL for the OCR text
    ocr_url = f"https://archive.org/download/{issue_id}/{issue_id}_djvu.txt"
    print(f"URL: {ocr_url}")
    
    # Set up the output file path
    output_file = output_dir / f"{issue_id}.txt"
    
    # Download the file with retries
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Use requests to download the file
            response = requests.get(ocr_url, timeout=30)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Write the OCR text to the output file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(response.text)
                
                print(f"Successfully downloaded OCR to {output_file}")
                return output_file
            else:
                print(f"Failed to download OCR: HTTP {response.status_code}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
        except Exception as e:
            print(f"Error downloading OCR: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
    
    print(f"Failed to download OCR after {max_retries} attempts")
    return None

def save_issue_list(issues, output_file="data/manual_issues.json"):
    """
    Save a list of issues that were successfully downloaded
    
    Args:
        issues: List of successfully downloaded issue IDs
        output_file: Path to save the JSON file
    """
    with open(output_file, "w") as f:
        json.dump({"issues": issues}, f, indent=2)
    
    print(f"Saved {len(issues)} issue IDs to {output_file}")
    return output_file

def main():
    """Download sample issues and prepare for processing"""
    print(f"Attempting to download {len(sample_issues)} sample issues...")
    
    successful_issues = []
    
    for issue_id in sample_issues:
        ocr_file = download_ocr(issue_id)
        if ocr_file:
            successful_issues.append(issue_id)
    
    if successful_issues:
        json_file = save_issue_list(successful_issues)
        
        print("\nYou can now process these issues locally with:")
        print(f"python scripts/process_local_issue.py --issue {successful_issues[0]} --ocr-file {temp_downloads}/{successful_issues[0]}.txt")
        print("\nOr process all downloaded issues with:")
        print(f"python scripts/batch_process_local_issues.py --issues-file {json_file}")
    else:
        print("No issues were downloaded successfully. Check the URLs or network connection.")

if __name__ == "__main__":
    main() 