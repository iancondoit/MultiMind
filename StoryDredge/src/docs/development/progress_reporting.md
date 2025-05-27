# Progress Reporting System

This document describes the progress reporting system implemented in StoryDredge. The system provides real-time feedback during pipeline execution with visual indicators in the terminal.

## Overview

The progress reporting system consists of several components that work together:

1. **ProgressStage**: Represents a specific stage in the pipeline with its own progress tracking
2. **ProgressManager**: Manages multiple stages and handles display updates
3. **ProgressContext**: Context manager for easily tracking progress in a function
4. **track_progress**: Decorator for adding progress tracking to functions

## Key Features

- Real-time progress updates in the terminal
- Progress bars with percentage completion
- Animated spinners for active tasks
- Hierarchy of stages with weighted overall progress
- Metrics display for component-specific information
- ETA calculation and display
- Thread-safe operation for parallel processing

## Configuration

Progress reporting can be configured in `config/pipeline.yml`:

```yaml
# Progress reporting configuration
progress:
  enabled: true                 # Enable/disable the entire system
  report_interval_seconds: 0.2  # How often to update the display
  show_spinner: true            # Show spinner animation
  show_progress_bar: true       # Show progress bars
  show_metrics: true            # Show metrics
  show_eta: true                # Show estimated time remaining
  verbose: false                # Show more detailed information
```

## Usage Examples

### Basic Usage with Context Manager

```python
from src.utils import ProgressContext

# Create and use a progress context
with ProgressContext("my_stage", "Processing data...", total_items=100) as ctx:
    for i in range(100):
        # Do some work...
        
        # Update progress
        ctx.update()
        
        # Optionally add metrics
        ctx.add_metric("processed_size", f"{i * 10} KB")
```

### Using the Decorator

```python
from src.utils import track_progress

@track_progress("fetch_data", "Fetching data from API", total_items=10)
def fetch_data(api_url, context):
    results = []
    for i in range(10):
        # Fetch data...
        data = api.get(f"{api_url}/{i}")
        results.append(data)
        
        # Update progress
        context.update()
        
        # Add metrics
        context.add_metric("last_item", f"item_{i}")
    
    return results
```

### Manual Stage Management

```python
from src.utils import get_progress_manager

# Get the progress manager
progress_manager = get_progress_manager()

# Create a stage
stage = progress_manager.create_stage(
    name="data_processing",
    description="Processing large dataset",
    total_items=1000,
    weight=2.0  # This stage counts double in overall progress
)

# Start the stage
progress_manager.start_stage("data_processing")

# Update progress periodically
for i in range(1000):
    # Do work...
    
    # Update progress
    progress_manager.update_progress("data_processing")
    
    # Add metrics
    if i % 100 == 0:
        progress_manager.add_metric("data_processing", "items_per_second", i / elapsed_time)

# Complete the stage
progress_manager.complete_stage("data_processing")
```

### Hierarchical Stages

```python
# Create parent stage
parent_stage = progress_manager.create_stage(
    name="pipeline",
    description="Processing pipeline"
)
progress_manager.start_stage("pipeline")

# Create child stages with parent reference
child1 = progress_manager.create_stage(
    name="stage1",
    description="Stage 1",
    total_items=100,
    parent="pipeline"
)
progress_manager.start_stage("stage1")

# Process stage 1...
progress_manager.complete_stage("stage1")

# Create and process another child stage
child2 = progress_manager.create_stage(
    name="stage2",
    description="Stage 2",
    total_items=50,
    parent="pipeline"
)
progress_manager.start_stage("stage2")

# Process stage 2...
progress_manager.complete_stage("stage2")

# Complete parent
progress_manager.complete_stage("pipeline")
```

## Integration with Error Handling

The progress reporting system integrates with the error handling system:

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

## Demonstration

To see the progress reporting system in action, run the example script:

```bash
python examples/progress_demo.py
```

## Implementation Details

The progress reporting system is implemented in `src/utils/progress.py`. Key components:

- **StageStatus**: Enum for tracking stage state (PENDING, RUNNING, COMPLETED, etc.)
- **ProgressStage**: Core class representing a pipeline stage
- **ProgressManager**: Manages stages and handles terminal output
- **ProgressContext**: Context manager for stage tracking
- **track_progress**: Decorator for applying progress tracking to functions

The system uses threading for concurrent progress updates and is designed to be thread-safe for use in parallel processing environments. 