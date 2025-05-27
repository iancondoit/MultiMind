"""
Benchmarking Module

This module provides utilities for measuring the performance of various
components in the StoryDredge pipeline, identifying bottlenecks, and
tracking performance improvements.

Features:
- Component-level performance measurement
- Pipeline end-to-end timing
- Memory usage tracking
- Performance visualization
- Comparative benchmarking to track improvements
"""

import time
import json
import logging
import psutil
import functools
import statistics
from typing import Dict, List, Any, Callable, Optional
from pathlib import Path
from datetime import datetime


class PerformanceMetric:
    """
    Represents a single performance measurement.
    
    Attributes:
        name: Name of the metric
        value: Measured value
        unit: Unit of measurement (e.g., "seconds", "MB", "items/sec")
    """
    
    def __init__(self, name: str, value: float, unit: str):
        self.name = name
        self.value = value
        self.unit = unit
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the metric to a dictionary."""
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp
        }


class BenchmarkResult:
    """
    Contains results from a benchmark run.
    
    Attributes:
        component: Name of the component being benchmarked
        operation: Name of the operation being benchmarked
        metrics: List of performance metrics
        metadata: Additional metadata about the benchmark
    """
    
    def __init__(self, component: str, operation: str):
        self.component = component
        self.operation = operation
        self.metrics: List[PerformanceMetric] = []
        self.metadata: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "system_info": get_system_info()
        }
    
    def add_metric(self, name: str, value: float, unit: str):
        """Add a performance metric to the result."""
        self.metrics.append(PerformanceMetric(name, value, unit))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the benchmark result to a dictionary."""
        return {
            "component": self.component,
            "operation": self.operation,
            "metrics": [metric.to_dict() for metric in self.metrics],
            "metadata": self.metadata
        }


class BenchmarkReporter:
    """
    Handles saving and reporting benchmark results.
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize the reporter with an output directory.
        
        Args:
            output_dir: Directory to save benchmark results
        """
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir or Path("benchmarks")
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def save_result(self, result: BenchmarkResult):
        """
        Save a benchmark result to a JSON file.
        
        Args:
            result: The benchmark result to save
        """
        # Create a filename based on component, operation, and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{result.component}_{result.operation}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # Save the result as JSON
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2)
            
        self.logger.info(f"Benchmark result saved to {filepath}")
    
    def compare_results(self, old_result: BenchmarkResult, new_result: BenchmarkResult) -> Dict[str, Any]:
        """
        Compare two benchmark results and report the differences.
        
        Args:
            old_result: Previous benchmark result
            new_result: New benchmark result
            
        Returns:
            Dictionary with metric differences
        """
        comparison = {
            "component": new_result.component,
            "operation": new_result.operation,
            "metrics": []
        }
        
        # Create lookup of old metrics by name
        old_metrics = {metric.name: metric for metric in old_result.metrics}
        
        # Compare metrics
        for new_metric in new_result.metrics:
            if new_metric.name in old_metrics:
                old_metric = old_metrics[new_metric.name]
                if old_metric.unit != new_metric.unit:
                    self.logger.warning(
                        f"Cannot compare metrics with different units: "
                        f"{old_metric.name} ({old_metric.unit} vs {new_metric.unit})"
                    )
                    continue
                
                # Calculate difference and percent change
                diff = new_metric.value - old_metric.value
                if old_metric.value != 0:
                    pct_change = (diff / old_metric.value) * 100
                else:
                    pct_change = float('inf')
                
                comparison["metrics"].append({
                    "name": new_metric.name,
                    "old_value": old_metric.value,
                    "new_value": new_metric.value,
                    "difference": diff,
                    "percent_change": pct_change,
                    "unit": new_metric.unit
                })
        
        return comparison


class Benchmarker:
    """
    Main benchmarking class to measure component performance.
    """
    
    def __init__(self, reporter: Optional[BenchmarkReporter] = None):
        """
        Initialize the benchmarker.
        
        Args:
            reporter: Reporter to save benchmark results
        """
        self.logger = logging.getLogger(__name__)
        self.reporter = reporter or BenchmarkReporter()
        self.current_result = None
    
    def benchmark_function(self, component: str, operation: str):
        """
        Decorator to benchmark a function.
        
        Args:
            component: Name of the component
            operation: Name of the operation
            
        Returns:
            Decorated function
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Create benchmark result
                result = BenchmarkResult(component, operation)
                
                # Measure memory before
                mem_before = get_memory_usage()
                
                # Measure time
                start_time = time.time()
                func_result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                
                # Measure memory after
                mem_after = get_memory_usage()
                
                # Record metrics
                result.add_metric("execution_time", elapsed_time, "seconds")
                result.add_metric("memory_used", mem_after - mem_before, "MB")
                
                # Save result
                self.reporter.save_result(result)
                
                return func_result
            return wrapper
        return decorator
    
    def start_benchmark(self, component: str, operation: str) -> BenchmarkResult:
        """
        Start a new benchmark measurement.
        
        Args:
            component: Name of the component
            operation: Name of the operation
            
        Returns:
            The created benchmark result
        """
        self.current_result = BenchmarkResult(component, operation)
        self.start_time = time.time()
        self.start_memory = get_memory_usage()
        return self.current_result
    
    def end_benchmark(self) -> BenchmarkResult:
        """
        End the current benchmark and record metrics.
        
        Returns:
            The completed benchmark result
        """
        if not self.current_result:
            raise ValueError("No benchmark in progress. Call start_benchmark first.")
        
        # Measure time and memory
        elapsed_time = time.time() - self.start_time
        memory_used = get_memory_usage() - self.start_memory
        
        # Record metrics
        self.current_result.add_metric("execution_time", elapsed_time, "seconds")
        self.current_result.add_metric("memory_used", memory_used, "MB")
        
        # Save result
        self.reporter.save_result(self.current_result)
        
        result = self.current_result
        self.current_result = None
        return result


def benchmark(component: str, operation: str):
    """
    Decorator to benchmark a function using the default benchmarker.
    
    Args:
        component: Name of the component
        operation: Name of the operation
        
    Returns:
        Decorated function
    """
    benchmarker = Benchmarker()
    return benchmarker.benchmark_function(component, operation)


def get_system_info() -> Dict[str, Any]:
    """
    Get information about the system for benchmark context.
    
    Returns:
        Dictionary with system information
    """
    system_info = {
        "processor": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "total_memory": round(psutil.virtual_memory().total / (1024 * 1024 * 1024), 2),  # GB
        "platform": psutil.Process().cpu_affinity() if hasattr(psutil.Process(), 'cpu_affinity') else None
    }
    return system_info


def get_memory_usage() -> float:
    """
    Get the current memory usage of the process in MB.
    
    Returns:
        Memory usage in MB
    """
    process = psutil.Process()
    memory_info = process.memory_info()
    return memory_info.rss / (1024 * 1024)  # Convert to MB


def run_repeated_benchmark(
    func: Callable, 
    args: tuple = (), 
    kwargs: dict = None, 
    component: str = "unknown", 
    operation: str = "unknown", 
    iterations: int = 5
) -> BenchmarkResult:
    """
    Run a benchmark multiple times and collect statistics.
    
    Args:
        func: Function to benchmark
        args: Arguments to pass to the function
        kwargs: Keyword arguments to pass to the function
        component: Name of the component
        operation: Name of the operation
        iterations: Number of iterations to run
        
    Returns:
        Benchmark result with statistics
    """
    kwargs = kwargs or {}
    
    # Collect measurements
    execution_times = []
    memory_usages = []
    
    for i in range(iterations):
        # Measure memory before
        mem_before = get_memory_usage()
        
        # Measure time
        start_time = time.time()
        func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        # Measure memory after
        mem_after = get_memory_usage()
        
        # Record measurements
        execution_times.append(elapsed_time)
        memory_usages.append(mem_after - mem_before)
    
    # Create result with statistics
    result = BenchmarkResult(component, operation)
    
    # Add execution time statistics
    result.add_metric("mean_execution_time", statistics.mean(execution_times), "seconds")
    result.add_metric("median_execution_time", statistics.median(execution_times), "seconds")
    result.add_metric("min_execution_time", min(execution_times), "seconds")
    result.add_metric("max_execution_time", max(execution_times), "seconds")
    if len(execution_times) > 1:
        result.add_metric("stdev_execution_time", statistics.stdev(execution_times), "seconds")
    
    # Add memory usage statistics
    result.add_metric("mean_memory_used", statistics.mean(memory_usages), "MB")
    
    # Add metadata
    result.metadata["iterations"] = iterations
    
    # Save result
    reporter = BenchmarkReporter()
    reporter.save_result(result)
    
    return result 