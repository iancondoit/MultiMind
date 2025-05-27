"""
Tests for utility functions.
"""

import pytest
import os
from pathlib import Path
import json
import tempfile
import shutil

# Import the implemented utility functions
from src.utils.common import slugify, sanitize_filename, ensure_directory, load_json, save_json


class TestUtilFunctions:
    """Test cases for utility functions."""
    
    def test_slugify(self):
        """Test the slugify function for creating URL-friendly strings."""
        assert slugify("Hello World") == "hello-world"
        assert slugify("This is a TEST!") == "this-is-a-test"
        assert slugify("Multiple   spaces") == "multiple-spaces"
        assert slugify("Special@#$%^&*() chars") == "special-chars"
        assert slugify("") == ""
    
    def test_sanitize_filename(self):
        """Test sanitizing filenames."""
        assert sanitize_filename("file with spaces.txt") == "file_with_spaces.txt"
        assert sanitize_filename("invalid/chars:in*name.txt") == "invalid_chars_in_name.txt"
        assert len(sanitize_filename("a" * 200 + ".txt")) <= 104  # Should truncate
    
    def test_ensure_directory(self, temp_dir):
        """Test directory creation."""
        # Test with Path object
        nested_dir = temp_dir / "nested" / "subdir"
        assert ensure_directory(nested_dir) is True
        assert nested_dir.is_dir()
        
        # Test with string path
        str_path = str(temp_dir / "string_path")
        assert ensure_directory(str_path) is True
        assert os.path.isdir(str_path)
    
    def test_load_json(self, temp_dir):
        """Test loading JSON files."""
        # Test data
        test_data = {"key": "value", "list": [1, 2, 3]}
        
        # Create test file
        file_path = temp_dir / "test.json"
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
        
        # Test loading
        loaded_data = load_json(file_path)
        assert loaded_data == test_data
        
        # Test loading nonexistent file
        nonexistent = temp_dir / "nonexistent.json"
        assert load_json(nonexistent) is None
        
        # Test default value
        assert load_json(nonexistent, default={"default": True}) == {"default": True}
    
    def test_save_json(self, temp_dir):
        """Test saving JSON files."""
        # Test data
        test_data = {"key": "value", "nested": {"a": 1, "b": 2}}
        file_path = temp_dir / "output.json"
        
        # Test saving
        success = save_json(test_data, file_path)
        assert success is True
        assert file_path.exists()
        
        # Verify contents
        with open(file_path, 'r') as f:
            loaded = json.load(f)
            assert loaded == test_data
        
        # Test creating directories
        nested_path = temp_dir / "subdir" / "nested" / "output.json"
        success = save_json(test_data, nested_path)
        assert success is True
        assert nested_path.exists()
        
        # Test error handling (invalid directory)
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            invalid_path = Path(temp_file_path) / "invalid.json"  # File treated as directory
            success = save_json(test_data, invalid_path)
            assert success is False
        finally:
            os.unlink(temp_file_path) 