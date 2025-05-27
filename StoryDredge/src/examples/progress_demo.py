#!/usr/bin/env python
"""
Demo script for StoryDredge progress reporting.

This script demonstrates the progress reporting capabilities
of the StoryDredge pipeline with a simulated workflow.
"""

import os
import sys
import time
import random
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    get_logger,
    get_config_manager,
    get_progress_manager,
    ProgressContext,
    track_progress
)

# Configure logging
logger = get_logger("progress_demo")

# Load configuration
config_manager = get_config_manager()
config = config_manager.config

# Get progress manager
progress_manager = get_progress_manager()


def simulate_work(duration: float, steps: int = 10) -> None:
    """
    Simulate work with random progress updates.
    
    Args:
        duration: Total duration in seconds
        steps: Number of progress updates
    """
    step_time = duration / steps
    for _ in range(steps):
        time.sleep(step_time * random.uniform(0.5, 1.5))
        yield


@track_progress("fetch_data", "Fetching newspaper data from archive.org", total_items=5)
def fetch_data(context):
    """Simulate fetching data from archive.org."""
    for i in range(5):
        time.sleep(random.uniform(0.5, 2.0))
        context.update()
        context.add_metric("last_issue", f"newspaper_{i+1}")


@track_progress("clean_ocr", "Cleaning OCR text", total_items=100)
def clean_ocr(context):
    """Simulate cleaning OCR text."""
    for i in range(100):
        time.sleep(random.uniform(0.01, 0.1))
        context.update()
        if i % 20 == 0:
            context.add_metric("errors_fixed", i * 3)


@track_progress("split_articles", "Splitting text into articles", total_items=50)
def split_articles(context):
    """Simulate splitting text into articles."""
    for i in range(50):
        time.sleep(random.uniform(0.1, 0.3))
        context.update()
        if i % 10 == 0:
            context.add_metric("articles_found", i)


@track_progress("classify", "Classifying articles with LLM", total_items=50)
def classify_articles(context):
    """Simulate classifying articles with LLM."""
    for i in range(50):
        time.sleep(random.uniform(0.2, 0.5))
        context.update()
        if i % 10 == 0:
            context.add_metric("processing_speed", f"{random.uniform(1.5, 3.0):.1f} articles/s")


@track_progress("format_output", "Formatting articles for HSA", total_items=50)
def format_output(context):
    """Simulate formatting articles for HSA."""
    for i in range(50):
        time.sleep(random.uniform(0.05, 0.15))
        context.update()
        if i % 10 == 0:
            context.add_metric("output_size", f"{i * 20} KB")


def run_pipeline():
    """Run the simulated pipeline."""
    try:
        logger.info("Starting StoryDredge progress demo")
        
        # Create parent pipeline stage for overall tracking
        parent_stage = progress_manager.create_stage(
            name="pipeline",
            description="Processing newspaper archive",
            weight=1.0
        )
        progress_manager.start_stage("pipeline")
        
        # Run each component with a small pause between them
        print("\n== Starting Pipeline ==\n")
        fetch_data()
        time.sleep(0.5)  # Small pause between stages
        
        clean_ocr()
        time.sleep(0.5)  # Small pause between stages
        
        split_articles()
        time.sleep(0.5)  # Small pause between stages
        
        classify_articles()
        time.sleep(0.5)  # Small pause between stages
        
        format_output()
        
        # Complete pipeline
        progress_manager.complete_stage("pipeline")
        
        logger.info("Pipeline completed successfully")
        print("\n== Pipeline completed successfully! ==\n")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        progress_manager.fail_stage("pipeline")
        print(f"\n== Pipeline failed: {e} ==\n")
        return 1
    
    return 0


if __name__ == "__main__":
    # Make sure the config directory exists
    if not os.path.exists("config"):
        print("Error: config directory not found. Run this script from the project root.")
        sys.exit(1)
    
    sys.exit(run_pipeline()) 