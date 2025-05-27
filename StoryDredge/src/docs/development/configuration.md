# Configuration Management System

This document describes the configuration management system implemented in StoryDredge. The system provides a centralized way to manage configuration across all components of the pipeline.

## Overview

The configuration management system consists of several components that work together:

1. **ConfigManager**: Central manager for loading, validating, and accessing configuration
2. **PipelineConfig**: Root configuration model that contains all settings
3. **ComponentConfig**: Base configuration model for individual pipeline components
4. **Configuration Models**: Specialized models for specific aspects (logging, progress, etc.)

## Key Features

- YAML-based configuration files
- Environment variable overrides
- Type validation using Pydantic
- Centralized configuration access
- Component-specific configurations
- Default values for all settings

## Configuration Structure

The main configuration file is located at `config/pipeline.yml` and follows this structure:

```yaml
# Global settings
parallel_processes: 4
cache_dir: "cache"
output_dir: "output"
temp_dir: "temp"

# Logging configuration
logging:
  level: "INFO"
  log_dir: "logs"
  console_logging: true
  file_logging: true
  max_log_size_mb: 10
  backup_count: 5

# Progress reporting configuration
progress:
  enabled: true
  report_interval_seconds: 0.5
  show_spinner: true
  show_progress_bar: true
  show_metrics: true
  show_eta: true
  verbose: false

# Component-specific configurations
fetcher:
  enabled: true
  debug_mode: false
  timeout_seconds: 120
  # Fetcher-specific settings
  rate_limit_requests: 10
  rate_limit_period_seconds: 60
  
cleaner:
  enabled: true
  debug_mode: false
  timeout_seconds: 300
  # Cleaner-specific settings
  normalize_whitespace: true
  
# More component configurations...
```

## Usage Examples

### Basic Configuration Access

```python
from src.utils import get_config_manager

# Get the configuration manager
config_manager = get_config_manager()

# Access the configuration
config = config_manager.config

# Use configuration values
parallel_processes = config.parallel_processes
output_dir = config.output_dir
```

### Component-Specific Configuration

```python
from src.utils import get_config_manager

# Get component-specific configuration
config_manager = get_config_manager()
fetcher_config = config_manager.get_component_config("fetcher")

# Use component-specific settings
if fetcher_config.enabled:
    timeout = fetcher_config.timeout_seconds
    rate_limit = fetcher_config.rate_limit_requests
```

### Environment Variable Overrides

Environment variables can override configuration values using the prefix `STORYDREDGE_`. For example:

```bash
# Set environment variables to override configuration
export STORYDREDGE_PARALLEL_PROCESSES=8
export STORYDREDGE_FETCHER__TIMEOUT_SECONDS=60
export STORYDREDGE_LOGGING__LEVEL="DEBUG"

# Run with overridden configuration
python pipeline/main.py
```

The double underscore (`__`) is used to specify nested configuration keys.

### Saving Configuration

```python
from src.utils import get_config_manager

# Get the configuration manager
config_manager = get_config_manager()

# Modify configuration
config_manager.config.parallel_processes = 8
config_manager.config.fetcher.timeout_seconds = 60

# Save to a new file
config_manager.save("config/custom_config.yml")
```

## Configuration Models

The system uses Pydantic models for configuration validation:

### PipelineConfig

Root configuration model that contains all settings:

```python
class PipelineConfig(BaseModel):
    # Component configurations
    fetcher: ComponentConfig
    cleaner: ComponentConfig
    splitter: ComponentConfig
    classifier: ComponentConfig
    formatter: ComponentConfig
    
    # System-wide configurations
    parallel_processes: int = 1
    cache_dir: str = "cache"
    output_dir: str = "output"
    temp_dir: str = "temp"
    
    # Specialized configurations
    logging: LoggingConfig
    progress: ProgressConfig
```

### ComponentConfig

Base configuration model for all pipeline components:

```python
class ComponentConfig(BaseModel):
    enabled: bool = True
    debug_mode: bool = False
    timeout_seconds: int = 600
    
    class Config:
        extra = "allow"  # Allow extra fields specific to components
```

### Specialized Configuration Models

Models for specific aspects of the system:

```python
class LoggingConfig(BaseModel):
    level: str = "INFO"
    log_dir: str = "logs"
    console_logging: bool = True
    file_logging: bool = True
    max_log_size_mb: int = 10
    backup_count: int = 5

class ProgressConfig(BaseModel):
    enabled: bool = True
    report_interval_seconds: float = 1.0
    show_spinner: bool = True
    show_progress_bar: bool = True
    show_metrics: bool = True
    show_eta: bool = True
    verbose: bool = False
```

## Integration with Other Systems

The configuration system integrates with other components:

### Logging System

```python
from src.utils import get_config_manager, get_logger

# Get configuration
config = get_config_manager().config
logging_config = config.logging

# Configure logger based on configuration
logger = get_logger("my_component", 
                   log_level=logging_config.level,
                   log_dir=logging_config.log_dir,
                   console_logging=logging_config.console_logging)
```

### Progress Reporting

```python
from src.utils import get_config_manager, get_progress_manager

# Get progress configuration
progress_config = get_config_manager().config.progress

# Use in progress reporting
if progress_config.enabled:
    progress_manager = get_progress_manager()
    # Configure progress reporting...
```

## Implementation Details

The configuration management system is implemented in `src/utils/config.py`. Key components:
- **ConfigManager**: Main class for configuration management
- **PipelineConfig**: Root configuration model
- **ComponentConfig**: Base component configuration
- **LoggingConfig**: Logging-specific configuration
- **ProgressConfig**: Progress reporting configuration

The system uses:
- **PyYAML** for loading YAML files
- **Pydantic** for validation and type conversion
- **Environment variables** for runtime overrides 