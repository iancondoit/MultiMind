"""
Batch Processor Module

This module provides functionality for batch processing of newspaper issues
through the entire StoryDredge pipeline.

Features:
- Process multiple archive.org newspaper issues sequentially
- Progress tracking with estimated completion time
- Error handling with retry logic
- Logging of processed items and errors
- Checkpoint/resume capability to continue interrupted processing
- Configurable concurrency and rate limiting
"""

import os
import json
import time
import logging
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import re

from src.utils.errors import StoryDredgeError
from src.utils.config import get_config_manager
from src.utils.progress import ProgressReporter
from src.fetcher.archive_fetcher import ArchiveFetcher
from src.cleaner.ocr_cleaner import OCRCleaner
from src.splitter.article_splitter import ArticleSplitter
from src.classifier.article_classifier import ArticleClassifier
from src.formatter.hsa_formatter import HSAFormatter


class BatchProcessor:
    """
    Processes multiple newspaper issues through the entire StoryDredge pipeline.
    
    This class orchestrates the end-to-end processing of newspaper issues from
    archive.org through OCR cleaning, article splitting, and classification.
    It provides robust error handling, progress tracking, and checkpoint/resume
    capability.
    """
    
    def __init__(self, 
                 output_dir: str = "output",
                 checkpoint_file: str = "checkpoint.json",
                 max_retries: int = 3,
                 enable_checkpointing: bool = True):
        """
        Initialize the BatchProcessor.
        
        Args:
            output_dir: Directory for storing processed results
            checkpoint_file: File to store processing progress for resume capability
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
        
        # Setup checkpoint file
        self.checkpoint_file = Path(checkpoint_file)
        self.enable_checkpointing = enable_checkpointing
        
        # Retry configuration
        self.max_retries = max_retries
        
        # Initialize components
        self.fetcher = ArchiveFetcher()
        self.cleaner = OCRCleaner()
        self.splitter = ArticleSplitter()
        self.classifier = ArticleClassifier()
        self.formatter = HSAFormatter(output_dir=self.output_dir / "hsa-ready")
        
        # State tracking
        self.processed_issues = self._load_checkpoint() if enable_checkpointing and self.checkpoint_file.exists() else set()
        self.failed_issues = set()
        
        self.logger.info(f"Batch processor initialized with output directory: {output_dir}")
        if self.processed_issues:
            self.logger.info(f"Loaded checkpoint with {len(self.processed_issues)} already processed issues")
    
    def process_issue(self, issue_id: str) -> bool:
        """
        Process a single newspaper issue through the entire pipeline.
        
        Args:
            issue_id: The archive.org identifier for the newspaper issue
            
        Returns:
            True if processing was successful, False otherwise
        """
        if issue_id in self.processed_issues:
            self.logger.info(f"Issue {issue_id} already processed, skipping")
            return True
        
        # Parse the issue_id to create a cleaner directory structure
        # Example: per_atlanta-constitution_1922-01-05_54_207
        parts = issue_id.split("_")
        
        # Default to original approach if we can't parse properly
        if len(parts) < 3 or not parts[1] or not re.match(r'^\d{4}-\d{2}-\d{2}', parts[2]):
            self.logger.warning(f"Could not parse issue_id: {issue_id}, using default structure")
            issue_output_dir = self.output_dir / "hsa-ready" / "unknown" / issue_id
        else:
            # Extract publication and date
            publication = parts[1]
            date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})', parts[2])
            
            if date_match:
                year, month, day = date_match.groups()
                # Use direct date-based directory structure under hsa-ready
                issue_output_dir = self.output_dir / "hsa-ready" / publication / year / month / day
            else:
                # Fallback to original approach but still under hsa-ready
                self.logger.warning(f"Could not parse date from issue_id: {issue_id}, using default structure")
                issue_output_dir = self.output_dir / "hsa-ready" / publication / issue_id
        
        issue_output_dir.mkdir(exist_ok=True, parents=True)
        
        self.logger.info(f"Processing issue: {issue_id}")
        
        try:
            # Step 1: Fetch the issue from archive.org
            self.logger.debug(f"Fetching issue {issue_id} from archive.org")
            raw_text = self.fetcher.fetch_issue(issue_id)
            
            # Save raw text for debugging purposes
            with open(issue_output_dir / "raw.txt", "w", encoding="utf-8") as f:
                f.write(raw_text)
            
            # Step 2: Clean the OCR text
            self.logger.debug(f"Cleaning OCR text for issue {issue_id}")
            cleaned_text = self.cleaner.clean_text(raw_text)
            
            # Save cleaned text for debugging purposes
            with open(issue_output_dir / "cleaned.txt", "w", encoding="utf-8") as f:
                f.write(cleaned_text)
                
            # Step 3: Split the text into articles
            self.logger.debug(f"Splitting issue {issue_id} into articles")
            articles = self.splitter.split_articles(cleaned_text)
            
            # Save individual articles
            articles_dir = issue_output_dir / "articles"
            articles_dir.mkdir(exist_ok=True)
            for i, article in enumerate(articles):
                with open(articles_dir / f"article_{i:04d}.json", "w", encoding="utf-8") as f:
                    json.dump(article, f, indent=2)
            
            # Step 4: Classify the articles
            self.logger.debug(f"Classifying {len(articles)} articles for issue {issue_id}")
            classified_articles = self.classifier.classify_batch(articles)
            
            # Save classified articles
            classified_dir = issue_output_dir / "classified"
            classified_dir.mkdir(exist_ok=True)
            for i, article in enumerate(classified_articles):
                with open(classified_dir / f"article_{i:04d}.json", "w", encoding="utf-8") as f:
                    json.dump(article, f, indent=2)
            
            # Step 5: Format articles for HSA
            self.logger.debug(f"Formatting {len(classified_articles)} articles for HSA")
            formatted_paths = self.formatter.process_batch(classified_articles)
            
            # Log HSA formatting results
            self.logger.info(f"Successfully formatted {len(formatted_paths)} articles for HSA")
            
            # Update processed issues set and save checkpoint
            self.processed_issues.add(issue_id)
            if self.enable_checkpointing:
                self._save_checkpoint()
                
            self.logger.info(f"Successfully processed issue {issue_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error processing issue {issue_id}: {e}")
            self.failed_issues.add(issue_id)
            return False
    
    def process_batch(self, issue_ids: List[str]) -> Dict[str, Any]:
        """
        Process a batch of newspaper issues.
        
        Args:
            issue_ids: List of archive.org issue identifiers to process
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        self.logger.info(f"Starting batch processing of {len(issue_ids)} issues")
        
        # Setup progress tracking
        total_issues = len(issue_ids)
        progress = ProgressReporter("Processing Issues", total_issues)
        
        # Track results
        successful = []
        failed = []
        skipped = []
        
        # Process each issue
        for i, issue_id in enumerate(issue_ids):
            # Skip already processed issues if resuming
            if issue_id in self.processed_issues:
                self.logger.info(f"Issue {issue_id} already processed, skipping")
                skipped.append(issue_id)
                progress.update(i + 1)
                continue
                
            # Process with retry logic
            success = False
            for attempt in range(1, self.max_retries + 1):
                try:
                    if self.process_issue(issue_id):
                        success = True
                        successful.append(issue_id)
                        break
                    else:
                        self.logger.warning(f"Failed to process issue {issue_id}, attempt {attempt}/{self.max_retries}")
                except Exception as e:
                    self.logger.error(f"Error processing issue {issue_id} (attempt {attempt}/{self.max_retries}): {e}")
                    # Sleep before retry (with exponential backoff)
                    if attempt < self.max_retries:
                        backoff_time = 2 ** (attempt - 1)  # 1, 2, 4, 8... seconds
                        self.logger.info(f"Retrying in {backoff_time} seconds...")
                        time.sleep(backoff_time)
            
            if not success:
                failed.append(issue_id)
                self.failed_issues.add(issue_id)
            
            # Update progress
            progress.update(i + 1)
        
        # Calculate processing time
        elapsed_time = time.time() - start_time
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Prepare results summary
        results = {
            "total_issues": total_issues,
            "successful": len(successful),
            "failed": len(failed),
            "skipped": len(skipped),
            "processing_time": f"{int(hours)}h {int(minutes)}m {int(seconds)}s",
            "successful_issues": successful,
            "failed_issues": failed,
            "skipped_issues": skipped,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save processing report
        report_path = self.output_dir / "processing_report.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        
        self.logger.info(f"Batch processing completed: {len(successful)} successful, {len(failed)} failed, {len(skipped)} skipped")
        self.logger.info(f"Processing time: {results['processing_time']}")
        self.logger.info(f"Processing report saved to {report_path}")
        
        return results
    
    def _load_checkpoint(self) -> set:
        """
        Load processing checkpoint from file.
        
        Returns:
            Set of already processed issue IDs
        """
        try:
            with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                checkpoint_data = json.load(f)
                self.logger.info(f"Loaded checkpoint from {self.checkpoint_file}")
                return set(checkpoint_data.get("processed_issues", []))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"Could not load checkpoint: {e}")
            return set()
    
    def _save_checkpoint(self) -> None:
        """Save processing checkpoint to file."""
        try:
            checkpoint_data = {
                "processed_issues": list(self.processed_issues),
                "failed_issues": list(self.failed_issues),
                "timestamp": datetime.now().isoformat()
            }
            
            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(checkpoint_data, f, indent=2)
                
            self.logger.debug(f"Updated checkpoint with {len(self.processed_issues)} processed issues")
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")


def main():
    """
    Command-line entry point for batch processing.
    """
    parser = argparse.ArgumentParser(description="StoryDredge Batch Processor")
    parser.add_argument("--input", "-i", required=True, help="Input file with list of issue IDs (one per line)")
    parser.add_argument("--output", "-o", default="output", help="Output directory for processed results")
    parser.add_argument("--checkpoint", default="checkpoint.json", help="Checkpoint file for resume capability")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum retries for failed issues")
    parser.add_argument("--disable-checkpointing", action="store_true", help="Disable checkpointing")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       help="Logging level")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("batch_processor.log"),
            logging.StreamHandler()
        ]
    )
    
    # Read issue IDs from input file
    with open(args.input, "r", encoding="utf-8") as f:
        issue_ids = [line.strip() for line in f if line.strip()]
    
    # Create batch processor
    processor = BatchProcessor(
        output_dir=args.output,
        checkpoint_file=args.checkpoint,
        max_retries=args.max_retries,
        enable_checkpointing=not args.disable_checkpointing
    )
    
    # Process the batch
    processor.process_batch(issue_ids)


if __name__ == "__main__":
    main() 