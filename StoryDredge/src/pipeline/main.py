#!/usr/bin/env python3
"""
main.py - Main pipeline orchestration for StoryDredge

This script orchestrates the entire pipeline process:
1. Fetch OCR from archive.org
2. Clean and normalize text
3. Split into articles
4. Classify with local LLM
5. Format for Human Story Atlas
6. Organize into HSA-ready folder structure by publication and date

Can process either in sequential mode (BatchProcessor) or parallel mode (ParallelProcessor).
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

from src.pipeline.batch_processor import BatchProcessor
from src.pipeline.parallel_processor import ParallelProcessor


def setup_logging():
    """Configure logging for the pipeline."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create a timestamp for the log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / f"pipeline_{timestamp}.log"),
            logging.StreamHandler()
        ]
    )


def main():
    """Main pipeline entry point."""
    parser = argparse.ArgumentParser(description="StoryDredge newspaper processing pipeline")
    parser.add_argument("--issue", help="Archive.org ID for a specific issue")
    parser.add_argument("--issues-file", help="JSON file with issues to process")
    parser.add_argument("--workers", type=int, default=None, help="Number of issues to process in parallel")
    parser.add_argument("--sequential", action="store_true", help="Force sequential processing even if parallel workers specified")
    parser.add_argument("--output-dir", type=str, default="output", help="Directory for output files")
    parser.add_argument("--checkpoint-file", type=str, default="checkpoint.json", help="Checkpoint file for resume capability")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmarks after processing")
    parser.add_argument("--skip-hsa-migration", action="store_true", help="Skip the HSA migration step")
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    logging.info("StoryDredge pipeline initialized")
    
    # Determine processing mode
    use_parallel = args.workers is not None and not args.sequential
    
    # Create processor based on mode
    if use_parallel:
        logging.info(f"Using parallel processing with {args.workers} workers")
        processor = ParallelProcessor(
            output_dir=args.output_dir,
            checkpoint_file=args.checkpoint_file,
            max_workers=args.workers
        )
    else:
        logging.info("Using sequential processing")
        processor = BatchProcessor(
            output_dir=args.output_dir,
            checkpoint_file=args.checkpoint_file
        )
    
    # Track processing time
    start_time = time.time()
    
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
            sys.exit(1)
            
        try:
            with open(args.issues_file, 'r') as f:
                issues_data = json.load(f)
                
            if isinstance(issues_data, list):
                issue_ids = issues_data
            elif isinstance(issues_data, dict) and "issues" in issues_data:
                issue_ids = issues_data["issues"]
            else:
                logging.error("Invalid issues file format. Expected a list or a dict with 'issues' key.")
                sys.exit(1)
                
            logging.info(f"Processing {len(issue_ids)} issues from {args.issues_file}")
            results = processor.process_batch(issue_ids)
            
            logging.info(f"Batch processing completed: {results['successful']} successful, {results['failed']} failed")
            
        except Exception as e:
            logging.error(f"Error processing issues from file: {e}")
            sys.exit(1)
    
    else:
        parser.print_help()
        logging.warning("No input specified. Use --issue or --issues-file.")
    
    # Report total execution time
    elapsed_time = time.time() - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    logging.info(f"Total execution time: {int(hours)}h {int(minutes)}m {int(seconds)}s")
    
    # Run benchmarks if requested
    if args.benchmark:
        try:
            logging.info("Running pipeline benchmarks...")
            from src.benchmarking.pipeline_benchmarks import analyze_benchmarks
            analysis_results = analyze_benchmarks()
            
            if analysis_results and "bottlenecks" in analysis_results and analysis_results["bottlenecks"]:
                logging.info("Performance bottlenecks identified:")
                for i, bottleneck in enumerate(analysis_results["bottlenecks"]):
                    logging.info(f"{i+1}. {bottleneck['component']}.{bottleneck['operation']}: {bottleneck['avg_execution_time']:.2f} seconds")
            else:
                logging.info("No significant performance bottlenecks identified.")
        except ImportError:
            logging.error("Could not import benchmarking module. Skipping benchmarks.")
        except Exception as e:
            logging.error(f"Error running benchmarks: {e}")
    
    # Run HSA migration step to organize articles by publication and date
    if not args.skip_hsa_migration:
        try:
            logging.info("Running HSA data migration to organize articles by publication and date...")
            
            # Use the same output directory as the pipeline
            source_dir = args.output_dir
            target_dir = os.path.join(args.output_dir, "hsa-ready")
            report_path = os.path.join("reports", "hsa_migration.json")
            
            # Create reports directory if it doesn't exist
            Path("reports").mkdir(exist_ok=True)
            
            # Run the migration script
            cmd = [
                sys.executable,
                "scripts/migrate_hsa_data.py",
                "--source", source_dir,
                "--target", target_dir,
                "--output", report_path
            ]
            
            logging.info(f"Executing command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logging.info("HSA migration completed successfully")
                if result.stdout:
                    logging.info(f"Migration output: {result.stdout}")
            else:
                logging.error(f"HSA migration failed with code {result.returncode}")
                if result.stderr:
                    logging.error(f"Migration error: {result.stderr}")
                if result.stdout:
                    logging.info(f"Migration output: {result.stdout}")
        except Exception as e:
            logging.error(f"Error running HSA migration: {e}")


if __name__ == "__main__":
    main()
