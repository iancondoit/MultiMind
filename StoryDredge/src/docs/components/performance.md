# Performance Optimization

This document describes the performance optimization features implemented in the StoryDredge pipeline as part of Milestone 9.

## Overview

Performance optimization is critical for processing large volumes of newspaper issues efficiently. The StoryDredge pipeline now includes comprehensive benchmarking tools and parallel processing capabilities to improve throughput and identify bottlenecks.

## Key Features

- **Benchmarking Framework**: Comprehensive tools for measuring component performance
- **Parallel Processing**: Multi-process execution for higher throughput
- **Performance Analysis**: Tools for identifying bottlenecks and optimization opportunities
- **Scalability**: Configurable processing to adapt to available resources

## Benchmarking

The benchmarking framework allows detailed measurement of each pipeline component's performance, tracking metrics such as:

- Execution time
- Memory usage
- Throughput (items processed per second)
- Component-specific performance metrics

### Usage

To run benchmarks on the pipeline components:

```python
from src.benchmarking.pipeline_benchmarks import benchmark_fetcher, benchmark_formatter, analyze_benchmarks

# Benchmark specific components
benchmark_fetcher()
benchmark_formatter()

# Analyze benchmark results
analysis = analyze_benchmarks()
```

Benchmarks can also be run directly from the command line:

```bash
python -m src.benchmarking.pipeline_benchmarks --component fetcher
python -m src.benchmarking.pipeline_benchmarks --component all
```

### Benchmark Decorators

Individual functions can be benchmarked using the provided decorators:

```python
from src.utils.benchmarks import benchmark

@benchmark("my_component", "my_operation")
def my_function():
    # Function implementation
    pass
```

## Parallel Processing

The parallel processing feature allows multiple newspaper issues to be processed simultaneously, with the following benefits:

- Higher throughput on multi-core systems
- Better resource utilization
- Resilience to individual process failures
- Checkpoint/resume capability for long-running jobs

### Usage

To use parallel processing:

```python
from src.pipeline.parallel_processor import ParallelProcessor

processor = ParallelProcessor(
    output_dir="output",
    max_workers=4  # Use 4 parallel processes
)

# Process a batch of issues
processor.process_batch(["issue1", "issue2", "issue3", "issue4"])
```

From the command line:

```bash
python pipeline/main.py --issues-file issues.json --workers 4
```

## Performance Analysis

The performance analysis tools help identify bottlenecks in the pipeline by:

- Aggregating benchmark results
- Calculating performance statistics (mean, median, standard deviation)
- Ranking components by execution time
- Generating performance reports

### Bottleneck Identification

The analysis module automatically identifies the slowest components in the pipeline:

```python
from src.benchmarking.pipeline_benchmarks import analyze_benchmarks

analysis = analyze_benchmarks()
bottlenecks = analysis.get("bottlenecks", [])

for bottleneck in bottlenecks:
    print(f"{bottleneck['component']}.{bottleneck['operation']}: {bottleneck['avg_execution_time']:.2f} seconds")
```

## Implementation Details

### Benchmarking Framework

The benchmarking framework consists of several key classes:

- `Benchmarker`: Main class for performance measurement
- `BenchmarkResult`: Container for benchmark metrics
- `BenchmarkReporter`: Handles saving and comparing benchmark results
- `PerformanceMetric`: Represents individual performance measurements

Benchmark results are saved as JSON files in the `benchmarks` directory, with a format that allows for easy analysis and comparison.

### Parallel Processor

The parallel processor uses Python's `concurrent.futures` module with a `ProcessPoolExecutor` to run multiple pipeline instances in parallel. Each worker process:

1. Initializes its own set of pipeline components
2. Processes a single newspaper issue
3. Returns results to the main process
4. Handles its own error conditions

The main process:
1. Manages the worker pool
2. Distributes work among workers
3. Collects and aggregates results
4. Handles checkpoint/resume functionality
5. Reports overall progress

## Configuration

Both the benchmarking and parallel processing features are highly configurable:

### Benchmarking Configuration

- Output directory for benchmark results
- Metrics to collect
- Number of iterations for statistical benchmarks

### Parallel Processing Configuration

- Number of worker processes
- Checkpoint file location
- Error handling behavior
- Output directory structure

## Performance Considerations

When using the parallel processing features, consider the following:

1. **CPU Resources**: The number of workers should generally not exceed the number of available CPU cores
2. **Memory Usage**: Each worker requires its own memory for pipeline components
3. **I/O Bottlenecks**: Disk and network I/O can become bottlenecks with many parallel processes
4. **External APIs**: Consider rate limits when accessing external services like archive.org

## Example

A complete example demonstrating performance optimization features is available in `examples/performance_optimization_example.py`. 