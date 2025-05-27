# Benchmarking API

The Benchmarking API provides functionality for measuring and optimizing the performance of the StoryDredge pipeline components.

## Benchmark Framework

The main class for running performance benchmarks on pipeline components.

### BenchmarkRunner

```python
from src.utils.benchmarks import BenchmarkRunner

# Create a benchmark runner for a specific component
runner = BenchmarkRunner(
    component_name="splitter",
    iterations=5,
    warmup=True
)
```

#### Parameters

- `component_name` (str): Name of the component to benchmark
- `iterations` (int, optional): Number of benchmark iterations. Default: 3
- `warmup` (bool, optional): Whether to run a warmup iteration. Default: True
- `output_dir` (str, optional): Directory to save benchmark results. Default: "benchmarks"

### Methods

#### run_benchmark

Runs a benchmark on a specified function with given inputs.

```python
results = runner.run_benchmark(
    func=my_function,
    args=args_list,
    kwargs=kwargs_dict,
    label="operation_name"
)
```

**Parameters:**
- `func` (callable): Function to benchmark
- `args` (list, optional): Positional arguments for the function
- `kwargs` (dict, optional): Keyword arguments for the function
- `label` (str, optional): Label for this benchmark operation

**Returns:**
- `dict`: Dictionary containing benchmark results:
  - `min_time`: Minimum execution time (seconds)
  - `max_time`: Maximum execution time (seconds)
  - `avg_time`: Average execution time (seconds)
  - `total_time`: Total execution time (seconds)
  - `iterations`: Number of iterations executed
  - `component`: Component name
  - `operation`: Operation label
  - `timestamp`: Benchmark timestamp

#### save_results

Saves benchmark results to a JSON file.

```python
runner.save_results(results, filename="custom_benchmark_results.json")
```

**Parameters:**
- `results` (dict): Benchmark results to save
- `filename` (str, optional): Custom filename for results

**Returns:**
- `str`: Path to the saved file

## Pipeline Benchmarks

Functions for benchmarking and analyzing the full pipeline.

### run_component_benchmark

Benchmarks a specific pipeline component or all components.

```python
from src.benchmarking.pipeline_benchmarks import run_component_benchmark

results = run_component_benchmark(
    component="cleaner",
    sample_size=3,
    iterations=5
)
```

**Parameters:**
- `component` (str): Component name ("fetcher", "cleaner", "splitter", "classifier", "formatter", or "all")
- `sample_size` (int, optional): Number of samples to use. Default: 3
- `iterations` (int, optional): Number of benchmark iterations. Default: 3

**Returns:**
- `dict`: Dictionary of benchmark results

### analyze_benchmarks

Analyzes benchmark results to identify bottlenecks.

```python
from src.benchmarking.pipeline_benchmarks import analyze_benchmarks

analysis = analyze_benchmarks(
    benchmark_file="benchmarks/latest.json",
    threshold=1.0
)
```

**Parameters:**
- `benchmark_file` (str, optional): Path to benchmark results file. If not provided, loads the latest.
- `threshold` (float, optional): Threshold ratio for identifying bottlenecks. Default: 1.0

**Returns:**
- `dict`: Analysis results including:
  - `bottlenecks`: List of detected bottlenecks
  - `component_times`: Average time per component
  - `total_pipeline_time`: Estimated total pipeline time
  - `recommendations`: Performance improvement recommendations

## Parallel Processing

The `ParallelProcessor` class provides functionality for processing newspaper issues in parallel.

### Initialization

```python
from src.pipeline.parallel_processor import ParallelProcessor

processor = ParallelProcessor(
    output_dir="output",
    checkpoint_file="checkpoint.json",
    max_workers=4
)
```

#### Parameters

- `output_dir` (str, optional): Directory for output files. Default: "output"
- `checkpoint_file` (str, optional): File to store processing checkpoints. Default: "checkpoint.json"
- `max_workers` (int, optional): Maximum number of parallel workers. Default: CPU count - 1

### Methods

#### process_batch

Processes multiple newspaper issues in parallel.

```python
results = processor.process_batch(issue_ids)
```

**Parameters:**
- `issue_ids` (list): List of archive.org issue identifiers

**Returns:**
- `dict`: Processing results with counts of successful and failed issues

#### process_issue

Processes a single newspaper issue.

```python
success = processor.process_issue(issue_id)
```

**Parameters:**
- `issue_id` (str): Archive.org identifier for the newspaper issue

**Returns:**
- `bool`: True if processing was successful, False otherwise

## Examples

### Basic Component Benchmarking

```python
from src.utils.benchmarks import BenchmarkRunner
from src.cleaner import OCRCleaner

# Create the component to benchmark
cleaner = OCRCleaner()

# Create a benchmark runner
runner = BenchmarkRunner(component_name="cleaner", iterations=5)

# Sample input
sample_text = "Sample OCR text with errers to cleaan"

# Run benchmark
results = runner.run_benchmark(
    func=cleaner.clean,
    args=[sample_text],
    label="text_cleaning"
)

print(f"Average execution time: {results['avg_time']:.4f} seconds")
```

### Running Pipeline Benchmarks

```python
from src.benchmarking.pipeline_benchmarks import run_component_benchmark, analyze_benchmarks

# Run benchmarks for all components
results = run_component_benchmark(component="all", sample_size=2, iterations=3)

# Analyze the results
analysis = analyze_benchmarks()

# Print bottlenecks
if analysis["bottlenecks"]:
    print("Performance bottlenecks:")
    for bottleneck in analysis["bottlenecks"]:
        print(f"- {bottleneck['component']}.{bottleneck['operation']}: {bottleneck['avg_execution_time']:.2f} seconds")
else:
    print("No significant bottlenecks detected")
```

### Parallel Processing Example

```python
from src.pipeline.parallel_processor import ParallelProcessor

# Create a parallel processor with 4 workers
processor = ParallelProcessor(max_workers=4)

# List of issues to process
issue_ids = [
    "sn84026749-19220101",
    "sn84026749-19220102",
    "sn84026749-19220103",
    "sn84026749-19220104",
    "sn84026749-19220105"
]

# Process issues in parallel
results = processor.process_batch(issue_ids)

print(f"Processed {results['successful']} issues successfully, {results['failed']} failed") 