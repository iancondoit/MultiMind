"""
Progress reporting utilities for StoryDredge.

This module provides tools for reporting pipeline progress in the terminal,
including:
1. Progress bars
2. Spinners
3. Status updates
4. ETA calculations
5. Pipeline stage tracking
"""

import os
import sys
import time
import functools
import threading
from enum import Enum, auto
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple

from .logging import get_logger
from .config import get_config_manager

logger = get_logger("utils.progress")


class StageStatus(Enum):
    """Status of a pipeline stage."""
    
    PENDING = auto()      # Stage not started yet
    RUNNING = auto()      # Stage is currently running
    COMPLETED = auto()    # Stage completed successfully
    FAILED = auto()       # Stage failed
    SKIPPED = auto()      # Stage was skipped


class ProgressStage:
    """
    Represents a stage in the pipeline with progress tracking.
    
    Each pipeline component may have one or more stages that are
    tracked individually.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        total_items: int = 0,
        weight: float = 1.0,
        parent: Optional['ProgressStage'] = None,
    ):
        """
        Initialize a progress stage.
        
        Args:
            name: Stage name (machine-friendly identifier)
            description: Human-readable description
            total_items: Total number of items to process
            weight: Weight of this stage in overall progress calculation
            parent: Parent stage (for hierarchical stages)
        """
        self.name = name
        self.description = description
        self.total_items = total_items
        self.processed_items = 0
        self.weight = weight
        self.parent = parent
        self.status = StageStatus.PENDING
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.children: List[ProgressStage] = []
        self.metrics: Dict[str, Any] = {}
        
        # Register as child of parent if provided
        if parent:
            parent.add_child(self)
    
    def add_child(self, child: 'ProgressStage'):
        """Add a child stage."""
        self.children.append(child)
    
    def start(self):
        """Mark the stage as started."""
        self.start_time = time.time()
        self.status = StageStatus.RUNNING
        logger.info(f"Started progress stage: {self.name}")
    
    def complete(self):
        """Mark the stage as completed."""
        self.end_time = time.time()
        self.status = StageStatus.COMPLETED
        logger.info(f"Completed progress stage: {self.name}")
    
    def fail(self):
        """Mark the stage as failed."""
        self.end_time = time.time()
        self.status = StageStatus.FAILED
        logger.error(f"Failed progress stage: {self.name}")
    
    def skip(self):
        """Mark the stage as skipped."""
        self.status = StageStatus.SKIPPED
        logger.info(f"Skipped progress stage: {self.name}")
    
    def update(self, items_processed: int = 1):
        """
        Update progress by incrementing processed items.
        
        Args:
            items_processed: Number of items processed in this update
        """
        self.processed_items += items_processed
        
        # Ensure we don't exceed total
        if self.total_items > 0 and self.processed_items > self.total_items:
            self.processed_items = self.total_items
    
    def set_progress(self, items_processed: int):
        """
        Set absolute progress value.
        
        Args:
            items_processed: Total number of items processed so far
        """
        self.processed_items = items_processed
        
        # Ensure we don't exceed total
        if self.total_items > 0 and self.processed_items > self.total_items:
            self.processed_items = self.total_items
    
    def get_progress_percentage(self) -> float:
        """
        Get progress as a percentage.
        
        Returns:
            Progress percentage (0-100)
        """
        if self.total_items <= 0:
            return 0.0 if self.status == StageStatus.PENDING else 100.0
        
        return min(100.0, (self.processed_items / self.total_items) * 100.0)
    
    def get_elapsed_time(self) -> float:
        """
        Get elapsed time in seconds.
        
        Returns:
            Elapsed time or 0 if not started
        """
        if not self.start_time:
            return 0.0
        
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def get_eta(self) -> Optional[float]:
        """
        Get estimated time remaining in seconds.
        
        Returns:
            Estimated time remaining or None if not applicable
        """
        if (
            self.status != StageStatus.RUNNING 
            or not self.start_time 
            or self.total_items <= 0 
            or self.processed_items <= 0
        ):
            return None
        
        elapsed = time.time() - self.start_time
        items_per_second = self.processed_items / elapsed
        
        if items_per_second <= 0:
            return None
        
        remaining_items = self.total_items - self.processed_items
        return remaining_items / items_per_second
    
    def add_metric(self, name: str, value: Any):
        """
        Add a metric to the stage.
        
        Args:
            name: Metric name
            value: Metric value
        """
        self.metrics[name] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert stage to dictionary for serialization.
        
        Returns:
            Dictionary representation of the stage
        """
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.name,
            "total_items": self.total_items,
            "processed_items": self.processed_items,
            "progress_percentage": self.get_progress_percentage(),
            "elapsed_seconds": self.get_elapsed_time(),
            "eta_seconds": self.get_eta(),
            "metrics": self.metrics,
            "children": [child.to_dict() for child in self.children],
        }


class ProgressManager:
    """
    Manager for tracking progress across multiple pipeline stages.
    
    This class maintains the state of all progress stages and provides
    methods for updating and reporting progress.
    """
    
    def __init__(self):
        """Initialize the progress manager."""
        self.stages: Dict[str, ProgressStage] = {}
        self.active_stages: Set[str] = set()
        self.current_display_stage: Optional[str] = None
        self.last_update_time = 0.0
        self.config = get_config_manager().config.progress
        self.update_interval = self.config.report_interval_seconds
        self._lock = threading.RLock()
        self._spinner_thread: Optional[threading.Thread] = None
        self._spinner_active = False
        self._spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self._spinner_idx = 0
    
    def create_stage(
        self,
        name: str,
        description: str,
        total_items: int = 0,
        weight: float = 1.0,
        parent: Optional[str] = None,
    ) -> ProgressStage:
        """
        Create a new progress stage.
        
        Args:
            name: Stage name
            description: Stage description
            total_items: Total items to process
            weight: Stage weight
            parent: Parent stage name
            
        Returns:
            Created ProgressStage instance
        """
        with self._lock:
            parent_stage = self.stages.get(parent) if parent else None
            
            stage = ProgressStage(
                name=name,
                description=description,
                total_items=total_items,
                weight=weight,
                parent=parent_stage,
            )
            
            self.stages[name] = stage
            logger.debug(f"Created progress stage: {name}")
            return stage
    
    def start_stage(self, name: str):
        """
        Start a progress stage.
        
        Args:
            name: Stage name
        """
        with self._lock:
            if name not in self.stages:
                logger.warning(f"Attempted to start unknown stage: {name}")
                return
            
            stage = self.stages[name]
            stage.start()
            self.active_stages.add(name)
            
            # If no stage is currently displayed, use this one
            if self.current_display_stage is None:
                self.current_display_stage = name
                self._start_spinner_if_needed()
            
            # Force an update to show the new stage
            self._update_display()
    
    def complete_stage(self, name: str):
        """
        Mark a stage as completed.
        
        Args:
            name: Stage name
        """
        with self._lock:
            if name not in self.stages:
                logger.warning(f"Attempted to complete unknown stage: {name}")
                return
            
            stage = self.stages[name]
            stage.complete()
            self.active_stages.discard(name)
            
            # If this was the displayed stage, find another one
            if self.current_display_stage == name:
                self.current_display_stage = next(iter(self.active_stages)) if self.active_stages else None
                self._update_display()
                
                if self.current_display_stage is None:
                    self._stop_spinner()
    
    def fail_stage(self, name: str):
        """
        Mark a stage as failed.
        
        Args:
            name: Stage name
        """
        with self._lock:
            if name not in self.stages:
                logger.warning(f"Attempted to fail unknown stage: {name}")
                return
            
            stage = self.stages[name]
            stage.fail()
            self.active_stages.discard(name)
            
            # If this was the displayed stage, find another one
            if self.current_display_stage == name:
                self.current_display_stage = next(iter(self.active_stages)) if self.active_stages else None
                self._update_display()
                
                if self.current_display_stage is None:
                    self._stop_spinner()
    
    def skip_stage(self, name: str):
        """
        Mark a stage as skipped.
        
        Args:
            name: Stage name
        """
        with self._lock:
            if name not in self.stages:
                logger.warning(f"Attempted to skip unknown stage: {name}")
                return
            
            stage = self.stages[name]
            stage.skip()
    
    def update_progress(self, name: str, items_processed: int = 1):
        """
        Update progress for a stage.
        
        Args:
            name: Stage name
            items_processed: Number of items processed
        """
        with self._lock:
            if name not in self.stages:
                logger.warning(f"Attempted to update unknown stage: {name}")
                return
            
            stage = self.stages[name]
            stage.update(items_processed)
            
            # Check if it's time to update the display
            now = time.time()
            if now - self.last_update_time >= self.update_interval:
                self._update_display()
                self.last_update_time = now
    
    def set_progress(self, name: str, items_processed: int):
        """
        Set absolute progress for a stage.
        
        Args:
            name: Stage name
            items_processed: Total number of items processed
        """
        with self._lock:
            if name not in self.stages:
                logger.warning(f"Attempted to set progress for unknown stage: {name}")
                return
            
            stage = self.stages[name]
            stage.set_progress(items_processed)
            
            # Check if it's time to update the display
            now = time.time()
            if now - self.last_update_time >= self.update_interval:
                self._update_display()
                self.last_update_time = now
    
    def add_metric(self, name: str, metric_name: str, value: Any):
        """
        Add a metric to a stage.
        
        Args:
            name: Stage name
            metric_name: Metric name
            value: Metric value
        """
        with self._lock:
            if name not in self.stages:
                logger.warning(f"Attempted to add metric for unknown stage: {name}")
                return
            
            stage = self.stages[name]
            stage.add_metric(metric_name, value)
    
    def get_stage(self, name: str) -> Optional[ProgressStage]:
        """
        Get a stage by name.
        
        Args:
            name: Stage name
            
        Returns:
            ProgressStage if found, None otherwise
        """
        return self.stages.get(name)
    
    def get_overall_progress(self) -> float:
        """
        Calculate overall pipeline progress.
        
        Returns:
            Progress percentage (0-100)
        """
        if not self.stages:
            return 0.0
        
        # Calculate weighted progress
        total_weight = sum(stage.weight for stage in self.stages.values())
        if total_weight <= 0:
            return 0.0
        
        weighted_progress = sum(
            stage.get_progress_percentage() * stage.weight
            for stage in self.stages.values()
        )
        
        return weighted_progress / total_weight
    
    def get_active_stages(self) -> List[ProgressStage]:
        """
        Get all currently active stages.
        
        Returns:
            List of active stages
        """
        return [self.stages[name] for name in self.active_stages if name in self.stages]
    
    def _update_display(self):
        """Update the terminal display with current progress."""
        if not self.config.enabled:
            return
        
        if not self.current_display_stage:
            return
        
        # Get the current stage
        stage = self.stages.get(self.current_display_stage)
        if not stage:
            return
        
        # Calculate overall progress
        overall_progress = self.get_overall_progress()
        
        # Prepare display
        self._clear_current_line()
        
        # Show spinner if enabled
        if self.config.show_spinner:
            spinner_char = self._spinner_chars[self._spinner_idx]
            sys.stdout.write(f"{spinner_char} ")
        
        # Show stage description
        sys.stdout.write(f"{stage.description} ")
        
        # Show progress bar if enabled
        if self.config.show_progress_bar and stage.total_items > 0:
            sys.stdout.write(self._create_progress_bar(stage.get_progress_percentage(), 20))
            sys.stdout.write(f" {stage.processed_items}/{stage.total_items} ")
        
        # Show ETA if enabled
        if self.config.show_eta:
            eta = stage.get_eta()
            if eta is not None:
                eta_str = self._format_time(eta)
                sys.stdout.write(f"ETA: {eta_str} ")
        
        # Show metrics if enabled
        if self.config.show_metrics and stage.metrics:
            metrics_str = " ".join(f"{k}={v}" for k, v in stage.metrics.items())
            sys.stdout.write(f"[{metrics_str}] ")
        
        # Show overall progress
        sys.stdout.write(f"(Overall: {overall_progress:.1f}%)\n")
        
        sys.stdout.flush()
    
    def _clear_current_line(self):
        """Clear the current terminal line."""
        sys.stdout.write("\r\033[K")  # Carriage return and clear line
        sys.stdout.flush()
    
    def _create_progress_bar(self, percentage: float, width: int = 20) -> str:
        """
        Create a text-based progress bar.
        
        Args:
            percentage: Progress percentage (0-100)
            width: Width of the progress bar in characters
            
        Returns:
            String representation of the progress bar
        """
        filled_width = int(width * percentage / 100)
        bar = "█" * filled_width + "░" * (width - filled_width)
        return f"[{bar}] {percentage:.1f}%"
    
    def _format_time(self, seconds: float) -> str:
        """
        Format seconds as human-readable time.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
    
    def _start_spinner_if_needed(self):
        """Start the spinner thread if not already running."""
        if not self.config.show_spinner or self._spinner_thread is not None:
            return
        
        self._spinner_active = True
        self._spinner_thread = threading.Thread(target=self._spinner_loop, daemon=True)
        self._spinner_thread.start()
    
    def _stop_spinner(self):
        """Stop the spinner thread."""
        self._spinner_active = False
        if self._spinner_thread:
            self._spinner_thread.join(timeout=0.5)
            self._spinner_thread = None
    
    def _spinner_loop(self):
        """Main loop for the spinner animation."""
        while self._spinner_active:
            with self._lock:
                self._spinner_idx = (self._spinner_idx + 1) % len(self._spinner_chars)
                if self.current_display_stage:
                    self._update_display()
            time.sleep(0.1)


class ProgressContext:
    """
    Context manager for tracking progress in a specific stage.
    
    Automatically starts and completes the stage and allows for
    progress updates within the context.
    
    Example:
        with ProgressContext("fetch_data", "Fetching data...", total_items=10) as ctx:
            for i in range(10):
                # Do work
                ctx.update()
    """
    
    def __init__(
        self,
        stage_name: str,
        description: str,
        total_items: int = 0,
        weight: float = 1.0,
        parent: Optional[str] = None,
        auto_complete: bool = True,
    ):
        """
        Initialize the progress context.
        
        Args:
            stage_name: Stage name
            description: Stage description
            total_items: Total items to process
            weight: Stage weight
            parent: Parent stage name
            auto_complete: Whether to auto-complete the stage on exit
        """
        self.stage_name = stage_name
        self.description = description
        self.total_items = total_items
        self.weight = weight
        self.parent = parent
        self.auto_complete = auto_complete
        self.progress_manager = get_progress_manager()
    
    def __enter__(self):
        """Enter the context and start the stage."""
        # Create the stage if it doesn't exist
        if not self.progress_manager.get_stage(self.stage_name):
            self.progress_manager.create_stage(
                name=self.stage_name,
                description=self.description,
                total_items=self.total_items,
                weight=self.weight,
                parent=self.parent,
            )
        
        # Start the stage
        self.progress_manager.start_stage(self.stage_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and complete or fail the stage."""
        if exc_type is None and self.auto_complete:
            self.progress_manager.complete_stage(self.stage_name)
        elif exc_type is not None:
            self.progress_manager.fail_stage(self.stage_name)
    
    def update(self, items: int = 1):
        """Update progress."""
        self.progress_manager.update_progress(self.stage_name, items)
    
    def set_progress(self, items: int):
        """Set absolute progress."""
        self.progress_manager.set_progress(self.stage_name, items)
    
    def add_metric(self, name: str, value: Any):
        """Add a metric."""
        self.progress_manager.add_metric(self.stage_name, name, value)


# Global progress manager instance
_progress_manager: Optional[ProgressManager] = None


def get_progress_manager() -> ProgressManager:
    """
    Get the global progress manager instance.
    
    Returns:
        ProgressManager instance
    """
    global _progress_manager
    
    if _progress_manager is None:
        _progress_manager = ProgressManager()
    
    return _progress_manager


def track_progress(
    stage_name: str,
    description: str,
    total_items: int = 0,
    weight: float = 1.0,
    parent: Optional[str] = None,
):
    """
    Decorator for tracking progress of a function.
    
    This decorator creates a progress stage and updates it during function execution.
    
    Args:
        stage_name: Stage name (machine-friendly identifier)
        description: Human-readable description
        total_items: Total number of items to process
        weight: Weight of this stage in overall progress
        parent: Parent stage name
    
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            progress_manager = get_progress_manager()
            
            # Create and start the stage
            stage = progress_manager.create_stage(
                name=stage_name,
                description=description,
                total_items=total_items,
                weight=weight,
                parent=parent
            )
            progress_manager.start_stage(stage_name)
            
            try:
                # Call the function
                result = func(*args, **kwargs)
                
                # Complete the stage
                progress_manager.complete_stage(stage_name)
                return result
            except Exception as e:
                # Mark as failed on exception
                progress_manager.fail_stage(stage_name)
                raise
        
        return wrapper
    
    return decorator


class ProgressReporter:
    """
    A simple progress reporter that can be used as a context manager.
    """
    
    def __init__(
        self,
        total: Union[int, str] = 0,
        desc: str = "Processing",
        unit: str = "it",
        unit_scale: bool = True,
        stage_name: Optional[str] = None,
    ):
        """
        Initialize the progress reporter.
        
        Args:
            total: Total number of items to process
            desc: Description of the process
            unit: Unit of measurement
            unit_scale: Whether to scale the unit (e.g., KB, MB)
            stage_name: Optional name for the progress stage
        """
        self.total = int(total)
        self.desc = desc
        self.unit = unit
        self.unit_scale = unit_scale
        self.stage_name = stage_name or f"progress_{int(time.time())}"
        self.processed = 0
        self.start_time = time.time()
        self.last_update = time.time()
        self.last_processed = 0
        # Try to get config, else use default
        try:
            self.config = get_config_manager().config.progress
            self.min_interval = getattr(self.config, 'report_interval_seconds', 1.0)
        except Exception:
            self.config = None
            self.min_interval = 1.0
        self.progress_manager = get_progress_manager()
        self.stage = self.progress_manager.create_stage(
            name=self.stage_name,
            description=desc,
            total_items=self.total
        )
        self.stage.start()
    
    def update(self, n: int = 1):
        """
        Update progress by incrementing by n units.
        
        Args:
            n: Number of units to increment by
        """
        self.processed += n
        current_time = time.time()
        if current_time - self.last_update >= self.min_interval:
            self.progress_manager.update_progress(self.stage_name, n)
            self.last_update = current_time
            elapsed = current_time - self.start_time
            if elapsed > 0 and self.processed > 0:
                speed = self.processed / elapsed
                self.progress_manager.add_metric(
                    self.stage_name,
                    "speed",
                    self._format_speed(speed)
                )
    
    def _format_speed(self, speed: float) -> str:
        """Format speed with units."""
        if not self.unit_scale:
            return f"{speed:.2f} {self.unit}/s"
        
        if self.unit.lower() == "b":  # Bytes
            for unit in ["B/s", "KB/s", "MB/s", "GB/s"]:
                if speed < 1024 or unit == "GB/s":
                    return f"{speed:.2f} {unit}"
                speed /= 1024
        
        # Default scaling for other units
        if speed < 0.1:
            return f"{speed*1000:.2f} m{self.unit}/s"
        elif speed < 1:
            return f"{speed*1000:.2f} m{self.unit}/s"
        elif speed >= 1000:
            return f"{speed/1000:.2f} k{self.unit}/s"
        else:
            return f"{speed:.2f} {self.unit}/s"
    
    def close(self):
        """Complete the progress reporting."""
        self.progress_manager.set_progress(self.stage_name, self.processed)
        self.progress_manager.complete_stage(self.stage_name)
    
    def __enter__(self):
        """Support for use as a context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete progress when exiting context."""
        if exc_type is not None:
            # An exception occurred
            self.progress_manager.fail_stage(self.stage_name)
        else:
            self.close() 