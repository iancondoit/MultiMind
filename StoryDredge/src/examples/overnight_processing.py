#!/usr/bin/env python3
"""
Example script for overnight batch processing of newspaper issues.

This script demonstrates how to set up and run a large batch of newspaper
issues for overnight processing using the BatchProcessor.

Usage:
    python examples/overnight_processing.py --input issue_list.txt --output output_dir

Before running:
1. Ensure Ollama is installed and running
2. Make sure issue_list.txt contains archive.org issue IDs (one per line)
3. Consider your hardware capabilities when setting batch size and concurrency
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pipeline.batch_processor import BatchProcessor
from src.utils.config import get_config_manager


def setup_logging(log_dir="logs"):
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(exist_ok=True, parents=True)
    
    # Generate timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(log_dir) / f"overnight_processing_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return log_file


def configure_pipeline(config_manager, concurrency=None, model=None):
    """Configure the pipeline for optimal overnight processing."""
    # Load the current configuration
    config_manager.load()
    
    # Set classifier parameters for overnight processing
    if model:
        config_manager.config.classifier.model_name = model
    
    if concurrency:
        config_manager.config.classifier.concurrency = concurrency
    
    # Save the updated configuration
    config_manager.save()
    
    logging.info(f"Pipeline configured with model={config_manager.config.classifier.model_name}, "
                f"concurrency={config_manager.config.classifier.concurrency}")


def main():
    """Run the overnight batch processing."""
    parser = argparse.ArgumentParser(description="StoryDredge Overnight Batch Processing")
    parser.add_argument("--input", "-i", required=True, help="Input file with list of issue IDs (one per line)")
    parser.add_argument("--output", "-o", default="output", help="Output directory for processed results")
    parser.add_argument("--checkpoint", default="checkpoint.json", help="Checkpoint file for resume capability")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum retries for failed issues")
    parser.add_argument("--model", default=None, help="Ollama model to use for classification")
    parser.add_argument("--concurrency", type=int, default=None, help="Number of concurrent classifications")
    
    args = parser.parse_args()
    
    # Setup logging
    log_file = setup_logging()
    logging.info("Starting overnight batch processing")
    
    # Configure pipeline settings
    config_manager = get_config_manager()
    configure_pipeline(config_manager, args.concurrency, args.model)
    
    try:
        # Read issue IDs from input file
        if not Path(args.input).exists():
            logging.error(f"Input file not found: {args.input}")
            return 1
            
        with open(args.input, "r", encoding="utf-8") as f:
            issue_ids = [line.strip() for line in f if line.strip()]
            
        logging.info(f"Loaded {len(issue_ids)} issues to process")
        
        # Create batch processor
        processor = BatchProcessor(
            output_dir=args.output,
            checkpoint_file=args.checkpoint,
            max_retries=args.max_retries
        )
        
        # Process the batch
        start_time = datetime.now()
        logging.info(f"Batch processing started at {start_time}")
        
        report = processor.process_batch(issue_ids)
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Log summary
        logging.info(f"Batch processing completed at {end_time}")
        logging.info(f"Total duration: {duration}")
        logging.info(f"Successfully processed: {report['successful']} issues")
        logging.info(f"Failed: {report['failed']} issues")
        logging.info(f"Skipped: {report['skipped']} issues")
        logging.info(f"Processing rate: {report['processed_per_hour']:.2f} issues per hour")
        
        if report['failed'] > 0:
            logging.warning(f"Failed issues: {', '.join(report['failed_issues'])}")
            logging.warning(f"See the detailed log at {log_file} for more information")
        
        return 0
        
    except KeyboardInterrupt:
        logging.info("Batch processing interrupted by user")
        return 130
        
    except Exception as e:
        logging.exception(f"Unexpected error during batch processing: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 