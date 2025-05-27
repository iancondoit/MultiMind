# Error Handling System

This document describes the error handling system implemented in StoryDredge. The system provides standardized error handling across all components of the pipeline.

## Overview

The error handling system consists of several components that work together:

1. **StoryDredgeError**: Base exception class with structured error information
2. **ErrorHandler**: Context manager for standardized error handling
3. **retry**: Decorator for retrying functions that may fail with transient errors
4. **ErrorTracker**: Tracks errors across pipeline components for reporting and analysis

## Key Features

- Structured error information with categorization and severity levels
- Standardized logging for all errors
- Automatic traceback capture
- Retry logic for transient errors
- Error recovery mechanisms
- Error tracking and reporting

## Error Classification

### Error Levels

Errors are classified by severity level:

- **INFO**: Informational errors (non-critical)
- **WARNING**: Warnings (non-fatal but concerning)
- **ERROR**: Regular errors (component failure)
- **CRITICAL**: Critical errors (pipeline failure)
- **FATAL**: Fatal errors (requires immediate shutdown)

### Error Categories

Errors are also classified by category:

- **NETWORK**: Network-related errors
- **IO**: File I/O errors
- **PARSE**: Parsing errors
- **VALIDATION**: Data validation errors
- **CONFIG**: Configuration errors
- **TIMEOUT**: Timeout errors
- **RESOURCE**: Resource allocation errors
- **EXTERNAL**: External dependency errors
- **MODEL**: ML model errors
- **UNKNOWN**: Unclassified errors

## Usage Examples

### Basic Error Handling

```python
from src.utils import StoryDredgeError, ErrorCategory, ErrorLevel

def process_data(data):
    try:
        # Process data...
        if not validate_data(data):
            raise StoryDredgeError(
                message="Invalid data format",
                level=ErrorLevel.ERROR,
                category=ErrorCategory.VALIDATION,
                component="data_processor",
                context={"data_size": len(data)}
            )
        
        # Continue processing...
    except Exception as e:
        # Convert to StoryDredgeError if it's not already
        if not isinstance(e, StoryDredgeError):
            e = StoryDredgeError(
                message=str(e),
                component="data_processor",
                original_exception=e
            )
        
        # Log the error
        e.log()
        
        # Re-raise for higher-level handling
        raise
```

### Using the Error Handler Context Manager

```python
from src.utils import ErrorHandler, NetworkError, TimeoutError

def fetch_data(url):
    # Define error mappings
    error_mapping = {
        ConnectionError: NetworkError,
        TimeoutError: TimeoutError,
    }
    
    # Use context manager for error handling
    with ErrorHandler("fetcher", recoverable=True, error_mapping=error_mapping) as handler:
        # Try to fetch data
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    
    # Handle error if it occurred
    if handler.has_error:
        # Return default value or fallback
        return {"error": handler.error.message}
```

### Using the Retry Decorator

```python
from src.utils import retry, NetworkError, TimeoutError

@retry(
    max_attempts=3,
    delay_seconds=1.0,
    backoff_factor=2.0,
    exceptions=[NetworkError, TimeoutError],
    component="fetcher"
)
def fetch_data_with_retry(url):
    # This function will be retried up to 3 times if it fails
    # with network or timeout errors
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()
```

### Tracking Errors

```python
from src.utils import get_error_tracker

# Get the global error tracker
error_tracker = get_error_tracker()

# Process items with error tracking
def process_items(items):
    results = []
    
    for item in items:
        try:
            result = process_item(item)
            results.append(result)
        except StoryDredgeError as e:
            # Track the error
            error_tracker.add_error(e)
            # Continue processing other items
    
    # Get error summary
    error_summary = error_tracker.get_error_summary()
    print(f"Processed {len(results)} items with {error_summary['total_errors']} errors")
    
    # Check if there were fatal errors
    if error_tracker.has_fatal_errors():
        print("Fatal errors occurred, stopping pipeline")
        return None
    
    return results
```

## Integration with Progress Reporting

The error handling system integrates with the progress reporting system:

```python
from src.utils import ProgressContext, ErrorHandler

# Combined usage
with ProgressContext("my_stage", "Processing data...", total_items=100) as ctx:
    with ErrorHandler("my_component", recoverable=True) as err_handler:
        for i in range(100):
            try:
                # Do risky work...
                result = process_item(i)
                
                # Update progress on success
                ctx.update()
            except Exception as e:
                # ErrorHandler will catch and log this
                raise
        
        # If a non-recoverable error occurred, the stage will be marked as failed
        # otherwise it will be marked as completed
```

## Custom Exception Types

The system provides several specialized exception types:

- **NetworkError**: Network-related errors
- **IOError**: File I/O errors
- **ParseError**: Parsing errors
- **ValidationError**: Data validation errors
- **ConfigError**: Configuration errors
- **TimeoutError**: Timeout errors
- **ResourceError**: Resource allocation errors
- **ExternalError**: External dependency errors
- **ModelError**: ML model errors

Example usage:

```python
from src.utils import NetworkError, ValidationError

# Raise network error
raise NetworkError(
    message="Failed to connect to server",
    component="fetcher",
    context={"url": "https://example.com"},
    recoverable=True,
)

# Raise validation error
raise ValidationError(
    message="Invalid schema",
    component="validator",
    error_code="SCHEMA_001",
    context={"schema_version": "1.0"},
)
```

## Implementation Details

The error handling system is implemented in `src/utils/errors.py`. Key components:

- **ErrorLevel**: Enum for error severity
- **ErrorCategory**: Enum for error categorization
- **StoryDredgeError**: Base exception class
- **Specialized Error Classes**: NetworkError, IOError, etc.
- **retry**: Decorator for retrying functions
- **ErrorHandler**: Context manager for error handling
- **ErrorTracker**: Tracks errors across components 