"""
Logging and monitoring utilities for StoryDredge.

This module provides a centralized logging system that enables:
1. Structured logging with consistent formatting
2. Different log levels for various components
3. Performance monitoring and metrics collection
4. Log rotation and management
"""

import os
import time
import json
import logging
import logging.handlers
from pathlib import Path
from functools import wraps
from typing import Dict, Any, Optional, Callable, Union, List, Set, Tuple

from pydantic import BaseModel

# Configure base logging
DEFAULT_LOG_DIR = Path("logs")
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class StoryDredgeLogger:
    """
    Centralized logger for StoryDredge components.
    
    This class provides consistent logging across all components,
    with support for structured logging, performance tracking, and
    error reporting.
    """
    
    def __init__(
        self,
        name: str,
        log_dir: Optional[Union[str, Path]] = None,
        log_level: int = DEFAULT_LOG_LEVEL,
        log_format: str = DEFAULT_LOG_FORMAT,
        enable_file_logging: bool = True,
        enable_console_logging: bool = True,
        max_log_size_mb: int = 10,
        backup_count: int = 5,
    ):
        """
        Initialize the logger.
        
        Args:
            name: Logger name (typically the component name)
            log_dir: Directory to store log files
            log_level: Logging level (e.g., logging.INFO)
            log_format: Format string for log messages
            enable_file_logging: Whether to log to files
            enable_console_logging: Whether to log to console
            max_log_size_mb: Maximum size of log files before rotation
            backup_count: Number of backup log files to keep
        """
        self.name = name
        self.log_dir = Path(log_dir) if log_dir else DEFAULT_LOG_DIR
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        self.log_format = log_format
        self.formatter = logging.Formatter(log_format)
        self.metrics: Dict[str, Any] = {}
        
        # Create handlers
        self.handlers = []
        
        # Ensure logger doesn't have existing handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        
        # Console handler
        if enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            self.logger.addHandler(console_handler)
            self.handlers.append(console_handler)
        
        # File handler
        if enable_file_logging:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            log_file = self.log_dir / f"{name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_log_size_mb * 1024 * 1024,
                backupCount=backup_count,
            )
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)
            self.handlers.append(file_handler)
    
    def debug(self, msg: str, **kwargs):
        """Log a debug message."""
        if kwargs:
            msg = f"{msg} {json.dumps(kwargs)}"
        self.logger.debug(msg)
    
    def info(self, msg: str, **kwargs):
        """Log an info message."""
        if kwargs:
            msg = f"{msg} {json.dumps(kwargs)}"
        self.logger.info(msg)
    
    def warning(self, msg: str, **kwargs):
        """Log a warning message."""
        if kwargs:
            msg = f"{msg} {json.dumps(kwargs)}"
        self.logger.warning(msg)
    
    def error(self, msg: str, exc_info: bool = True, **kwargs):
        """Log an error message."""
        if kwargs:
            msg = f"{msg} {json.dumps(kwargs)}"
        self.logger.error(msg, exc_info=exc_info)
    
    def critical(self, msg: str, exc_info: bool = True, **kwargs):
        """Log a critical message."""
        if kwargs:
            msg = f"{msg} {json.dumps(kwargs)}"
        self.logger.critical(msg, exc_info=exc_info)
    
    def record_metric(self, name: str, value: Any):
        """
        Record a metric for monitoring.
        
        Args:
            name: Metric name
            value: Metric value
        """
        self.metrics[name] = value
        self.debug(f"Metric recorded: {name}", value=value)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all recorded metrics."""
        return self.metrics
    
    def clear_metrics(self):
        """Clear all recorded metrics."""
        self.metrics.clear()
    
    def log_dict(self, level: int, data: Dict[str, Any], msg: str = ""):
        """
        Log a dictionary at the specified level.
        
        Args:
            level: Logging level
            data: Dictionary to log
            msg: Optional message
        """
        log_msg = msg + " " + json.dumps(data) if msg else json.dumps(data)
        self.logger.log(level, log_msg)


class PerformanceTimer:
    """
    Context manager for timing code execution.
    
    Example:
        with PerformanceTimer(logger, "fetch_operation") as timer:
            # Code to time
            result = fetch_data()
            timer.add_context(items_processed=len(result))
    """
    
    def __init__(self, logger: StoryDredgeLogger, operation_name: str):
        """
        Initialize the timer.
        
        Args:
            logger: Logger instance
            operation_name: Name of the operation being timed
        """
        self.logger = logger
        self.operation_name = operation_name
        self.start_time = 0.0
        self.end_time = 0.0
        self.context: Dict[str, Any] = {}
    
    def __enter__(self):
        """Start the timer when entering context."""
        self.start_time = time.time()
        self.logger.debug(f"Started operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        End the timer when exiting context and log the result.
        
        Also logs any exceptions that occurred during execution.
        """
        self.end_time = time.time()
        duration_ms = (self.end_time - self.start_time) * 1000
        
        if exc_type:
            # Operation failed
            self.logger.error(
                f"Operation failed: {self.operation_name}",
                duration_ms=duration_ms,
                error=str(exc_val),
                **self.context
            )
        else:
            # Operation succeeded
            self.logger.info(
                f"Completed operation: {self.operation_name}",
                duration_ms=duration_ms,
                **self.context
            )
        
        # Record metric
        self.logger.record_metric(f"{self.operation_name}_duration_ms", duration_ms)
    
    def add_context(self, **kwargs):
        """
        Add context information to be included in the log.
        
        Args:
            **kwargs: Key-value pairs to add to the context
        """
        self.context.update(kwargs)


def logged_function(logger: StoryDredgeLogger, operation_name: Optional[str] = None):
    """
    Decorator for logging function calls with timing.
    
    Example:
        @logged_function(logger, "process_article")
        def process_article(article_id: str) -> Dict:
            # Implementation
    
    Args:
        logger: Logger instance
        operation_name: Optional name for the operation (defaults to function name)
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Use function name if operation_name not provided
            op_name = operation_name or func.__name__
            
            with PerformanceTimer(logger, op_name) as timer:
                # Add function arguments to context (if simple types)
                context = {}
                for i, arg in enumerate(args):
                    if isinstance(arg, (str, int, float, bool)):
                        context[f"arg{i}"] = arg
                
                for key, value in kwargs.items():
                    if isinstance(value, (str, int, float, bool)):
                        context[key] = value
                
                if context:
                    timer.add_context(**context)
                
                # Call the function
                result = func(*args, **kwargs)
                
                # Add result info to context (if simple types)
                if isinstance(result, (str, int, float, bool)):
                    timer.add_context(result=result)
                elif isinstance(result, (list, tuple, set)):
                    timer.add_context(result_length=len(result))
                elif isinstance(result, dict):
                    timer.add_context(result_length=len(result))
                
                return result
        
        return wrapper
    
    return decorator


# Create a global logger registry to access loggers by name
LOGGER_REGISTRY: Dict[str, StoryDredgeLogger] = {}


def get_logger(name: str, **kwargs) -> StoryDredgeLogger:
    """
    Get or create a logger by name.
    
    This ensures each component uses the same logger instance.
    
    Args:
        name: Logger name
        **kwargs: Parameters to pass to StoryDredgeLogger constructor
    
    Returns:
        Logger instance
    """
    if name not in LOGGER_REGISTRY:
        LOGGER_REGISTRY[name] = StoryDredgeLogger(name, **kwargs)
    
    return LOGGER_REGISTRY[name]


# Configure default loggers for main components
def configure_default_loggers(log_dir: Optional[Union[str, Path]] = None) -> None:
    """
    Configure default loggers for all main components.
    
    Args:
        log_dir: Optional custom log directory
    """
    components = [
        "fetcher", "cleaner", "splitter", "classifier", "formatter", "pipeline"
    ]
    
    for component in components:
        get_logger(component, log_dir=log_dir)
    
    # Root logger for general application logging
    get_logger("storydredge", log_dir=log_dir)


# Metrics collection
class MetricsCollector:
    """
    Collector for application-wide metrics.
    
    This class aggregates metrics from all components and
    can export them for monitoring systems.
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.metrics: Dict[str, Any] = {}
        self.start_time = time.time()
    
    def collect_from_loggers(self) -> Dict[str, Any]:
        """
        Collect metrics from all registered loggers.
        
        Returns:
            Combined metrics dictionary
        """
        for name, logger in LOGGER_REGISTRY.items():
            component_metrics = logger.get_metrics()
            for metric_name, value in component_metrics.items():
                full_name = f"{name}.{metric_name}"
                self.metrics[full_name] = value
        
        # Add uptime metric
        uptime_seconds = time.time() - self.start_time
        self.metrics["system.uptime_seconds"] = uptime_seconds
        
        return self.metrics
    
    def export_json(self, file_path: Optional[Union[str, Path]] = None) -> str:
        """
        Export metrics as JSON.
        
        Args:
            file_path: Optional file path to save metrics
        
        Returns:
            JSON string of metrics
        """
        metrics = self.collect_from_loggers()
        json_str = json.dumps(metrics, indent=2)
        
        if file_path:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(json_str)
        
        return json_str 