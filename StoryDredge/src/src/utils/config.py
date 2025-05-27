"""
Configuration management utilities for StoryDredge.

This module provides a centralized way to manage configuration across
all components of the pipeline, with support for:
1. Loading configuration from YAML files
2. Environment variable overrides
3. Runtime configuration changes
4. Configuration validation
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from pydantic import BaseModel, Field, ValidationError

from .logging import get_logger

logger = get_logger("utils.config")

# Default configuration paths
DEFAULT_CONFIG_DIR = Path("config")
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "pipeline.yml"

class ComponentConfig(BaseModel):
    """Base configuration model for pipeline components."""
    
    enabled: bool = True
    debug_mode: bool = False
    timeout_seconds: int = 600
    
    class Config:
        extra = "allow"  # Allow extra fields specific to components


class LoggingConfig(BaseModel):
    """Configuration for logging."""
    
    level: str = "INFO"
    log_dir: str = "logs"
    console_logging: bool = True
    file_logging: bool = True
    max_log_size_mb: int = 10
    backup_count: int = 5


class ProgressConfig(BaseModel):
    """Configuration for progress reporting."""
    
    enabled: bool = True
    report_interval_seconds: float = 1.0
    show_spinner: bool = True
    show_progress_bar: bool = True
    show_metrics: bool = True
    show_eta: bool = True
    verbose: bool = False


class PipelineConfig(BaseModel):
    """Configuration for the StoryDredge pipeline."""
    
    # Component configurations
    fetcher: ComponentConfig = Field(default_factory=ComponentConfig)
    cleaner: ComponentConfig = Field(default_factory=ComponentConfig)
    splitter: ComponentConfig = Field(default_factory=ComponentConfig)
    classifier: ComponentConfig = Field(default_factory=ComponentConfig)
    formatter: ComponentConfig = Field(default_factory=ComponentConfig)
    
    # System-wide configurations
    parallel_processes: int = 1
    cache_dir: str = "cache"
    output_dir: str = "output"
    temp_dir: str = "temp"
    
    # Logging configuration
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Progress reporting configuration
    progress: ProgressConfig = Field(default_factory=ProgressConfig)
    
    class Config:
        extra = "allow"  # Allow extra fields for future expansion


class ConfigManager:
    """
    Manager for StoryDredge configuration.
    
    Handles loading, validation, and access to configuration values.
    """
    
    def __init__(
        self,
        config_file: Optional[Union[str, Path]] = None,
        env_prefix: str = "STORYDREDGE_",
    ):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file
            env_prefix: Prefix for environment variables
        """
        self.config_file = Path(config_file) if config_file else DEFAULT_CONFIG_FILE
        self.env_prefix = env_prefix
        self.config: PipelineConfig = PipelineConfig()
        self.raw_config: Dict[str, Any] = {}
        self.is_loaded = False
    
    def load(self, reload: bool = False) -> bool:
        """
        Load configuration from file and environment variables.
        
        Args:
            reload: Whether to reload if already loaded
            
        Returns:
            True if loading succeeded, False otherwise
        """
        if self.is_loaded and not reload:
            return True
        
        try:
            # Load from file if it exists
            if self.config_file.exists():
                with open(self.config_file, "r") as f:
                    self.raw_config = yaml.safe_load(f) or {}
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                logger.warning(f"Configuration file {self.config_file} not found, using defaults")
                self.raw_config = {}
            
            # Apply environment variable overrides
            self._apply_env_overrides()
            
            # Create validated config
            self.config = PipelineConfig(**self.raw_config)
            self.is_loaded = True
            
            # Log configuration summary
            logger.info("Configuration loaded successfully")
            return True
            
        except (yaml.YAMLError, OSError) as e:
            logger.error(f"Error loading configuration: {e}")
            return False
        except ValidationError as e:
            logger.error(f"Invalid configuration: {e}")
            return False
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides to configuration."""
        overrides = {}
        
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(self.env_prefix):].lower()
                
                # Handle nested keys using double underscores
                if "__" in config_key:
                    parts = config_key.split("__")
                    current = overrides
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = self._parse_env_value(value)
                else:
                    overrides[config_key] = self._parse_env_value(value)
        
        # Update raw config with overrides
        self._update_dict_recursive(self.raw_config, overrides)
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type."""
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        elif value.isdigit():
            return int(value)
        elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
            return float(value)
        else:
            return value
    
    def _update_dict_recursive(self, target: Dict, source: Dict):
        """Recursively update a dictionary with another dictionary."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._update_dict_recursive(target[key], value)
            else:
                target[key] = value
    
    def get_component_config(self, component_name: str) -> ComponentConfig:
        """
        Get configuration for a specific component.
        
        Args:
            component_name: Name of the component
            
        Returns:
            Component configuration
        """
        if not self.is_loaded:
            self.load()
        
        if hasattr(self.config, component_name):
            return getattr(self.config, component_name)
        else:
            logger.warning(f"No configuration found for component '{component_name}', using defaults")
            return ComponentConfig()
    
    def save(self, config_file: Optional[Union[str, Path]] = None) -> bool:
        """
        Save current configuration to a file.
        
        Args:
            config_file: Path to save configuration to (uses current config_file if None)
            
        Returns:
            True if saving succeeded, False otherwise
        """
        save_path = Path(config_file) if config_file else self.config_file
        
        try:
            # Create directory if it doesn't exist
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert config to dict and save as YAML
            config_dict = self.config.dict()
            with open(save_path, "w") as f:
                yaml.dump(config_dict, f, default_flow_style=False)
            
            logger.info(f"Configuration saved to {save_path}")
            return True
        except (OSError, yaml.YAMLError) as e:
            logger.error(f"Error saving configuration: {e}")
            return False


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager(config_file: Optional[Union[str, Path]] = None) -> ConfigManager:
    """
    Get the global configuration manager instance.
    
    Args:
        config_file: Optional config file path to override the default
        
    Returns:
        ConfigManager instance
    """
    global _config_manager
    
    if _config_manager is None:
        _config_manager = ConfigManager(config_file=config_file)
        _config_manager.load()
    elif config_file is not None and Path(config_file) != _config_manager.config_file:
        _config_manager = ConfigManager(config_file=config_file)
        _config_manager.load()
    
    return _config_manager 