#!/usr/bin/env python3
"""
Performance Optimization Example

This script demonstrates the performance optimization features implemented in
Milestone 9 of the StoryDredge project, including benchmarking and parallel processing.
"""

import os
import sys
import json
import time
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.benchmarks import Benchmarker, BenchmarkReporter, run_repeated_benchmark
from src.pipeline.batch_processor import BatchProcessor
from src.pipeline.parallel_processor import ParallelProcessor
from src.benchmarking.pipeline_benchmarks import benchmark_formatter, benchmark_classifier, analyze_benchmarks


def setup_logging():
    """Configure logging for the example."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("examples/output/performance_example.log")
        ]
    )


def create_sample_data():
    """Create sample data for benchmarking if it doesn't exist."""
    # Create output directory
    output_dir = Path("examples/output")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Create sample directories
    sample_dirs = [
        "data/samples/raw",
        "data/samples/cleaned",
        "data/samples/articles",
        "data/samples/classified",
        "examples/output/sequential",
        "examples/output/parallel",
        "benchmarks"
    ]
    
    for directory in sample_dirs:
        Path(directory).mkdir(exist_ok=True, parents=True)
    
    # Create sample article data if it doesn't exist
    sample_article_file = Path("data/samples/articles/sample_article_001.json")
    
    if not sample_article_file.exists():
        sample_article = {
            "headline": "Sample Article for Benchmarking",
            "body": "This is a sample article for benchmarking the StoryDredge pipeline. " * 50,
            "raw_text": "Raw text of the article for benchmarking purposes. " * 20,
            "source_issue": "sample-19500101",
            "source_url": "https://archive.org/details/sample-19500101",
            "date": "1950-01-01",
            "publication": "The Sample Newspaper"
        }
        
        with open(sample_article_file, "w", encoding="utf-8") as f:
            json.dump(sample_article, f, indent=2)
        
        logging.info(f"Created sample article: {sample_article_file}")
    
    # Create sample classified article data if it doesn't exist
    sample_classified_file = Path("data/samples/classified/sample_classified_001.json")
    
    if not sample_classified_file.exists():
        sample_classified = {
            "headline": "Sample Classified Article for Benchmarking",
            "body": "This is a sample classified article for benchmarking the StoryDredge pipeline. " * 50,
            "raw_text": "Raw text of the article for benchmarking purposes. " * 20,
            "source_issue": "sample-19500101",
            "source_url": "https://archive.org/details/sample-19500101",
            "date": "1950-01-01",
            "publication": "The Sample Newspaper",
            "section": "news",
            "tags": ["sample", "benchmark", "test"],
            "byline": "By Sample Author",
            "dateline": "SAMPLE CITY, Jan 1"
        }
        
        with open(sample_classified_file, "w", encoding="utf-8") as f:
            json.dump(sample_classified, f, indent=2)
        
        logging.info(f"Created sample classified article: {sample_classified_file}")
    
    # Create sample issues file
    sample_issues_file = Path("examples/output/sample_issues.json")
    
    if not sample_issues_file.exists():
        sample_issues = {
            "issues": [
                "sn84026994-19110101",
                "sn83045487-19250315",
                "sn83030214-19340520"
            ]
        }
        
        with open(sample_issues_file, "w", encoding="utf-8") as f:
            json.dump(sample_issues, f, indent=2)
        
        logging.info(f"Created sample issues file: {sample_issues_file}")


def demonstrate_function_benchmarking():
    """Demonstrate benchmarking individual functions."""
    logging.info("\n=== Function Benchmarking Example ===\n")
    
    # Create a benchmarker
    benchmarker = Benchmarker()
    
    # Define a simple function to benchmark
    def process_text(text, iterations=1000):
        """Sample function that does some text processing."""
        result = text
        for _ in range(iterations):
            result = result.replace('a', 'A').replace('e', 'E')
            result = result.upper()
            result = result.lower()
        return result
    
    # Start the benchmark
    benchmarker.start_benchmark("example", "process_text")
    
    # Run the function
    sample_text = "This is a sample text for benchmarking purposes." * 100
    process_text(sample_text)
    
    # End the benchmark
    result = benchmarker.end_benchmark()
    
    # Print results
    logging.info("Function benchmark results:")
    for metric in result.metrics:
        logging.info(f"  {metric.name}: {metric.value:.4f} {metric.unit}")
    
    # Run repeated benchmark for statistical analysis
    logging.info("\nRunning repeated benchmark for statistical analysis...")
    
    repeated_result = run_repeated_benchmark(
        process_text,
        args=(sample_text,),
        kwargs={"iterations": 500},
        component="example",
        operation="process_text_repeated",
        iterations=5
    )
    
    # Print statistical results
    logging.info("Statistical benchmark results:")
    for metric in repeated_result.metrics:
        logging.info(f"  {metric.name}: {metric.value:.4f} {metric.unit}")


def demonstrate_component_benchmarking():
    """Demonstrate benchmarking pipeline components."""
    logging.info("\n=== Component Benchmarking Example ===\n")
    
    # Benchmark formatter component
    logging.info("Benchmarking HSA Formatter component...")
    benchmark_formatter(samples=1)
    
    # Benchmark classifier component (if available)
    try:
        logging.info("Benchmarking Article Classifier component...")
        benchmark_classifier(samples=1)
    except Exception as e:
        logging.error(f"Error benchmarking classifier: {e}")
    
    # Analyze results
    logging.info("\nAnalyzing benchmark results...")
    analysis = analyze_benchmarks()
    
    if analysis and "bottlenecks" in analysis and analysis["bottlenecks"]:
        logging.info("Performance bottlenecks identified:")
        for i, bottleneck in enumerate(analysis["bottlenecks"]):
            logging.info(f"{i+1}. {bottleneck['component']}.{bottleneck['operation']}")
            logging.info(f"   Average execution time: {bottleneck['avg_execution_time']:.4f} seconds")
            logging.info(f"   Average memory used: {bottleneck['avg_memory_used']:.2f} MB")


def demonstrate_parallel_processing():
    """Compare sequential vs parallel processing performance."""
    logging.info("\n=== Parallel Processing Example ===\n")
    
    # Load sample issues
    sample_issues_file = Path("examples/output/sample_issues.json")
    if not sample_issues_file.exists():
        logging.error(f"Sample issues file not found: {sample_issues_file}")
        return
    
    with open(sample_issues_file, "r") as f:
        issues_data = json.load(f)
    
    issue_ids = issues_data.get("issues", [])
    if not issue_ids:
        logging.error("No issues found in sample issues file")
        return
    
    # Use only the first issue for this example to keep it quick
    issue_id = issue_ids[0]
    logging.info(f"Using sample issue: {issue_id}")
    
    # Sequential processing
    logging.info("\nRunning sequential processing...")
    sequential_processor = BatchProcessor(
        output_dir="examples/output/sequential",
        checkpoint_file="examples/output/sequential_checkpoint.json",
        enable_checkpointing=False
    )
    
    sequential_start = time.time()
    sequential_processor.process_issue(issue_id)
    sequential_time = time.time() - sequential_start
    
    logging.info(f"Sequential processing time: {sequential_time:.2f} seconds")
    
    # Parallel processing (just for demonstration - not actually faster for a single issue)
    logging.info("\nRunning parallel processing...")
    parallel_processor = ParallelProcessor(
        output_dir="examples/output/parallel",
        checkpoint_file="examples/output/parallel_checkpoint.json",
        max_workers=2,
        enable_checkpointing=False
    )
    
    parallel_start = time.time()
    parallel_processor.process_issue(issue_id)
    parallel_time = time.time() - parallel_start
    
    logging.info(f"Parallel processing time: {parallel_time:.2f} seconds")
    
    # Compare results
    logging.info("\nPerformance comparison:")
    logging.info(f"Sequential processing: {sequential_time:.2f} seconds")
    logging.info(f"Parallel processing: {parallel_time:.2f} seconds")
    
    if sequential_time > 0:
        comparison = (sequential_time - parallel_time) / sequential_time * 100
        if comparison > 0:
            logging.info(f"Parallel processing was {comparison:.2f}% faster")
        else:
            logging.info(f"Parallel processing was {-comparison:.2f}% slower (overhead)")
            logging.info("Note: Parallel processing is more beneficial with multiple issues")


def main():
    """Main function to run the performance optimization examples."""
    # Setup logging
    setup_logging()
    
    # Create directories and sample data
    create_sample_data()
    
    # Show a menu of examples
    print("\nStoryDredge Performance Optimization Examples:")
    print("1. Function Benchmarking")
    print("2. Component Benchmarking")
    print("3. Parallel Processing Comparison")
    print("4. Run All Examples")
    print("0. Exit")
    
    choice = input("\nSelect an example to run (0-4): ")
    
    if choice == "1":
        demonstrate_function_benchmarking()
    elif choice == "2":
        demonstrate_component_benchmarking()
    elif choice == "3":
        demonstrate_parallel_processing()
    elif choice == "4":
        demonstrate_function_benchmarking()
        demonstrate_component_benchmarking()
        demonstrate_parallel_processing()
    else:
        print("Exiting...")
        return
    
    print("\nExample completed. Check the output directory and logs for results.")


if __name__ == "__main__":
    main() 