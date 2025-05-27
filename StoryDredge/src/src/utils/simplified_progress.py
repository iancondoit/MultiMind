"""
Simplified progress reporting for StoryDredge.

This module provides a simple progress reporting class that can be used
to track progress of long-running operations.
"""

import time
import logging
import sys
from typing import Optional, Any

# Configure logger
logger = logging.getLogger(__name__)

class ProgressReporter:
    """
    A simple progress reporter that works in the terminal.
    """
    
    def __init__(
        self,
        desc: str = "Processing",
        total: int = 0,
        unit: str = "it",
        unit_scale: bool = True
    ):
        """
        Initialize the progress reporter.
        
        Args:
            desc: Description of the operation
            total: Total number of items
            unit: Unit name (e.g., "it" for items)
            unit_scale: Whether to scale units for display
        """
        self.desc = desc
        self.total = max(0, int(total) if total else 0)
        self.unit = unit
        self.unit_scale = unit_scale
        
        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.min_interval = 0.1  # Minimum seconds between display updates
        
        # Spinner characters
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.spinner_index = 0
        
        # Initial display
        self._update_display()
    
    def update(self, n: int = 1):
        """
        Update progress by incrementing by n units.
        
        Args:
            n: Number of units to increment by
        """
        try:
            # Ensure n is a valid number
            n = int(n) if n else 1
        except (ValueError, TypeError):
            n = 1
        
        self.current += n
        
        # Ensure we don't exceed total
        if self.total > 0 and self.current > self.total:
            self.current = self.total
        
        # Only update display periodically to avoid slowing down
        current_time = time.time()
        if current_time - self.last_update_time >= self.min_interval:
            self._update_display()
            self.last_update_time = current_time
    
    def _update_display(self):
        """Update the progress display in the terminal."""
        # Only display if we're in a terminal
        if not sys.stdout.isatty():
            return
        
        spinner = self.spinner_chars[self.spinner_index % len(self.spinner_chars)]
        self.spinner_index += 1
        
        # Create status line
        if self.total > 0:
            # We have a known total, show percentage
            percentage = min(100.0, (self.current / self.total) * 100.0)
            status = f"{spinner} {self.desc} ({percentage:.1f}%)"
        else:
            # Unknown total, just show count
            status = f"{spinner} {self.desc} (Overall: 100.0%)"
        
        # Print status (clear line first)
        sys.stdout.write("\r\033[K" + status)
        sys.stdout.flush()
    
    def complete(self):
        """Mark the progress as complete."""
        if self.total > 0:
            self.current = self.total
        
        self._update_display()
        # Add a newline to move past the progress display
        sys.stdout.write("\n")
        sys.stdout.flush()
    
    def __enter__(self):
        """Support for context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete progress when exiting context."""
        if exc_type is None:
            # No exception occurred
            self.complete()
        else:
            # Add a newline to move past the progress display
            sys.stdout.write("\n")
            sys.stdout.flush() 