#!/usr/bin/env python3
"""
Test HSA Formatter Output

This module contains tests to verify that the HSA formatter produces output
in the correct format with all required fields.
"""

import os
import sys
import json
import pytest
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from io import StringIO

# Ensure we can import from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.formatter.hsa_formatter import HSAFormatter


def create_test_article() -> Dict[str, Any]:
    """Create a test article with minimal fields."""
    return {
        "title": "Test Article Headline",
        "raw_text": "This is a test article body with some content.",
        "category": "news",
        "source_issue": "per_atlanta-constitution_1922-01-01_54_203"
    }


@pytest.fixture
def test_output_dir(tmp_path) -> Path:
    """Create a temporary output directory for test files."""
    return tmp_path / "output"


@pytest.fixture
def formatter(test_output_dir) -> HSAFormatter:
    """Create a formatter instance with test output directory."""
    formatter = HSAFormatter(output_dir=test_output_dir)
    formatter.add_default_values = True
    formatter.strict_validation = False
    return formatter


def test_formatter_basic_output(formatter, test_output_dir):
    """Test that the formatter produces basic correctly formatted output."""
    article = create_test_article()
    
    # Format the article
    formatted = formatter.format_article(article)
    
    # Check required fields
    assert "headline" in formatted
    assert formatted["headline"] == "Test Article Headline"
    assert "body" in formatted
    assert "tags" in formatted
    assert isinstance(formatted["tags"], list)
    assert "section" in formatted
    assert formatted["section"] == "news"
    assert "timestamp" in formatted
    assert "publication" in formatted
    assert "source_issue" in formatted
    assert "source_url" in formatted


def test_formatter_output_path(formatter, test_output_dir):
    """Test that the formatter saves files to the correct directory structure."""
    article = create_test_article()
    
    # Save the article
    output_path = formatter.save_article(article)
    
    # Check that the output path exists
    assert output_path.exists()
    
    # Check that it's in the correct directory structure (YYYY/MM/DD)
    path_parts = output_path.relative_to(test_output_dir).parts
    assert len(path_parts) >= 4  # hsa-ready/YYYY/MM/DD/filename.json
    assert path_parts[0] == "hsa-ready"
    assert path_parts[1] == "1922"  # From article source_issue
    assert path_parts[2] == "01"
    assert path_parts[3] == "01"


def test_formatter_validation(formatter):
    """Test that the formatter correctly validates articles."""
    # Create a minimal valid article
    minimal_article = {
        "headline": "Test Headline",
        "body": "Test body text",
        "tags": ["news"],
        "section": "news",
        "timestamp": "2022-01-01T00:00:00.000Z",
        "publication": "Test Publication",
        "source_issue": "test_source",
        "source_url": "https://example.com"
    }
    
    # Validate the article
    valid, errors = formatter.validate_article(minimal_article)
    assert valid
    assert len(errors) == 0
    
    # Create an invalid article (missing required fields)
    invalid_article = {
        "headline": "Test Headline",
        "body": "Test body text"
    }
    
    # Validate the invalid article
    valid, errors = formatter.validate_article(invalid_article)
    assert not valid
    assert len(errors) > 0


def test_formatter_byline_handling(formatter):
    """Test that the formatter correctly handles bylines in various formats."""
    # Article with headline starting with "BY"
    byline_article = {
        "title": "BY JOHN SMITH",
        "raw_text": "This is an article with a byline in the title.",
        "category": "news",
        "source_issue": "per_atlanta-constitution_1922-01-01_54_203"
    }
    
    # Format the article
    formatted = formatter.format_article(byline_article)
    
    # Check that byline was extracted
    assert "byline" in formatted
    assert formatted["byline"] == "JOHN SMITH"
    
    # Check that a new headline was created
    assert formatted["headline"] != "BY JOHN SMITH"
    
    # Article with explicit byline
    explicit_byline_article = {
        "title": "Test Article",
        "raw_text": "This is a test article.",
        "byline": "Jane Doe",
        "category": "news",
        "source_issue": "per_atlanta-constitution_1922-01-01_54_203"
    }
    
    # Format the article
    formatted = formatter.format_article(explicit_byline_article)
    
    # Check that byline was preserved
    assert "byline" in formatted
    assert formatted["byline"] == "Jane Doe"


def test_formatter_timestamp_formatting(formatter):
    """Test that the formatter correctly formats timestamps."""
    # Article with timestamp in different format
    article = create_test_article()
    article["timestamp"] = "2022-01-01 12:34:56"
    
    # Format the article
    formatted = formatter.format_article(article)
    
    # Check that timestamp was formatted correctly
    assert "timestamp" in formatted
    assert formatted["timestamp"] == "2022-01-01T12:34:56.000Z"


def test_formatter_handles_missing_fields(formatter):
    """Test that the formatter handles missing fields with defaults when configured to do so."""
    # Create an article with minimal fields
    minimal_article = {
        "raw_text": "This is a test article with minimal fields."
    }
    
    # Format with add_default_values = True
    formatter.add_default_values = True
    formatted = formatter.format_article(minimal_article)
    
    # Save should succeed because defaults are added
    output_path = formatter.save_article(minimal_article)
    assert output_path is not None
    
    # Check that required fields were added
    with open(output_path, 'r', encoding='utf-8') as f:
        saved = json.load(f)
        
    for field in formatter.REQUIRED_FIELDS:
        assert field in saved
        assert saved[field] != ""


def test_formatter_strict_validation(formatter):
    """Test that the formatter can be configured for strict validation."""
    # Create an article with missing fields
    minimal_article = {
        "raw_text": "This is a test article with minimal fields."
    }
    
    # Format with default settings (should work)
    formatter.strict_validation = False
    formatter.add_default_values = True
    output_path = formatter.save_article(minimal_article)
    assert output_path is not None
    
    # Create an extremely minimal article that will fail even with default values
    extremely_minimal = {}
    
    # Test with strict validation
    formatter.strict_validation = True
    formatter.add_default_values = True
    
    # Test that save_article correctly applies strict_validation
    # by patching the validate_article method to always return failure
    original_validate = formatter.validate_article
    
    # Define a patched validate function that always returns False
    def mock_validate(article):
        return False, ["Mock validation error"]
    
    # Patch the function
    try:
        formatter.validate_article = mock_validate
        # Attempt to save with the patched validate function
        output_path = formatter.save_article(extremely_minimal)
        # With strict validation, it should return None
        assert output_path is None
    finally:
        # Restore the original function
        formatter.validate_article = original_validate
    
    # Reset formatter settings to original
    formatter.strict_validation = False
    formatter.add_default_values = True


def test_formatter_with_real_example():
    """Test formatter with a real example matching the documentation."""
    # Example from the documentation
    example = {
        "headline": "AND SAVE MONEY",
        "body": "AND SAVE MONEY. \nSANTA CLAUS left another carload of oil \nstocks in your chimney...",
        "tags": ["news"],
        "section": "news",
        "timestamp": "1922-01-01T00:00:00.000Z",
        "publication": "Atlanta Constitution",
        "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
        "source_url": "https://archive.org/details/per_atlanta-constitution_1922-01-01",
        "byline": ""
    }
    
    # Create formatter with temporary directory
    formatter = HSAFormatter(output_dir=Path("temp_test_output"))
    
    # Validate the example
    valid, errors = formatter.validate_article(example)
    assert valid, f"Example from documentation is not valid: {errors}"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 