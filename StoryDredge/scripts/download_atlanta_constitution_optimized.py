#!/usr/bin/env python3
"""
Optimized Atlanta Constitution Downloader

This optimized version eliminates redundant API calls and downloads much faster by:
1. Skipping OCR availability checks - just try to download directly
2. Using batch operations and concurrent downloads
3. Eliminating the double API call pattern (check + download)
4. Ultra-aggressive rate limiting settings

Expected performance improvement: 5-10x faster than the original script.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import time

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src" / "src"))

try:
    from fetcher.archive_fetcher_optimized import OptimizedArchiveFetcher
except ImportError as e:
    print(f"Error: Could not import optimized fetcher: {e}")
    print("Make sure you're running this script from the StoryDredge root directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/atlanta_constitution_optimized.log')
    ]
)
logger = logging.getLogger("optimized_downloader")

class OptimizedAtlantaDownloader:
    """Ultra-fast Atlanta Constitution downloader."""
    
    def __init__(self, start_year: int = 1920, end_year: int = 1969, max_workers: int = 64):
        """
        Initialize the optimized downloader.
        
        Args:
            start_year: Starting year for downloads
            end_year: Ending year for downloads
            max_workers: Maximum concurrent download threads
        """
        self.start_year = start_year
        self.end_year = end_year
        self.max_workers = max_workers
        
        # Create necessary directories
        Path("logs").mkdir(parents=True, exist_ok=True)
        
        # Initialize optimized fetcher
        self.fetcher = OptimizedArchiveFetcher(max_workers=max_workers)
        
        # Statistics
        self.stats = {
            "total_years": end_year - start_year + 1,
            "total_searched": 0,
            "total_downloaded": 0,
            "total_cached": 0,
            "total_no_ocr": 0,
            "total_failed": 0,
            "by_year": {},
            "start_time": datetime.now()
        }
        
        logger.info(f"Optimized downloader initialized")
        logger.info(f"Date range: {start_year} to {end_year}")
        logger.info(f"Max workers: {max_workers}")
    
    def download_year_optimized(self, year: int) -> Dict[str, Any]:
        """
        Download all issues for a specific year using optimized approach.
        
        Args:
            year: Year to download
            
        Returns:
            Download statistics for the year
        """
        logger.info(f"Starting optimized download for {year}")
        
        # Search for all issues in the year (no OCR checking)
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        identifiers = self.fetcher.search_newspaper_collection_optimized(
            collection="pub_atlanta-constitution",
            date_range=(start_date, end_date),
            limit=500
        )
        
        if not identifiers:
            logger.warning(f"No issues found for {year}")
            return {
                "year": year,
                "total_found": 0,
                "successful": 0,
                "cached": 0,
                "no_ocr": 0,
                "failed": 0,
                "duration": 0
            }
        
        logger.info(f"Found {len(identifiers)} issues for {year}, starting batch download")
        
        # Download all issues concurrently
        year_start = datetime.now()
        download_stats = self.fetcher.download_issues_batch(identifiers)
        year_duration = (datetime.now() - year_start).total_seconds()
        
        # Compile year statistics
        year_stats = {
            "year": year,
            "total_found": len(identifiers),
            "successful": download_stats["successful"],
            "cached": download_stats["cached"],
            "no_ocr": download_stats["no_ocr"],
            "failed": download_stats["failed"],
            "duration": year_duration
        }
        
        # Update global statistics
        self.stats["total_searched"] += len(identifiers)
        self.stats["total_downloaded"] += download_stats["successful"]
        self.stats["total_cached"] += download_stats["cached"]
        self.stats["total_no_ocr"] += download_stats["no_ocr"]
        self.stats["total_failed"] += download_stats["failed"]
        self.stats["by_year"][year] = year_stats
        
        logger.info(f"Completed {year} in {year_duration:.1f}s: "
                   f"{download_stats['successful']} downloaded, "
                   f"{download_stats['cached']} cached, "
                   f"{download_stats['no_ocr']} no OCR, "
                   f"{download_stats['failed']} failed")
        
        return year_stats
    
    def run_optimized(self) -> Dict[str, Any]:
        """
        Run the optimized download process for all years.
        
        Returns:
            Complete download statistics
        """
        logger.info(f"Starting optimized download for {self.stats['total_years']} years "
                   f"({self.start_year}-{self.end_year})")
        
        overall_start = datetime.now()
        
        # Process each year
        for year in range(self.start_year, self.end_year + 1):
            try:
                year_stats = self.download_year_optimized(year)
                
                # Log progress
                years_completed = year - self.start_year + 1
                years_remaining = self.end_year - year
                
                if years_completed > 0:
                    avg_time_per_year = (datetime.now() - overall_start).total_seconds() / years_completed
                    estimated_remaining = avg_time_per_year * years_remaining / 60  # in minutes
                    
                    logger.info(f"Progress: {years_completed}/{self.stats['total_years']} years completed. "
                               f"Estimated {estimated_remaining:.1f} minutes remaining.")
                
            except Exception as e:
                logger.error(f"Error processing year {year}: {e}")
                self.stats["by_year"][year] = {
                    "year": year,
                    "error": str(e),
                    "total_found": 0,
                    "successful": 0,
                    "cached": 0,
                    "no_ocr": 0,
                    "failed": 0,
                    "duration": 0
                }
        
        # Finalize statistics
        self.stats["end_time"] = datetime.now()
        self.stats["total_duration"] = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        # Calculate OCR availability rate
        total_with_content = self.stats["total_downloaded"] + self.stats["total_cached"]
        total_attempted = self.stats["total_searched"]
        ocr_rate = (total_with_content / total_attempted * 100) if total_attempted > 0 else 0
        
        logger.info("=" * 60)
        logger.info("OPTIMIZED DOWNLOAD COMPLETE!")
        logger.info("=" * 60)
        logger.info(f"Total duration: {self.stats['total_duration'] / 60:.1f} minutes")
        logger.info(f"Years processed: {self.stats['total_years']}")
        logger.info(f"Issues searched: {self.stats['total_searched']}")
        logger.info(f"Issues downloaded: {self.stats['total_downloaded']}")
        logger.info(f"Issues cached: {self.stats['total_cached']}")
        logger.info(f"Issues without OCR: {self.stats['total_no_ocr']}")
        logger.info(f"Failed downloads: {self.stats['total_failed']}")
        logger.info(f"OCR availability rate: {ocr_rate:.1f}%")
        logger.info(f"Download rate: {total_with_content / (self.stats['total_duration'] / 60):.1f} issues/minute")
        
        return self.stats
    
    def close(self):
        """Close the fetcher."""
        self.fetcher.close()

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Optimized Atlanta Constitution Downloader")
    parser.add_argument("--start-year", type=int, default=1920, help="Starting year (default: 1920)")
    parser.add_argument("--end-year", type=int, default=1969, help="Ending year (default: 1969)")
    parser.add_argument("--max-workers", type=int, default=64, help="Maximum concurrent downloads (default: 64)")
    parser.add_argument("--test-year", type=int, help="Test with a single year only")
    
    args = parser.parse_args()
    
    # If testing with a single year
    if args.test_year:
        args.start_year = args.test_year
        args.end_year = args.test_year
        logger.info(f"Testing with single year: {args.test_year}")
    
    # Create and run downloader
    downloader = OptimizedAtlantaDownloader(
        start_year=args.start_year,
        end_year=args.end_year,
        max_workers=args.max_workers
    )
    
    try:
        stats = downloader.run_optimized()
        
        # Save statistics
        stats_file = Path("logs") / f"optimized_download_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            stats_copy = stats.copy()
            stats_copy["start_time"] = stats_copy["start_time"].isoformat()
            stats_copy["end_time"] = stats_copy["end_time"].isoformat()
            json.dump(stats_copy, f, indent=2)
        
        logger.info(f"Statistics saved to {stats_file}")
        
    except KeyboardInterrupt:
        logger.info("Download interrupted by user")
    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise
    finally:
        downloader.close()

if __name__ == "__main__":
    main() 