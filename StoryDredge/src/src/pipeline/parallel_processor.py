"""
Parallel Processor Module

This module enhances the BatchProcessor with parallel processing capabilities
to improve performance when processing multiple newspaper issues.

Features:
- Process multiple newspaper issues in parallel
- Configurable process pool size
- Progress tracking across parallel processes
- Shared result collection
- Dynamic workload distribution
"""

import os
import json
import time
import logging
import multiprocessing
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.utils.errors import StoryDredgeError
from src.utils.config import get_config_manager
from src.utils.progress import ProgressReporter
from src.fetcher.archive_fetcher import ArchiveFetcher
from src.cleaner.ocr_cleaner import OCRCleaner
from src.splitter.article_splitter import ArticleSplitter
from src.classifier.article_classifier import ArticleClassifier
from src.formatter.hsa_formatter import HSAFormatter


def process_issue_worker(
    issue_id: str, 
    output_dir: str,
    issue_output_dir: str,
    **kwargs
) -> Tuple[str, bool, Dict[str, Any]]:
    """
    Worker function to process a single newspaper issue.
    
    This function is designed to be run in a separate process as part of
    a parallel processing pool.
    
    Args:
        issue_id: The archive.org identifier for the newspaper issue
        output_dir: Base output directory
        issue_output_dir: Output directory for this specific issue
        **kwargs: Additional parameters for processing
        
    Returns:
        Tuple containing:
        - issue_id: The processed issue ID
        - success: Whether processing was successful
        - stats: Processing statistics
    """
    try:
        start_time = time.time()
        
        # Initialize components for this process
        fetcher = ArchiveFetcher()
        cleaner = OCRCleaner()
        splitter = ArticleSplitter()
        classifier = ArticleClassifier()
        formatter = HSAFormatter(output_dir=Path(output_dir) / "hsa-ready")
        
        # Create issue directory
        Path(issue_output_dir).mkdir(exist_ok=True, parents=True)
        
        # Component timing
        timings = {}
        
        # Step 1: Fetch the issue from archive.org
        fetch_start = time.time()
        raw_text = fetcher.fetch_issue(issue_id)
        timings["fetch"] = time.time() - fetch_start
        
        # Save raw text for debugging purposes
        with open(Path(issue_output_dir) / "raw.txt", "w", encoding="utf-8") as f:
            f.write(raw_text)
        
        # Step 2: Clean the OCR text
        clean_start = time.time()
        cleaned_text = cleaner.clean_text(raw_text)
        timings["clean"] = time.time() - clean_start
        
        # Save cleaned text for debugging purposes
        with open(Path(issue_output_dir) / "cleaned.txt", "w", encoding="utf-8") as f:
            f.write(cleaned_text)
            
        # Step 3: Split the text into articles
        split_start = time.time()
        articles = splitter.split_articles(cleaned_text)
        timings["split"] = time.time() - split_start
        
        # Save individual articles
        articles_dir = Path(issue_output_dir) / "articles"
        articles_dir.mkdir(exist_ok=True)
        for i, article in enumerate(articles):
            with open(articles_dir / f"article_{i:04d}.json", "w", encoding="utf-8") as f:
                json.dump(article, f, indent=2)
        
        # Step 4: Classify the articles
        classify_start = time.time()
        classified_articles = classifier.classify_batch(articles)
        timings["classify"] = time.time() - classify_start
        
        # Save classified articles
        classified_dir = Path(issue_output_dir) / "classified"
        classified_dir.mkdir(exist_ok=True)
        for i, article in enumerate(classified_articles):
            with open(classified_dir / f"article_{i:04d}.json", "w", encoding="utf-8") as f:
                json.dump(article, f, indent=2)
        
        # Step 5: Format articles for HSA
        format_start = time.time()
        formatted_paths = formatter.process_batch(classified_articles)
        timings["format"] = time.time() - format_start
        
        # Prepare stats
        processing_time = time.time() - start_time
        stats = {
            "issue_id": issue_id,
            "processing_time": processing_time,
            "articles_count": len(articles),
            "classified_count": len(classified_articles),
            "formatted_count": len(formatted_paths),
            "component_timings": timings,
            "timestamp": datetime.now().isoformat()
        }
        
        return (issue_id, True, stats)
        
    except Exception as e:
        error_msg = f"Error processing issue {issue_id}: {str(e)}"
        return (issue_id, False, {"error": error_msg})


class ParallelProcessor:
    """
    Processes multiple newspaper issues in parallel.
    
    This class enhances the BatchProcessor with parallel processing capabilities
    to improve performance when processing multiple newspaper issues.
    """
    
    def __init__(self, 
                 output_dir: str = "output",
                 checkpoint_file: str = "checkpoint.json",
                 max_workers: int = None,
                 max_retries: int = 3,
                 enable_checkpointing: bool = True):
        """
        Initialize the ParallelProcessor.
        
        Args:
            output_dir: Directory for storing processed results
            checkpoint_file: File to store processing progress for resume capability
            max_workers: Maximum number of worker processes (defaults to CPU count)
            max_retries: Maximum number of retries for failed issues
            enable_checkpointing: Whether to create checkpoints for resume capability
        """
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        config_manager = get_config_manager()
        config_manager.load()
        self.config = config_manager.config
        
        # Setup directories
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Worker configuration
        self.max_workers = max_workers or max(1, os.cpu_count() - 1)  # Default to CPU count - 1
        
        # Setup checkpoint file
        self.checkpoint_file = Path(checkpoint_file)
        self.enable_checkpointing = enable_checkpointing
        
        # Retry configuration
        self.max_retries = max_retries
        
        # State tracking
        self.processed_issues = self._load_checkpoint() if enable_checkpointing and self.checkpoint_file.exists() else set()
        self.failed_issues = set()
        
        self.logger.info(f"Parallel processor initialized with {self.max_workers} workers")
        if self.processed_issues:
            self.logger.info(f"Loaded checkpoint with {len(self.processed_issues)} already processed issues")
    
    def process_issue(self, issue_id: str) -> bool:
        """
        Process a single newspaper issue through the entire pipeline.
        
        This is a convenience method for processing a single issue without
        creating a parallel pool.
        
        Args:
            issue_id: The archive.org identifier for the newspaper issue
            
        Returns:
            True if processing was successful, False otherwise
        """
        if issue_id in self.processed_issues:
            self.logger.info(f"Issue {issue_id} already processed, skipping")
            return True
        
        issue_output_dir = str(self.output_dir / issue_id)
        
        self.logger.info(f"Processing issue: {issue_id}")
        
        # Process the issue using the worker function
        issue_id, success, stats = process_issue_worker(
            issue_id=issue_id,
            output_dir=str(self.output_dir),
            issue_output_dir=issue_output_dir
        )
        
        if success:
            self.processed_issues.add(issue_id)
            if self.enable_checkpointing:
                self._save_checkpoint()
            self.logger.info(f"Successfully processed issue {issue_id}")
            return True
        else:
            self.failed_issues.add(issue_id)
            self.logger.error(f"Failed to process issue {issue_id}: {stats.get('error', 'Unknown error')}")
            return False
    
    def process_batch(self, issue_ids: List[str]) -> Dict[str, Any]:
        """
        Process a batch of newspaper issues in parallel.
        
        Args:
            issue_ids: List of archive.org issue identifiers to process
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        self.logger.info(f"Starting parallel processing of {len(issue_ids)} issues with {self.max_workers} workers")
        
        # Filter out already processed issues if resuming
        pending_issues = [issue_id for issue_id in issue_ids if issue_id not in self.processed_issues]
        skipped_issues = [issue_id for issue_id in issue_ids if issue_id in self.processed_issues]
        
        # Setup progress tracking
        total_issues = len(pending_issues)
        progress = ProgressReporter("Processing Issues", total_issues)
        
        # Track results
        successful = []
        failed = []
        all_stats = []
        
        # Process issues in parallel
        if pending_issues:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all jobs
                future_to_issue = {}
                for issue_id in pending_issues:
                    issue_output_dir = str(self.output_dir / issue_id)
                    future = executor.submit(
                        process_issue_worker,
                        issue_id=issue_id,
                        output_dir=str(self.output_dir),
                        issue_output_dir=issue_output_dir
                    )
                    future_to_issue[future] = issue_id
                
                # Process results as they complete
                completed = 0
                for future in as_completed(future_to_issue):
                    issue_id = future_to_issue[future]
                    try:
                        result_issue_id, success, stats = future.result()
                        
                        if success:
                            successful.append(issue_id)
                            all_stats.append(stats)
                            self.processed_issues.add(issue_id)
                        else:
                            failed.append(issue_id)
                            self.failed_issues.add(issue_id)
                            self.logger.error(f"Failed to process issue {issue_id}: {stats.get('error', 'Unknown error')}")
                    
                    except Exception as e:
                        failed.append(issue_id)
                        self.failed_issues.add(issue_id)
                        self.logger.error(f"Error in worker for issue {issue_id}: {e}")
                    
                    # Update progress
                    completed += 1
                    progress.update(completed)
                    
                    # Save checkpoint periodically
                    if self.enable_checkpointing and completed % 5 == 0:
                        self._save_checkpoint()
        
        # Final checkpoint save
        if self.enable_checkpointing:
            self._save_checkpoint()
        
        # Calculate processing time
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Prepare results summary
        results = {
            "total_issues": len(issue_ids),
            "successful": len(successful),
            "failed": len(failed),
            "skipped": len(skipped_issues),
            "processing_time": f"{int(hours)}h {int(minutes)}m {int(seconds)}s",
            "successful_issues": successful,
            "failed_issues": failed,
            "skipped_issues": skipped_issues,
            "timestamp": datetime.now().isoformat(),
            "workers": self.max_workers,
            "issue_stats": all_stats
        }
        
        # Calculate performance metrics
        if successful:
            avg_issue_time = sum(stats.get("processing_time", 0) for stats in all_stats) / len(successful)
            results["avg_issue_time"] = avg_issue_time
            results["throughput"] = len(successful) / elapsed_time if elapsed_time > 0 else 0
        
        # Save processing report
        report_path = self.output_dir / "processing_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Parallel processing completed: {len(successful)} successful, {len(failed)} failed, {len(skipped_issues)} skipped")
        self.logger.info(f"Processing time: {results['processing_time']}")
        
        if successful:
            self.logger.info(f"Average time per issue: {avg_issue_time:.2f} seconds")
            self.logger.info(f"Throughput: {results['throughput']:.4f} issues/second")
        
        return results
    
    def _load_checkpoint(self) -> set:
        """Load checkpoint of processed issues."""
        try:
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                checkpoint_data = json.load(f)
                return set(checkpoint_data.get("processed_issues", []))
        except (json.JSONDecodeError, FileNotFoundError):
            self.logger.warning(f"Could not load checkpoint file {self.checkpoint_file}")
            return set()
    
    def _save_checkpoint(self) -> None:
        """Save checkpoint of processed issues."""
        checkpoint_data = {
            "processed_issues": list(self.processed_issues),
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(checkpoint_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving checkpoint: {e}")


def main():
    """Main function for testing the parallel processor."""
    import argparse
    
    parser = argparse.ArgumentParser(description="StoryDredge Parallel Processing")
    parser.add_argument("--issue", help="Archive.org ID for a specific issue")
    parser.add_argument("--issues-file", help="JSON file with issues to process")
    parser.add_argument("--workers", type=int, default=None, help="Number of worker processes")
    parser.add_argument("--output-dir", type=str, default="output", help="Directory for output files")
    parser.add_argument("--checkpoint-file", type=str, default="checkpoint.json", help="Checkpoint file for resume capability")
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create parallel processor
    processor = ParallelProcessor(
        output_dir=args.output_dir,
        checkpoint_file=args.checkpoint_file,
        max_workers=args.workers
    )
    
    # Process single issue
    if args.issue:
        logging.info(f"Processing single issue: {args.issue}")
        result = processor.process_issue(args.issue)
        if result:
            logging.info(f"Successfully processed issue {args.issue}")
        else:
            logging.error(f"Failed to process issue {args.issue}")
    
    # Process issues from file
    elif args.issues_file:
        if not Path(args.issues_file).exists():
            logging.error(f"Issues file not found: {args.issues_file}")
            return
            
        try:
            with open(args.issues_file, 'r') as f:
                issues_data = json.load(f)
                
            if isinstance(issues_data, list):
                issue_ids = issues_data
            elif isinstance(issues_data, dict) and "issues" in issues_data:
                issue_ids = issues_data["issues"]
            else:
                logging.error("Invalid issues file format. Expected a list or a dict with 'issues' key.")
                return
                
            logging.info(f"Processing {len(issue_ids)} issues from {args.issues_file}")
            results = processor.process_batch(issue_ids)
            
            logging.info(f"Batch processing completed: {results['successful']} successful, {results['failed']} failed")
            
        except Exception as e:
            logging.error(f"Error processing issues from file: {e}")
    
    else:
        parser.print_help()
        logging.warning("No input specified. Use --issue or --issues-file.")


if __name__ == "__main__":
    main() 