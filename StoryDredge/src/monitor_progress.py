#!/usr/bin/env python3
"""
Monitor progress of Atlanta Constitution processing
"""

import os
import json
import time
from pathlib import Path
import argparse
from datetime import datetime

def parse_args():
    parser = argparse.ArgumentParser(description="Monitor Atlanta Constitution processing progress")
    parser.add_argument("--refresh", type=int, default=30,
                       help="Refresh interval in seconds")
    parser.add_argument("--output-dir", type=str, default="output/atlanta-constitution",
                       help="Output directory containing processed issues")
    parser.add_argument("--log-file", type=str, default=None,
                       help="Specific log file to monitor (defaults to latest)")
    return parser.parse_args()

def get_latest_log_file():
    """Find the most recent processing log file"""
    log_dir = Path("logs")
    log_files = list(log_dir.glob("atlanta_processing_*.log"))
    
    if not log_files:
        return None
        
    return max(log_files, key=lambda p: p.stat().st_mtime)

def count_downloaded_issues():
    """Count OCR files in the temp_downloads directory"""
    temp_dir = Path("temp_downloads")
    return len(list(temp_dir.glob("per_atlanta-constitution_*.txt")))

def count_processed_issues(output_dir):
    """Count number of processed days in the output directory"""
    output_path = Path(output_dir) / "atlanta-constitution"
    
    if not output_path.exists():
        return 0
        
    # Count unique days (YYYY/MM/DD directories)
    years = [d for d in output_path.iterdir() if d.is_dir() and d.name.isdigit()]
    
    day_count = 0
    for year in years:
        for month in year.iterdir():
            if month.is_dir():
                day_count += sum(1 for d in month.iterdir() if d.is_dir())
    
    return day_count

def count_processed_articles(output_dir):
    """Count number of articles in the output directory"""
    output_path = Path(output_dir) / "atlanta-constitution"
    
    if not output_path.exists():
        return 0
        
    article_count = 0
    for root, dirs, files in os.walk(output_path):
        article_count += sum(1 for f in files if f.endswith(".json"))
    
    return article_count

def get_progress_data():
    """Get progress data from the progress file"""
    progress_file = Path("data") / "processing_progress.json"
    
    if not progress_file.exists():
        return {"completed_issues": [], "failed_issues": []}
        
    try:
        with open(progress_file, "r") as f:
            return json.load(f)
    except:
        return {"completed_issues": [], "failed_issues": []}

def tail_log(log_file, n=10):
    """Get the last n lines of a log file"""
    if not log_file or not log_file.exists():
        return ["No log file found"]
        
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
            return lines[-n:]
    except:
        return ["Error reading log file"]

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    args = parse_args()
    
    log_file = Path(args.log_file) if args.log_file else get_latest_log_file()
    
    try:
        while True:
            clear_screen()
            
            # Update log file if it's not specified
            if not args.log_file:
                log_file = get_latest_log_file()
            
            # Get current stats
            downloaded = count_downloaded_issues()
            processed_days = count_processed_issues(args.output_dir)
            processed_articles = count_processed_articles(args.output_dir)
            progress_data = get_progress_data()
            
            # Calculate completion percentage
            if "completed_issues" in progress_data:
                completed = len(progress_data.get("completed_issues", []))
                failed = len(progress_data.get("failed_issues", []))
                total_attempted = completed + failed
                if total_attempted > 0:
                    completion_pct = (completed / 300) * 100
                else:
                    completion_pct = 0
            else:
                completed = 0
                failed = 0
                completion_pct = 0
            
            # Print progress information
            print("\n===== ATLANTA CONSTITUTION PROCESSING STATUS =====")
            print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 50)
            print(f"Downloaded OCR files:      {downloaded}")
            print(f"Completed issues:          {completed}")
            print(f"Failed issues:             {failed}")
            print(f"Progress:                  {completion_pct:.1f}% ({completed}/300)")
            print(f"Processed days:            {processed_days}")
            print(f"Extracted articles:        {processed_articles}")
            print("=" * 50)
            
            if log_file:
                print(f"Latest log ({log_file.name}):")
                for line in tail_log(log_file, 10):
                    print(f"  {line.strip()}")
            
            print("\nPress Ctrl+C to exit...")
            
            # Wait for next refresh
            time.sleep(args.refresh)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
    
if __name__ == "__main__":
    main() 