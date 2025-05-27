#!/usr/bin/env python3
"""
Download Atlanta Constitution Issues (1920s-1960s)

This script downloads 40 years of Atlanta Constitution newspaper issues from archive.org
covering the period from 1920 to 1969. It uses the StoryDredge ArchiveFetcher to:

1. Search for available issues by decade
2. Check OCR availability for each issue
3. Download and cache the OCR text files
4. Generate comprehensive documentation of the download process
5. Create backup-ready file lists for remote storage

Usage:
    python scripts/download_atlanta_constitution_1920s_1960s.py [--dry-run] [--start-year YYYY] [--end-year YYYY]

Arguments:
    --dry-run: Only search and list issues without downloading
    --start-year: Starting year (default: 1920)
    --end-year: Ending year (default: 1969)
    --max-per-year: Maximum issues per year (default: 500)
    --output-dir: Output directory for documentation (default: docs/downloads)

The script will create:
- Downloaded OCR files in cache/
- Issue lists by decade in data/atlanta-constitution/
- Download progress documentation in docs/downloads/
- Backup file lists for remote storage planning
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import time
import concurrent.futures
import threading

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src" / "src"))

try:
    from fetcher.archive_fetcher import ArchiveFetcher
    from utils.progress import ProgressReporter
except ImportError as e:
    print(f"Error: Could not import required modules: {e}")
    print("Make sure you're running this script from the StoryDredge root directory.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/atlanta_constitution_download.log')
    ]
)
logger = logging.getLogger("atlanta_downloader")

class AtlantaConstitutionDownloader:
    """Downloads Atlanta Constitution issues from archive.org for 1920s-1960s."""
    
    def __init__(self, start_year: int = 1920, end_year: int = 1969, 
                 max_per_year: int = 500, output_dir: str = "docs/downloads"):
        """
        Initialize the downloader.
        
        Args:
            start_year: Starting year for downloads
            end_year: Ending year for downloads  
            max_per_year: Maximum issues to download per year
            output_dir: Directory for documentation output
        """
        self.start_year = start_year
        self.end_year = end_year
        self.max_per_year = max_per_year
        self.output_dir = Path(output_dir)
        
        # Create necessary directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        Path("data/atlanta-constitution").mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(parents=True, exist_ok=True)
        
        # Initialize fetcher
        self.fetcher = ArchiveFetcher()
        
        # Thread safety
        self._stats_lock = threading.Lock()
        
        # Statistics tracking
        self.stats = {
            "total_searched": 0,
            "total_found": 0,
            "total_with_ocr": 0,
            "total_downloaded": 0,
            "total_cached": 0,
            "failed_downloads": 0,
            "by_decade": {},
            "by_year": {},
            "start_time": datetime.now(),
            "end_time": None
        }
        
        logger.info(f"Atlanta Constitution Downloader initialized")
        logger.info(f"Date range: {start_year} to {end_year}")
        logger.info(f"Max per year: {max_per_year}")
        logger.info(f"Output directory: {output_dir}")
    
    def get_decades(self) -> List[Tuple[int, int]]:
        """Get list of decade ranges to process."""
        decades = []
        current_decade_start = (self.start_year // 10) * 10
        
        while current_decade_start <= self.end_year:
            decade_end = min(current_decade_start + 9, self.end_year)
            if decade_end >= self.start_year:
                actual_start = max(current_decade_start, self.start_year)
                decades.append((actual_start, decade_end))
            current_decade_start += 10
            
        return decades
    
    def search_issues_for_year(self, year: int) -> List[Dict[str, Any]]:
        """
        Search for Atlanta Constitution issues for a specific year.
        
        Args:
            year: Year to search for
            
        Returns:
            List of issue metadata with OCR availability
        """
        logger.info(f"Searching for Atlanta Constitution issues in {year}")
        
        # Define date range for the year
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        
        try:
            # Search for issues in this year
            issues = self.fetcher.get_newspaper_issues(
                collection="pub_atlanta-constitution",
                date_range=(start_date, end_date),
                limit=self.max_per_year
            )
            
            # Filter to only issues with OCR
            issues_with_ocr = [issue for issue in issues if issue.get("has_ocr", False)]
            
            logger.info(f"Found {len(issues_with_ocr)} issues with OCR for {year}")
            
            # Update statistics
            self.stats["by_year"][year] = {
                "total_found": len(issues),
                "with_ocr": len(issues_with_ocr),
                "downloaded": 0,
                "cached": 0,
                "failed": 0
            }
            
            return issues_with_ocr
            
        except Exception as e:
            logger.error(f"Error searching for issues in {year}: {e}")
            self.stats["by_year"][year] = {
                "total_found": 0,
                "with_ocr": 0,
                "downloaded": 0,
                "cached": 0,
                "failed": 0,
                "error": str(e)
            }
            return []
    
    def download_issue_safe(self, issue: Dict[str, Any]) -> bool:
        """Thread-safe wrapper for download_issue."""
        return self.download_issue(issue)
    
    def download_issue(self, issue: Dict[str, Any]) -> bool:
        """
        Download OCR for a single issue.
        
        Args:
            issue: Issue metadata dictionary
            
        Returns:
            True if successful, False otherwise
        """
        identifier = issue.get("identifier")
        if not identifier:
            logger.warning("Issue missing identifier, skipping")
            return False
        
        try:
            # Check if already cached
            cache_file = self.fetcher.cache_dir / f"{identifier}.txt"
            if cache_file.exists():
                logger.debug(f"Issue {identifier} already cached")
                return True
            
            # Download the issue
            result = self.fetcher.fetch_issue(identifier)
            
            if result:
                logger.info(f"Successfully downloaded {identifier}")
                return True
            else:
                logger.warning(f"Failed to download {identifier}")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading {identifier}: {e}")
            return False
    
    def process_decade(self, start_year: int, end_year: int, dry_run: bool = False) -> Dict[str, Any]:
        """
        Process all issues for a decade.
        
        Args:
            start_year: Starting year of decade
            end_year: Ending year of decade
            dry_run: If True, only search without downloading
            
        Returns:
            Dictionary with decade statistics
        """
        decade_name = f"{start_year}s"
        logger.info(f"Processing decade: {decade_name} ({start_year}-{end_year})")
        
        decade_stats = {
            "decade": decade_name,
            "start_year": start_year,
            "end_year": end_year,
            "years_processed": 0,
            "total_issues_found": 0,
            "total_with_ocr": 0,
            "total_downloaded": 0,
            "total_cached": 0,
            "failed_downloads": 0,
            "issues_by_year": {},
            "all_issues": []
        }
        
        # Process each year in the decade
        for year in range(start_year, end_year + 1):
            logger.info(f"Processing year {year}")
            
            # Search for issues in this year
            issues = self.search_issues_for_year(year)
            
            decade_stats["years_processed"] += 1
            decade_stats["total_issues_found"] += len(issues)
            decade_stats["total_with_ocr"] += len(issues)
            decade_stats["issues_by_year"][year] = len(issues)
            decade_stats["all_issues"].extend(issues)
            
            if not dry_run:
                # Download issues concurrently
                downloaded = 0
                cached = 0
                failed = 0
                
                # Check for already cached files first
                uncached_issues = []
                for issue in issues:
                    identifier = issue.get("identifier")
                    cache_file = self.fetcher.cache_dir / f"{identifier}.txt"
                    if cache_file.exists():
                        cached += 1
                        with self._stats_lock:
                            self.stats["total_cached"] += 1
                    else:
                        uncached_issues.append(issue)
                
                # Download uncached issues concurrently
                if uncached_issues:
                    logger.info(f"Downloading {len(uncached_issues)} uncached issues for {year}")
                    
                    # Use ThreadPoolExecutor for concurrent downloads
                    max_workers = min(8, len(uncached_issues))  # Limit concurrent downloads
                    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # Submit all download tasks
                        future_to_issue = {
                            executor.submit(self.download_issue_safe, issue): issue 
                            for issue in uncached_issues
                        }
                        
                        # Process completed downloads
                        for future in concurrent.futures.as_completed(future_to_issue):
                            issue = future_to_issue[future]
                            try:
                                success = future.result()
                                if success:
                                    downloaded += 1
                                    with self._stats_lock:
                                        self.stats["total_downloaded"] += 1
                                else:
                                    failed += 1
                                    with self._stats_lock:
                                        self.stats["failed_downloads"] += 1
                            except Exception as e:
                                logger.error(f"Error downloading {issue.get('identifier', 'unknown')}: {e}")
                                failed += 1
                                with self._stats_lock:
                                    self.stats["failed_downloads"] += 1
                
                # Update year statistics
                self.stats["by_year"][year]["downloaded"] = downloaded
                self.stats["by_year"][year]["cached"] = cached
                self.stats["by_year"][year]["failed"] = failed
                
                decade_stats["total_downloaded"] += downloaded
                decade_stats["total_cached"] += cached
                decade_stats["failed_downloads"] += failed
                
                logger.info(f"Year {year}: {downloaded} downloaded, {cached} cached, {failed} failed")
        
        # Save decade issue list
        decade_file = Path(f"data/atlanta-constitution/atlanta_constitution_{decade_name}_{start_year}_{end_year}.json")
        issue_data = {
            "decade": decade_name,
            "date_range": f"{start_year}-{end_year}",
            "total_issues": len(decade_stats["all_issues"]),
            "issues": [issue.get("identifier") for issue in decade_stats["all_issues"] if issue.get("identifier")]
        }
        
        with open(decade_file, 'w') as f:
            json.dump(issue_data, f, indent=2)
        
        logger.info(f"Saved {len(issue_data['issues'])} issue IDs to {decade_file}")
        
        # Update global statistics
        self.stats["by_decade"][decade_name] = decade_stats
        
        return decade_stats
    
    def generate_documentation(self) -> None:
        """Generate comprehensive documentation of the download process."""
        
        # Calculate final statistics
        self.stats["end_time"] = datetime.now()
        self.stats["duration"] = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        # Create documentation file
        doc_file = self.output_dir / f"atlanta_constitution_download_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(doc_file, 'w') as f:
            f.write("# Atlanta Constitution Download Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Date Range:** {self.start_year} - {self.end_year}\n")
            f.write(f"**Duration:** {self.stats['duration']:.2f} seconds\n\n")
            
            f.write("## Summary Statistics\n\n")
            f.write(f"- **Total Issues Found:** {sum(decade['total_issues_found'] for decade in self.stats['by_decade'].values())}\n")
            f.write(f"- **Issues with OCR:** {sum(decade['total_with_ocr'] for decade in self.stats['by_decade'].values())}\n")
            f.write(f"- **Successfully Downloaded:** {self.stats['total_downloaded']}\n")
            f.write(f"- **Already Cached:** {self.stats['total_cached']}\n")
            f.write(f"- **Failed Downloads:** {self.stats['failed_downloads']}\n\n")
            
            f.write("## By Decade\n\n")
            for decade_name, decade_stats in self.stats["by_decade"].items():
                f.write(f"### {decade_name}\n")
                f.write(f"- Years: {decade_stats['start_year']}-{decade_stats['end_year']}\n")
                f.write(f"- Issues Found: {decade_stats['total_issues_found']}\n")
                f.write(f"- With OCR: {decade_stats['total_with_ocr']}\n")
                f.write(f"- Downloaded: {decade_stats['total_downloaded']}\n")
                f.write(f"- Cached: {decade_stats['total_cached']}\n")
                f.write(f"- Failed: {decade_stats['failed_downloads']}\n\n")
            
            f.write("## By Year\n\n")
            f.write("| Year | Found | With OCR | Downloaded | Cached | Failed |\n")
            f.write("|------|-------|----------|------------|--------|---------|\n")
            
            for year in sorted(self.stats["by_year"].keys()):
                year_stats = self.stats["by_year"][year]
                f.write(f"| {year} | {year_stats['total_found']} | {year_stats['with_ocr']} | ")
                f.write(f"{year_stats['downloaded']} | {year_stats['cached']} | {year_stats['failed']} |\n")
            
            f.write("\n## File Locations\n\n")
            f.write("### Issue Lists by Decade\n")
            for decade_name in self.stats["by_decade"].keys():
                decade_file = f"data/atlanta-constitution/atlanta_constitution_{decade_name}_*.json"
                f.write(f"- {decade_name}: `{decade_file}`\n")
            
            f.write("\n### Downloaded OCR Files\n")
            f.write("- Location: `cache/`\n")
            f.write("- Format: `per_atlanta-constitution_YYYY-MM-DD_XX_XXX.txt`\n")
            f.write("- Total Files: See summary statistics above\n\n")
            
            f.write("## Remote Backup Planning\n\n")
            f.write("### Recommended Backup Strategy\n")
            f.write("1. **Archive by Decade**: Create compressed archives for each decade\n")
            f.write("2. **Cloud Storage**: Upload to multiple cloud providers for redundancy\n")
            f.write("3. **Verification**: Maintain checksums for integrity verification\n")
            f.write("4. **Documentation**: Keep this report with the backup archives\n\n")
            
            f.write("### Backup Commands\n")
            f.write("```bash\n")
            f.write("# Create decade archives\n")
            for decade_name in self.stats["by_decade"].keys():
                f.write(f"tar -czf atlanta_constitution_{decade_name}.tar.gz cache/per_atlanta-constitution_{decade_name[:4]}*.txt\n")
            f.write("\n# Create master archive\n")
            f.write("tar -czf atlanta_constitution_1920s_1960s_complete.tar.gz cache/per_atlanta-constitution_19*.txt cache/per_atlanta-constitution_196*.txt\n")
            f.write("```\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. **Process Articles**: Use the universal pipeline to extract articles from downloaded OCR\n")
            f.write("2. **Quality Check**: Verify OCR quality and article extraction success rates\n")
            f.write("3. **Remote Backup**: Implement the backup strategy outlined above\n")
            f.write("4. **Integration**: Connect to StoryMap for article ingestion\n\n")
        
        logger.info(f"Documentation saved to {doc_file}")
        
        # Also save statistics as JSON
        stats_file = self.output_dir / f"atlanta_constitution_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(stats_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            stats_copy = self.stats.copy()
            stats_copy["start_time"] = stats_copy["start_time"].isoformat()
            if stats_copy["end_time"]:
                stats_copy["end_time"] = stats_copy["end_time"].isoformat()
            json.dump(stats_copy, f, indent=2)
        
        logger.info(f"Statistics saved to {stats_file}")
    
    def run(self, dry_run: bool = False) -> None:
        """
        Run the complete download process.
        
        Args:
            dry_run: If True, only search and document without downloading
        """
        logger.info("Starting Atlanta Constitution download process")
        logger.info(f"Dry run mode: {dry_run}")
        
        try:
            # Get decades to process
            decades = self.get_decades()
            logger.info(f"Processing {len(decades)} decades: {decades}")
            
            # Process each decade
            for start_year, end_year in decades:
                decade_stats = self.process_decade(start_year, end_year, dry_run)
                logger.info(f"Completed decade {start_year}-{end_year}: {decade_stats['total_with_ocr']} issues with OCR")
            
            # Generate documentation
            self.generate_documentation()
            
            logger.info("Atlanta Constitution download process completed successfully")
            
        except Exception as e:
            logger.error(f"Error during download process: {e}")
            raise
        finally:
            # Always close the fetcher
            self.fetcher.close()

def main():
    """Main function to run the downloader."""
    parser = argparse.ArgumentParser(description="Download Atlanta Constitution issues from 1920s-1960s")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Only search and list issues without downloading")
    parser.add_argument("--start-year", type=int, default=1920,
                       help="Starting year (default: 1920)")
    parser.add_argument("--end-year", type=int, default=1969,
                       help="Ending year (default: 1969)")
    parser.add_argument("--max-per-year", type=int, default=500,
                       help="Maximum issues per year (default: 500)")
    parser.add_argument("--output-dir", type=str, default="docs/downloads",
                       help="Output directory for documentation (default: docs/downloads)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.start_year > args.end_year:
        print("Error: Start year must be less than or equal to end year")
        sys.exit(1)
    
    if args.start_year < 1900 or args.end_year > 2000:
        print("Warning: Years outside 1900-2000 may have limited availability")
    
    # Create and run downloader
    downloader = AtlantaConstitutionDownloader(
        start_year=args.start_year,
        end_year=args.end_year,
        max_per_year=args.max_per_year,
        output_dir=args.output_dir
    )
    
    try:
        downloader.run(dry_run=args.dry_run)
        print(f"\nDownload process completed successfully!")
        print(f"Check {args.output_dir} for detailed documentation.")
        
    except KeyboardInterrupt:
        print("\nDownload process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 