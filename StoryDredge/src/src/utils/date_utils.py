"""
Date utilities for StoryDredge.

This module provides functions for working with dates in various formats.
"""

import re
from datetime import datetime
from typing import Optional, Tuple, Union


def extract_date_from_archive_id(archive_id: str) -> Optional[str]:
    """
    Extract date from an archive.org identifier like per_atlanta-constitution_1922-01-01_54_203.
    
    Args:
        archive_id: Archive.org identifier
        
    Returns:
        Formatted date string in YYYY-MM-DD format, or None if no date found
    """
    # Try to extract date using regex
    date_pattern = r'_(\d{4}-\d{2}-\d{2})_'
    match = re.search(date_pattern, archive_id)
    
    if match:
        date_str = match.group(1)
        return date_str
    
    # Alternative format: try to find YYYYMMDD or YYYY_MM_DD
    alt_pattern1 = r'_(\d{4})(\d{2})(\d{2})_'
    alt_pattern2 = r'_(\d{4})_(\d{2})_(\d{2})_'
    
    match1 = re.search(alt_pattern1, archive_id)
    if match1:
        year, month, day = match1.groups()
        return f"{year}-{month}-{day}"
    
    match2 = re.search(alt_pattern2, archive_id)
    if match2:
        year, month, day = match2.groups()
        return f"{year}-{month}-{day}"
    
    # Last resort: try to find any 4-digit number as year and nearby 2-digit numbers
    year_pattern = r'_(\d{4})_'
    year_match = re.search(year_pattern, archive_id)
    
    if year_match:
        year = year_match.group(1)
        # Default to January 1st of that year
        return f"{year}-01-01"
    
    return None


def format_iso_date(year: Union[str, int], month: Union[str, int], day: Union[str, int]) -> str:
    """
    Format a date in ISO format YYYY-MM-DDT00:00:00.000Z.
    
    Args:
        year: Year as string or integer
        month: Month as string or integer
        day: Day as string or integer
        
    Returns:
        Formatted date string
    """
    # Ensure all parts are strings and zero-padded
    year_str = str(year).zfill(4)
    month_str = str(month).zfill(2)
    day_str = str(day).zfill(2)
    
    return f"{year_str}-{month_str}-{day_str}T00:00:00.000Z"


def is_valid_date(date_str: str) -> bool:
    """
    Check if a date string is valid.
    
    Args:
        date_str: Date string to check
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Try to parse the date
        if 'T' in date_str:
            # ISO format
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        elif '-' in date_str:
            # YYYY-MM-DD format
            year, month, day = date_str.split('-')
            datetime(int(year), int(month), int(day))
        else:
            return False
        
        return True
    except (ValueError, TypeError):
        return False


def get_current_date() -> str:
    """
    Get the current date in ISO format.
    
    Returns:
        Current date in YYYY-MM-DD format
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_current_timestamp() -> str:
    """
    Get the current timestamp in ISO format.
    
    Returns:
        Current timestamp in YYYY-MM-DDT00:00:00.000Z format
    """
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z") 