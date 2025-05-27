#!/usr/bin/env python3
"""
Pipeline Benchmarking

This script runs benchmarks on the StoryDredge pipeline components to identify
performance bottlenecks and areas for optimization.

Usage:
    python -m src.benchmarking.pipeline_benchmarks --component all
    python -m src.benchmarking.pipeline_benchmarks --component fetcher
    python -m src.benchmarking.pipeline_benchmarks --component cleaner
"""

import os
import sys
import time
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

from src.utils.benchmarks import Benchmarker, BenchmarkReporter, run_repeated_benchmark
from src.utils.progress import ProgressReporter

# Import pipeline components
from src.fetcher.archive_fetcher import ArchiveFetcher
from src.cleaner.ocr_cleaner import OCRCleaner
from src.splitter.article_splitter import ArticleSplitter
from src.classifier.article_classifier import ArticleClassifier
from src.formatter.hsa_formatter import HSAFormatter
from src.pipeline.batch_processor import BatchProcessor


def setup_logging():
    """Configure logging for benchmarks."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "benchmarks.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def benchmark_fetcher(samples: int = 3):
    """Benchmark the Archive Fetcher component."""
    logging.info("Benchmarking Archive Fetcher...")
    
    # Sample archive IDs for testing
    # These should be replaced with real newspaper issue IDs from your dataset
    sample_ids = [
        "sn84026994-19110101",  # Example ID 1
        "sn83045487-19250315",  # Example ID 2
        "sn83030214-19340520",  # Example ID 3
    ]
    
    # Initialize components
    fetcher = ArchiveFetcher()
    benchmarker = Benchmarker()
    
    # Ensure we only use available samples
    sample_count = min(samples, len(sample_ids))
    test_samples = sample_ids[:sample_count]
    
    logging.info(f"Testing {sample_count} samples: {test_samples}")
    
    # Benchmark fetch_issue for each sample
    for issue_id in test_samples:
        # Start benchmark
        result = benchmarker.start_benchmark("fetcher", f"fetch_issue_{issue_id}")
        
        try:
            # Fetch the issue
            fetcher.fetch_issue(issue_id)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking fetch_issue for {issue_id}: {e}")
    
    # Benchmark fetch_metadata for each sample
    for issue_id in test_samples:
        # Start benchmark
        result = benchmarker.start_benchmark("fetcher", f"fetch_metadata_{issue_id}")
        
        try:
            # Fetch metadata
            fetcher.fetch_metadata(issue_id)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking fetch_metadata for {issue_id}: {e}")
    
    logging.info("Archive Fetcher benchmarking completed")


def benchmark_cleaner(samples: int = 3):
    """Benchmark the OCR Cleaner component."""
    logging.info("Benchmarking OCR Cleaner...")
    
    # Initialize components
    cleaner = OCRCleaner()
    benchmarker = Benchmarker()
    
    # Find sample raw OCR files
    sample_dir = Path("data/samples/raw")
    if not sample_dir.exists():
        logging.error(f"Sample directory {sample_dir} does not exist")
        return
    
    sample_files = list(sample_dir.glob("*.txt"))
    if not sample_files:
        logging.error(f"No sample files found in {sample_dir}")
        return
    
    # Ensure we only use available samples
    sample_count = min(samples, len(sample_files))
    test_samples = sample_files[:sample_count]
    
    logging.info(f"Testing {sample_count} samples: {[f.name for f in test_samples]}")
    
    # Benchmark clean_text for each sample
    for sample_file in test_samples:
        # Read the sample file
        with open(sample_file, "r", encoding="utf-8") as f:
            raw_text = f.read()
        
        # Start benchmark
        result = benchmarker.start_benchmark("cleaner", f"clean_text_{sample_file.name}")
        
        try:
            # Clean the text
            cleaner.clean_text(raw_text)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking clean_text for {sample_file.name}: {e}")
    
    logging.info("OCR Cleaner benchmarking completed")


def benchmark_splitter(samples: int = 3):
    """Benchmark the Article Splitter component."""
    logging.info("Benchmarking Article Splitter...")
    
    # Initialize components
    splitter = ArticleSplitter()
    benchmarker = Benchmarker()
    
    # Find sample cleaned OCR files
    sample_dir = Path("data/samples/cleaned")
    if not sample_dir.exists():
        logging.error(f"Sample directory {sample_dir} does not exist")
        return
    
    sample_files = list(sample_dir.glob("*.txt"))
    if not sample_files:
        logging.error(f"No sample files found in {sample_dir}")
        return
    
    # Ensure we only use available samples
    sample_count = min(samples, len(sample_files))
    test_samples = sample_files[:sample_count]
    
    logging.info(f"Testing {sample_count} samples: {[f.name for f in test_samples]}")
    
    # Benchmark split_articles for each sample
    for sample_file in test_samples:
        # Read the sample file
        with open(sample_file, "r", encoding="utf-8") as f:
            cleaned_text = f.read()
        
        # Start benchmark
        result = benchmarker.start_benchmark("splitter", f"split_articles_{sample_file.name}")
        
        try:
            # Split the articles
            splitter.split_articles(cleaned_text)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking split_articles for {sample_file.name}: {e}")
    
    # Also benchmark with aggressive mode
    for sample_file in test_samples:
        # Read the sample file
        with open(sample_file, "r", encoding="utf-8") as f:
            cleaned_text = f.read()
        
        # Start benchmark
        result = benchmarker.start_benchmark("splitter", f"split_articles_aggressive_{sample_file.name}")
        
        try:
            # Split the articles with aggressive mode
            splitter.split_articles(cleaned_text, aggressive=True)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking split_articles (aggressive) for {sample_file.name}: {e}")
    
    logging.info("Article Splitter benchmarking completed")


def benchmark_classifier(samples: int = 3):
    """Benchmark the Article Classifier component."""
    logging.info("Benchmarking Article Classifier...")
    
    # Initialize components
    classifier = ArticleClassifier()
    benchmarker = Benchmarker()
    
    # Find sample article files
    sample_dir = Path("data/samples/articles")
    if not sample_dir.exists():
        logging.error(f"Sample directory {sample_dir} does not exist")
        return
    
    sample_files = list(sample_dir.glob("*.json"))
    if not sample_files:
        logging.error(f"No sample files found in {sample_dir}")
        return
    
    # Ensure we only use available samples
    sample_count = min(samples, len(sample_files))
    test_samples = sample_files[:sample_count]
    
    logging.info(f"Testing {sample_count} samples: {[f.name for f in test_samples]}")
    
    # Benchmark classify_article for each sample
    for sample_file in test_samples:
        # Read the sample file
        with open(sample_file, "r", encoding="utf-8") as f:
            article = json.load(f)
        
        # Start benchmark
        result = benchmarker.start_benchmark("classifier", f"classify_article_{sample_file.name}")
        
        try:
            # Classify the article
            classifier.classify_article(article)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking classify_article for {sample_file.name}: {e}")
    
    # Benchmark batch processing of articles
    if sample_count > 1:
        # Load all sample articles
        articles = []
        for sample_file in test_samples:
            with open(sample_file, "r", encoding="utf-8") as f:
                articles.append(json.load(f))
        
        # Start benchmark
        result = benchmarker.start_benchmark("classifier", "classify_batch")
        
        try:
            # Classify the batch of articles
            classifier.classify_batch(articles)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking classify_batch: {e}")
    
    logging.info("Article Classifier benchmarking completed")


def benchmark_formatter(samples: int = 3):
    """Benchmark the HSA Formatter component."""
    logging.info("Benchmarking HSA Formatter...")
    
    # Initialize components
    formatter = HSAFormatter(output_dir=Path("benchmarks/formatter_output"))
    benchmarker = Benchmarker()
    
    # Find sample classified article files
    sample_dir = Path("data/samples/classified")
    if not sample_dir.exists():
        logging.error(f"Sample directory {sample_dir} does not exist")
        return
    
    sample_files = list(sample_dir.glob("*.json"))
    if not sample_files:
        logging.error(f"No sample files found in {sample_dir}")
        return
    
    # Ensure we only use available samples
    sample_count = min(samples, len(sample_files))
    test_samples = sample_files[:sample_count]
    
    logging.info(f"Testing {sample_count} samples: {[f.name for f in test_samples]}")
    
    # Benchmark format_article for each sample
    for sample_file in test_samples:
        # Read the sample file
        with open(sample_file, "r", encoding="utf-8") as f:
            article = json.load(f)
        
        # Start benchmark
        result = benchmarker.start_benchmark("formatter", f"format_article_{sample_file.name}")
        
        try:
            # Format the article
            formatter.format_article(article)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking format_article for {sample_file.name}: {e}")
    
    # Benchmark save_article for each sample
    for sample_file in test_samples:
        # Read the sample file
        with open(sample_file, "r", encoding="utf-8") as f:
            article = json.load(f)
        
        # Start benchmark
        result = benchmarker.start_benchmark("formatter", f"save_article_{sample_file.name}")
        
        try:
            # Save the article
            formatter.save_article(article)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking save_article for {sample_file.name}: {e}")
    
    # Benchmark batch processing of articles
    if sample_count > 1:
        # Load all sample articles
        articles = []
        for sample_file in test_samples:
            with open(sample_file, "r", encoding="utf-8") as f:
                articles.append(json.load(f))
        
        # Start benchmark
        result = benchmarker.start_benchmark("formatter", "process_batch")
        
        try:
            # Process the batch of articles
            formatter.process_batch(articles)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking process_batch: {e}")
    
    logging.info("HSA Formatter benchmarking completed")


def benchmark_pipeline(samples: int = 1):
    """Benchmark the complete pipeline."""
    logging.info("Benchmarking complete pipeline...")
    
    # Initialize the batch processor
    batch_processor = BatchProcessor(
        output_dir="benchmarks/pipeline_output",
        checkpoint_file="benchmarks/pipeline_checkpoint.json",
        enable_checkpointing=False
    )
    benchmarker = Benchmarker()
    
    # Sample archive IDs for testing
    # These should be replaced with real newspaper issue IDs from your dataset
    sample_ids = [
        "sn84026994-19110101",  # Example ID 1
        "sn83045487-19250315",  # Example ID 2
        "sn83030214-19340520",  # Example ID 3
    ]
    
    # Ensure we only use available samples
    sample_count = min(samples, len(sample_ids))
    test_samples = sample_ids[:sample_count]
    
    logging.info(f"Testing {sample_count} samples: {test_samples}")
    
    # Benchmark individual issue processing
    for issue_id in test_samples:
        # Start benchmark
        result = benchmarker.start_benchmark("pipeline", f"process_issue_{issue_id}")
        
        try:
            # Process the issue
            batch_processor.process_issue(issue_id)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking process_issue for {issue_id}: {e}")
    
    # Benchmark batch processing
    if sample_count > 1:
        # Start benchmark
        result = benchmarker.start_benchmark("pipeline", "process_batch")
        
        try:
            # Process the batch of issues
            batch_processor.process_batch(test_samples)
            
            # End benchmark and save result
            benchmarker.end_benchmark()
            
        except Exception as e:
            logging.error(f"Error benchmarking process_batch: {e}")
    
    logging.info("Complete pipeline benchmarking completed")


def analyze_benchmarks():
    """Analyze benchmark results and identify bottlenecks."""
    logging.info("Analyzing benchmark results...")
    
    # Initialize the benchmark reporter
    reporter = BenchmarkReporter()
    benchmark_dir = Path("benchmarks")
    
    if not benchmark_dir.exists():
        logging.error("No benchmark results found")
        return
    
    # Find all benchmark result files
    result_files = list(benchmark_dir.glob("*.json"))
    
    if not result_files:
        logging.error("No benchmark result files found")
        return
    
    logging.info(f"Found {len(result_files)} benchmark result files")
    
    # Aggregate results by component and operation
    component_results = {}
    
    for result_file in result_files:
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                result_data = json.load(f)
            
            component = result_data.get("component")
            operation = result_data.get("operation")
            
            if not component or not operation:
                continue
            
            # Initialize component if not already in results
            if component not in component_results:
                component_results[component] = {}
            
            # Initialize operation if not already in component results
            if operation not in component_results[component]:
                component_results[component][operation] = []
            
            # Add result to operation results
            component_results[component][operation].append(result_data)
            
        except Exception as e:
            logging.error(f"Error processing benchmark result file {result_file}: {e}")
    
    # Calculate average metrics for each component and operation
    averages = {}
    
    for component, operations in component_results.items():
        averages[component] = {}
        
        for operation, results in operations.items():
            # Extract execution times from all results
            execution_times = []
            memory_usages = []
            
            for result in results:
                for metric in result.get("metrics", []):
                    if metric.get("name") == "execution_time":
                        execution_times.append(metric.get("value", 0))
                    elif metric.get("name") == "memory_used":
                        memory_usages.append(metric.get("value", 0))
            
            # Calculate averages
            if execution_times:
                avg_time = sum(execution_times) / len(execution_times)
            else:
                avg_time = 0
            
            if memory_usages:
                avg_memory = sum(memory_usages) / len(memory_usages)
            else:
                avg_memory = 0
            
            # Store averages
            averages[component][operation] = {
                "avg_execution_time": avg_time,
                "avg_memory_used": avg_memory,
                "sample_count": len(results)
            }
    
    # Identify bottlenecks
    bottlenecks = []
    
    # Find operations with highest average execution times
    all_operations = []
    
    for component, operations in averages.items():
        for operation, metrics in operations.items():
            all_operations.append({
                "component": component,
                "operation": operation,
                "avg_execution_time": metrics["avg_execution_time"],
                "avg_memory_used": metrics["avg_memory_used"],
                "sample_count": metrics["sample_count"]
            })
    
    # Sort operations by average execution time (descending)
    all_operations.sort(key=lambda x: x["avg_execution_time"], reverse=True)
    
    # Top 5 slowest operations are considered bottlenecks
    bottlenecks = all_operations[:5]
    
    # Print bottleneck analysis
    logging.info("Performance Bottleneck Analysis:")
    
    if bottlenecks:
        for i, bottleneck in enumerate(bottlenecks):
            logging.info(f"{i+1}. {bottleneck['component']}.{bottleneck['operation']}")
            logging.info(f"   Average execution time: {bottleneck['avg_execution_time']:.4f} seconds")
            logging.info(f"   Average memory used: {bottleneck['avg_memory_used']:.2f} MB")
            logging.info(f"   Sample count: {bottleneck['sample_count']}")
    else:
        logging.info("No bottlenecks identified")
    
    # Save analysis results
    analysis_path = benchmark_dir / "analysis_results.json"
    
    analysis_results = {
        "component_averages": averages,
        "bottlenecks": bottlenecks,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2)
    
    logging.info(f"Analysis results saved to {analysis_path}")
    
    return analysis_results


def main():
    """Main entry point for the pipeline benchmarking script."""
    parser = argparse.ArgumentParser(description="StoryDredge Pipeline Benchmarking")
    parser.add_argument("--component", choices=["fetcher", "cleaner", "splitter", "classifier", "formatter", "pipeline", "analyze", "all"], 
                        default="all", help="Component to benchmark")
    parser.add_argument("--samples", type=int, default=3, help="Number of samples to test")
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Create benchmark directory
    benchmark_dir = Path("benchmarks")
    benchmark_dir.mkdir(exist_ok=True, parents=True)
    
    # Run benchmarks based on component
    if args.component in ["fetcher", "all"]:
        benchmark_fetcher(args.samples)
    
    if args.component in ["cleaner", "all"]:
        benchmark_cleaner(args.samples)
    
    if args.component in ["splitter", "all"]:
        benchmark_splitter(args.samples)
    
    if args.component in ["classifier", "all"]:
        benchmark_classifier(args.samples)
    
    if args.component in ["formatter", "all"]:
        benchmark_formatter(args.samples)
    
    if args.component in ["pipeline", "all"]:
        benchmark_pipeline(max(1, args.samples // 3))  # Reduce samples for full pipeline
    
    if args.component in ["analyze", "all"]:
        analyze_benchmarks()
    
    logging.info("Pipeline benchmarking completed")


if __name__ == "__main__":
    main() 