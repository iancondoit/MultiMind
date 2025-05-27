"""
Common utility functions for the StoryDredge pipeline.
"""

import os
import json
import re
from pathlib import Path
import logging
from typing import Any, Dict, Optional, Union, List

logger = logging.getLogger("utils.common")


def slugify(text: str) -> str:
    """
    Convert a string to a slug (URL-friendly string).
    
    Args:
        text: The string to convert
        
    Returns:
        A slugified string
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace non-alphanumeric characters with hyphens
    text = re.sub(r'[^a-z0-9]', '-', text)
    
    # Replace multiple hyphens with a single hyphen
    text = re.sub(r'-+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    return text


def sanitize_filename(filename: str, max_length: int = 100) -> str:
    """
    Sanitize a filename to ensure it's valid on all operating systems.
    
    Args:
        filename: The filename to sanitize
        max_length: Maximum length of the filename
        
    Returns:
        A sanitized filename
    """
    # Replace invalid characters with underscores
    filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
    
    # Replace spaces with underscores
    filename = re.sub(r'\s+', '_', filename)
    
    # Truncate if too long
    if len(filename) > max_length:
        base, ext = os.path.splitext(filename)
        filename = base[:max_length - len(ext)] + ext
    
    return filename


def ensure_directory(directory: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
        
    Returns:
        True if the directory exists or was created, False otherwise
    """
    directory = Path(directory)
    
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False


def load_json(file_path: Union[str, Path], default: Any = None) -> Any:
    """
    Load JSON from a file.
    
    Args:
        file_path: Path to the JSON file
        default: Default value to return if loading fails
        
    Returns:
        The loaded JSON data or the default value
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return default
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {e}")
        return default


def save_json(data: Any, file_path: Union[str, Path], indent: int = 2) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        data: Data to save
        file_path: Path to the output file
        indent: Number of spaces for indentation
        
    Returns:
        True if saving succeeded, False otherwise
    """
    file_path = Path(file_path)
    
    # Create the directory if it doesn't exist
    if not ensure_directory(file_path.parent):
        return False
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {e}")
        return False 