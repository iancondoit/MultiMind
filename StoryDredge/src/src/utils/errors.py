"""
Error handling utilities for StoryDredge.

This module provides standardized error handling across all components
of the pipeline, including:
1. Custom exception classes
2. Error recovery mechanisms
3. Retry logic for transient errors
4. Error reporting and tracking
"""

import time
import functools
import traceback
from typing import Callable, TypeVar, Any, Optional, List, Dict, Union, Type
from enum import Enum, auto

from .logging import get_logger

logger = get_logger("utils.errors")

# Type variable for generic function return type
T = TypeVar('T')


class ErrorLevel(Enum):
    """Error severity levels."""
    
    INFO = auto()         # Informational errors (non-critical)
    WARNING = auto()      # Warning (non-fatal but concerning)
    ERROR = auto()        # Regular error (component failure)
    CRITICAL = auto()     # Critical error (pipeline failure)
    FATAL = auto()        # Fatal error (requires immediate shutdown)


class ErrorCategory(Enum):
    """Categories of errors for classification."""
    
    NETWORK = auto()      # Network-related errors
    IO = auto()           # File I/O errors
    PARSE = auto()        # Parsing errors
    VALIDATION = auto()   # Data validation errors
    CONFIG = auto()       # Configuration errors
    TIMEOUT = auto()      # Timeout errors
    RESOURCE = auto()     # Resource allocation errors
    EXTERNAL = auto()     # External dependency errors
    MODEL = auto()        # ML model errors
    UNKNOWN = auto()      # Unclassified errors


class StoryDredgeError(Exception):
    """
    Base exception class for all StoryDredge errors.
    
    Provides structured error information and context.
    """
    
    def __init__(
        self,
        message: str,
        level: ErrorLevel = ErrorLevel.ERROR,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        component: str = "unknown",
        original_exception: Optional[Exception] = None,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        recoverable: bool = True,
    ):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            level: Error severity level
            category: Error category
            component: Component where the error occurred
            original_exception: Original exception that caused this error
            error_code: Error code for programmatic handling
            context: Additional context about the error
            recoverable: Whether the error is potentially recoverable
        """
        self.message = message
        self.level = level
        self.category = category
        self.component = component
        self.original_exception = original_exception
        self.error_code = error_code
        self.context = context or {}
        self.recoverable = recoverable
        self.traceback = traceback.format_exc() if original_exception else None
        
        # Call parent constructor
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/serialization."""
        return {
            "message": self.message,
            "level": self.level.name,
            "category": self.category.name,
            "component": self.component,
            "original_exception": str(self.original_exception) if self.original_exception else None,
            "error_code": self.error_code,
            "context": self.context,
            "recoverable": self.recoverable,
            "traceback": self.traceback,
        }
    
    def log(self, log_traceback: bool = True):
        """Log the error with the appropriate level."""
        error_dict = self.to_dict()
        
        if log_traceback and self.traceback:
            error_dict["traceback"] = self.traceback
        
        if self.level == ErrorLevel.INFO:
            logger.info(f"Error in {self.component}: {self.message}", **error_dict)
        elif self.level == ErrorLevel.WARNING:
            logger.warning(f"Warning in {self.component}: {self.message}", **error_dict)
        elif self.level == ErrorLevel.ERROR:
            logger.error(f"Error in {self.component}: {self.message}", **error_dict)
        elif self.level == ErrorLevel.CRITICAL:
            logger.critical(f"Critical error in {self.component}: {self.message}", **error_dict)
        elif self.level == ErrorLevel.FATAL:
            logger.critical(f"Fatal error in {self.component}: {self.message}", **error_dict)


class NetworkError(StoryDredgeError):
    """Network-related errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.NETWORK, **kwargs)


class IOError(StoryDredgeError):
    """File I/O errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.IO, **kwargs)


class ParseError(StoryDredgeError):
    """Parsing errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.PARSE, **kwargs)


class ValidationError(StoryDredgeError):
    """
    Error raised when input validation fails.
    
    This error is raised when input data does not meet validation requirements,
    such as format, range, or content restrictions.
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.VALIDATION, **kwargs)


class ConfigError(StoryDredgeError):
    """Configuration errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.CONFIG, **kwargs)


class TimeoutError(StoryDredgeError):
    """Timeout errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.TIMEOUT, **kwargs)


class ResourceError(StoryDredgeError):
    """Resource allocation errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.RESOURCE, **kwargs)


class ExternalError(StoryDredgeError):
    """External dependency errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.EXTERNAL, **kwargs)


class ModelError(StoryDredgeError):
    """ML model errors."""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.MODEL, **kwargs)


class FetchError(StoryDredgeError):
    """
    Error raised when fetching resources fails.
    
    This error is raised when there is a problem fetching or downloading
    resources from external sources like archive.org.
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, category=ErrorCategory.EXTERNAL, **kwargs)


class RateLimitError(FetchError):
    """
    Error raised when rate limits are exceeded.
    
    This error is raised when an external service's rate limits are
    exceeded, indicating that requests are being made too quickly.
    """
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, **kwargs)


def retry(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
    retry_condition: Optional[Callable[[Exception], bool]] = None,
    component: str = "unknown",
):
    """
    Decorator for retrying functions that may fail with transient errors.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Initial delay between retries in seconds
        backoff_factor: Factor to increase delay after each retry
        exceptions: Exception types to catch and retry
        retry_condition: Function that returns True if the error should be retried
        component: Component name for error reporting
        
    Example:
        @retry(max_attempts=3, exceptions=[NetworkError, TimeoutError])
        def fetch_data(url):
            # Code that might have transient failures
            return requests.get(url).json()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            current_delay = delay_seconds
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    # Check if we should retry based on custom condition
                    if retry_condition and not retry_condition(e):
                        logger.warning(
                            f"Not retrying {func.__name__} after attempt {attempt}/{max_attempts} "
                            f"because retry condition returned False",
                            exception=str(e),
                            component=component,
                        )
                        break
                    
                    # Log the retry attempt
                    if attempt < max_attempts:
                        logger.warning(
                            f"Retrying {func.__name__} after attempt {attempt}/{max_attempts} "
                            f"in {current_delay:.2f} seconds",
                            exception=str(e),
                            component=component,
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(
                            f"Failed to execute {func.__name__} after {max_attempts} attempts",
                            exception=str(e),
                            component=component,
                        )
            
            # If we've reached here, all retries failed
            if isinstance(last_exception, StoryDredgeError):
                raise last_exception
            else:
                raise StoryDredgeError(
                    message=f"Failed after {max_attempts} attempts: {str(last_exception)}",
                    level=ErrorLevel.ERROR,
                    component=component,
                    original_exception=last_exception,
                )
                
        return wrapper
    
    return decorator


class ErrorHandler:
    """
    Context manager for standardized error handling.
    
    Example:
        with ErrorHandler("fetcher", recoverable=True) as handler:
            # Code that might raise exceptions
            result = fetch_data(url)
            return result
        
        if handler.has_error:
            # Handle the error
            return fallback_value
    """
    
    def __init__(
        self,
        component: str,
        recoverable: bool = True,
        error_mapping: Optional[Dict[Type[Exception], Type[StoryDredgeError]]] = None,
    ):
        """
        Initialize the error handler.
        
        Args:
            component: Component name for error reporting
            recoverable: Whether errors are considered recoverable
            error_mapping: Mapping from standard exceptions to StoryDredge exceptions
        """
        self.component = component
        self.recoverable = recoverable
        self.error_mapping = error_mapping or {}
        self.error: Optional[StoryDredgeError] = None
        self.has_error = False
    
    def __enter__(self):
        """Enter the context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit the context manager and handle any exceptions.
        
        Args:
            exc_type: Type of the exception
            exc_val: Exception instance
            exc_tb: Exception traceback
            
        Returns:
            True if the exception was handled, False otherwise
        """
        if exc_val is None:
            return False
        
        # Map the exception to a StoryDredgeError if possible
        if isinstance(exc_val, StoryDredgeError):
            self.error = exc_val
        elif exc_type in self.error_mapping:
            error_class = self.error_mapping[exc_type]
            self.error = error_class(
                message=str(exc_val),
                component=self.component,
                original_exception=exc_val,
                recoverable=self.recoverable,
            )
        else:
            self.error = StoryDredgeError(
                message=str(exc_val),
                component=self.component,
                original_exception=exc_val,
                recoverable=self.recoverable,
            )
        
        # Log the error
        self.error.log()
        self.has_error = True
        
        # Return True to suppress the exception if it's recoverable
        return self.recoverable


class ErrorTracker:
    """
    Tracks errors across pipeline components for reporting and analysis.
    
    This class keeps track of all errors that occur during pipeline execution
    and provides methods for analyzing error patterns.
    """
    
    def __init__(self):
        """Initialize the error tracker."""
        self.errors: List[StoryDredgeError] = []
        self.component_errors: Dict[str, List[StoryDredgeError]] = {}
        self.category_counts: Dict[ErrorCategory, int] = {category: 0 for category in ErrorCategory}
    
    def add_error(self, error: StoryDredgeError):
        """
        Add an error to the tracker.
        
        Args:
            error: The error to track
        """
        self.errors.append(error)
        
        # Track by component
        if error.component not in self.component_errors:
            self.component_errors[error.component] = []
        self.component_errors[error.component].append(error)
        
        # Track by category
        self.category_counts[error.category] = self.category_counts.get(error.category, 0) + 1
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get a summary of tracked errors.
        
        Returns:
            Dictionary with error statistics
        """
        return {
            "total_errors": len(self.errors),
            "error_by_component": {comp: len(errors) for comp, errors in self.component_errors.items()},
            "error_by_category": {cat.name: count for cat, count in self.category_counts.items() if count > 0},
            "recoverable_errors": sum(1 for error in self.errors if error.recoverable),
            "unrecoverable_errors": sum(1 for error in self.errors if not error.recoverable),
        }
    
    def has_fatal_errors(self) -> bool:
        """
        Check if there are any fatal errors.
        
        Returns:
            True if there are fatal errors, False otherwise
        """
        return any(error.level == ErrorLevel.FATAL for error in self.errors)
    
    def get_errors_by_component(self, component: str) -> List[StoryDredgeError]:
        """
        Get all errors for a specific component.
        
        Args:
            component: Component name
            
        Returns:
            List of errors for the component
        """
        return self.component_errors.get(component, [])
    
    def clear(self):
        """Clear all tracked errors."""
        self.errors.clear()
        self.component_errors.clear()
        self.category_counts = {category: 0 for category in ErrorCategory}


# Global error tracker instance
_error_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """
    Get the global error tracker instance.
    
    Returns:
        ErrorTracker instance
    """
    global _error_tracker
    
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    
    return _error_tracker 