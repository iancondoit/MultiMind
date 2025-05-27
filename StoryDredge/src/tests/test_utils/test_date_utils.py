"""
Tests for date utilities.
"""

import pytest
from src.utils.date_utils import extract_date_from_archive_id, format_iso_date


class TestDateUtils:
    """Tests for date utilities."""
    
    def test_extract_date_from_archive_id(self):
        """Test extracting dates from archive IDs."""
        # Test with standard format
        archive_id = "per_atlanta-constitution_1922-01-01_54_203"
        result = extract_date_from_archive_id(archive_id)
        assert result == ("1922", "01", "01")
        
        # Test with no extra parts
        archive_id = "per_chicago-tribune_1934-05-22"
        result = extract_date_from_archive_id(archive_id)
        assert result == ("1934", "05", "22")
        
        # Test with different prefix
        archive_id = "sim_newcastle-morning-herald_1893-10-15"
        result = extract_date_from_archive_id(archive_id)
        assert result == ("1893", "10", "15")
        
        # Test with compact date format
        archive_id = "sim_newcastle-morning-herald_18931015"
        result = extract_date_from_archive_id(archive_id)
        assert result == ("1893", "10", "15")
        
        # Test with no date
        archive_id = "random_archive_with_no_date"
        result = extract_date_from_archive_id(archive_id)
        assert result is None
        
    def test_format_iso_date(self):
        """Test formatting dates to ISO format."""
        # Test valid date
        result = format_iso_date("1922", "01", "01")
        assert result == "1922-01-01T00:00:00.000Z"
        
        # Test another valid date
        result = format_iso_date("1934", "05", "22")
        assert result == "1934-05-22T00:00:00.000Z"
        
        # Test invalid date (February 30)
        result = format_iso_date("1922", "02", "30")
        # Should use current year with default month/day
        import datetime
        current_year = datetime.datetime.now().year
        assert result == f"{current_year}-01-01T00:00:00.000Z" 