"""
Tests for the HSAFormatter class.
"""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime

# Import the HSAFormatter class
from src.formatter.hsa_formatter import HSAFormatter
from src.utils.date_utils import extract_date_from_archive_id


class TestHSAFormatter:
    """Test cases for HSAFormatter."""
    
    def test_init(self):
        """Test initialization of HSAFormatter."""
        formatter = HSAFormatter()
        assert formatter.output_dir == Path("output/hsa-ready")
        
        # Use a valid directory instead of root-level path
        custom_dir = Path("custom_output")
        formatter = HSAFormatter(output_dir=custom_dir)
        assert formatter.output_dir == custom_dir
        
        # Cleanup
        if custom_dir.exists():
            import shutil
            shutil.rmtree(custom_dir)
    
    def test_validate_article(self, sample_newspaper_metadata):
        """Test article validation."""
        # Valid article
        article = {
            "headline": "Test Headline",
            "body": "Test body content",
            "section": "news",
            "tags": ["tag1", "tag2"],
            "timestamp": "1977-06-14",
            "publication": sample_newspaper_metadata["publication"],
            "source_issue": sample_newspaper_metadata["archive_id"],
            "source_url": sample_newspaper_metadata["source_url"],
            "byline": "By John Smith",
            "dateline": "SAN ANTONIO, JUNE 14"
        }
        
        formatter = HSAFormatter()
        valid, errors = formatter.validate_article(article)
        assert valid is True
        assert not errors
        
        # Test invalid article (missing required fields)
        invalid_article = {
            "headline": "Test Headline",
            # Missing body
            "section": "unknown",  # Invalid section
            # Missing tags
        }
        
        valid, errors = formatter.validate_article(invalid_article)
        assert valid is False
        assert len(errors) >= 3  # At least 3 errors (missing body, section, tags)
        assert any("body" in error for error in errors)
        assert any("section" in error for error in errors)
        assert any("tags" in error for error in errors)
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        formatter = HSAFormatter()
        
        # Test with date only
        timestamp = formatter.format_timestamp("1977-06-14")
        assert timestamp == "1977-06-14T00:00:00.000Z"
        
        # Test with date and time
        timestamp = formatter.format_timestamp("1977-06-14 15:30:00")
        assert timestamp == "1977-06-14T15:30:00.000Z"
        
        # Test with already formatted timestamp
        timestamp = formatter.format_timestamp("1977-06-14T15:30:00.000Z")
        assert timestamp == "1977-06-14T15:30:00.000Z"
        
        # Test with invalid date format
        timestamp = formatter.format_timestamp("June 14, 1977")
        # Should default to YYYY-MM-DD
        year = datetime.now().year
        assert timestamp == f"{year}-01-01T00:00:00.000Z"
    
    def test_get_output_path(self, temp_dir):
        """Test output path generation."""
        article = {
            "timestamp": "1977-06-14T00:00:00.000Z",
            "headline": "Test Headline"
        }
        
        formatter = HSAFormatter(output_dir=temp_dir)
        path = formatter.get_output_path(article)
        
        # Should create a path like: output_dir/1977/06/14/some-unique-filename.json
        assert "1977" in str(path)
        assert "06" in str(path)
        assert "14" in str(path)
        assert path.suffix == ".json"
        
        # Parent directories should be created
        assert path.parent.exists()
    
    def test_format_article(self, sample_newspaper_metadata):
        """Test article formatting for HSA."""
        # Raw article from classifier
        article = {
            "headline": "Test Headline",
            "raw_text": "This should not be in the final output",
            "body": "Test body content",
            "section": "news",
            "tags": ["tag1", "tag2"],
            "date": "1977-06-14",  # Non-standard format
            "publication": sample_newspaper_metadata["publication"],
            "source_issue": sample_newspaper_metadata["archive_id"],
            "source_url": sample_newspaper_metadata["source_url"],
            "byline": "By John Smith",
            "dateline": "SAN ANTONIO, JUNE 14",
            "extra_field": "This should be removed"
        }
        
        formatter = HSAFormatter()
        formatted = formatter.format_article(article)
        
        # Check required fields
        assert formatted["headline"] == "Test Headline"
        # When both raw_text and body are present, body should be used
        assert formatted["body"] == "Test body content"  
        assert formatted["section"] == "news"
        assert "tag1" in formatted["tags"]
        assert formatted["timestamp"] is not None  # Now it might use date from archive ID
        assert formatted["publication"] == sample_newspaper_metadata["publication"]
        assert formatted["source_issue"] == sample_newspaper_metadata["archive_id"]
        assert formatted["source_url"] == sample_newspaper_metadata["source_url"]
        assert formatted["byline"] == "By John Smith"
        assert formatted["dateline"] == "SAN ANTONIO, JUNE 14"
        
        # These fields should not be in the output
        assert "raw_text" not in formatted
        assert "date" not in formatted
        assert "extra_field" not in formatted
        
        # Test with only raw_text, not body
        article = {
            "headline": "Test Headline",
            "raw_text": "This should be used as body content",
            # No body field
            "section": "news",
            "tags": ["tag1", "tag2"],
            "date": "1977-06-14",
            "publication": sample_newspaper_metadata["publication"]
        }
        
        formatted = formatter.format_article(article)
        assert formatted["body"] == "This should be used as body content"
    
    def test_format_article_with_archive_id_date(self):
        """Test article formatting with date extraction from archive ID."""
        # Article with archive ID containing date
        article = {
            "headline": "Test Headline",
            "body": "Test body content",
            "section": "news",
            "tags": ["tag1", "tag2"],
            # No explicit date/timestamp
            "publication": "The Atlanta Constitution",
            "source_issue": "per_atlanta-constitution_1922-01-15_54_210",
            "source_url": "https://archive.org/details/per_atlanta-constitution_1922-01-15_54_210"
        }
        
        formatter = HSAFormatter()
        formatted = formatter.format_article(article)
        
        # Should extract date from archive ID
        assert formatted["timestamp"] == "1922-01-15T00:00:00.000Z"
        
        # Test with alternative archive ID format
        article["source_issue"] = "sim_newcastle-morning-herald_18931015"
        formatted = formatter.format_article(article)
        
        # Should extract date from alternative archive ID format
        assert formatted["timestamp"] == "1893-10-15T00:00:00.000Z"
        
        # Test with explicit date that should be overridden by archive ID
        article["date"] = "2020-05-01"  # This should be ignored in favor of archive ID date
        article["source_issue"] = "per_atlanta-constitution_1922-01-15_54_210"
        formatted = formatter.format_article(article)
        
        # Should prioritize date from archive ID
        assert formatted["timestamp"] == "1922-01-15T00:00:00.000Z"
    
    def test_format_article_with_metadata(self, sample_newspaper_metadata):
        """Test article formatting with metadata extraction for tags."""
        # Article with metadata from classifier
        article = {
            "headline": "Test Headline",
            "body": "Test body content",
            "category": "News",
            "confidence": 0.95,
            "metadata": {
                "topic": "Politics",
                "people": ["John Doe", "Jane Smith"],
                "organizations": ["Acme Corp", "Government"],
                "locations": ["New York", "Washington DC"]
            },
            "section": "news",
            "tags": ["original_tag"],
            "date": "1977-06-14",
            "publication": sample_newspaper_metadata["publication"],
            "source_issue": sample_newspaper_metadata["archive_id"],
            "source_url": sample_newspaper_metadata["source_url"]
        }
        
        formatter = HSAFormatter()
        formatted = formatter.format_article(article)
        
        # Original tag should be preserved
        assert "original_tag" in formatted["tags"]
        
        # Metadata should be extracted as tags
        assert "news" in formatted["tags"]  # Category
        assert "politics" in formatted["tags"]  # Topic
        assert "john doe" in formatted["tags"]  # Person
        assert "jane smith" in formatted["tags"]  # Person
        assert "acme corp" in formatted["tags"]  # Organization
        assert "government" in formatted["tags"]  # Organization
        assert "new york" in formatted["tags"]  # Location
        assert "washington dc" in formatted["tags"]  # Location
        
        # Check that there are 9 tags total (1 original + 8 from metadata)
        assert len(formatted["tags"]) == 9
    
    def test_map_category_to_section(self):
        """Test mapping classification categories to valid HSA sections."""
        formatter = HSAFormatter()
        
        # Test direct mappings
        assert formatter._map_category_to_section("News") == "news"
        assert formatter._map_category_to_section("Sports") == "sports"
        assert formatter._map_category_to_section("Opinion") == "opinion"
        assert formatter._map_category_to_section("Business") == "business"
        
        # Test with whitespace and case variations
        assert formatter._map_category_to_section("  NEWS  ") == "news"
        assert formatter._map_category_to_section("SPORTS") == "sports"
        
        # Test fuzzy matching
        assert formatter._map_category_to_section("Sporting Event") == "sports"
        assert formatter._map_category_to_section("Editorial Opinion") == "opinion"
        assert formatter._map_category_to_section("Business Finance") == "business"
        
        # Test unmapped category
        assert formatter._map_category_to_section("Unknown Category") is None
    
    def test_format_article_with_category_section_mapping(self):
        """Test that category is properly mapped to section when section is invalid."""
        # Article with invalid section, but valid category
        article = {
            "headline": "Test Headline",
            "body": "Test body content",
            "category": "Sports",
            "section": "invalid_section",  # Not a valid section
            "tags": [],
            "timestamp": "1977-06-14T00:00:00.000Z"
        }
        
        formatter = HSAFormatter()
        formatted = formatter.format_article(article)
        
        # Section should be mapped from category since the original section was invalid
        assert formatted["section"] == "sports"
        
        # Article with category that doesn't map to valid section
        article = {
            "headline": "Test Headline",
            "body": "Test body content",
            "category": "Unknown Category",
            "section": "invalid_section",
            "tags": [],
            "timestamp": "1977-06-14T00:00:00.000Z"
        }
        
        formatter = HSAFormatter()
        formatted = formatter.format_article(article)
        
        # Section should default to "other"
        assert formatted["section"] == "other"
    
    def test_save_article(self, temp_dir, sample_newspaper_metadata):
        """Test saving formatted article to file."""
        article = {
            "headline": "Test Headline",
            "body": "Test body content",
            "section": "news",
            "tags": ["tag1", "tag2"],
            "timestamp": "1977-06-14T00:00:00.000Z",
            "publication": sample_newspaper_metadata["publication"],
            "source_issue": sample_newspaper_metadata["archive_id"],
            "source_url": sample_newspaper_metadata["source_url"],
            "byline": "By John Smith",
            "dateline": "SAN ANTONIO, JUNE 14"
        }
        
        formatter = HSAFormatter(output_dir=temp_dir)
        result = formatter.save_article(article)
        
        # Should successfully save
        assert result is not None
        assert result.exists()
        
        # Verify content
        with open(result, 'r') as f:
            saved = json.load(f)
            assert saved["headline"] == "Test Headline"
            assert saved["body"] == "Test body content"
            assert saved["section"] == "news"
    
    def test_save_article_invalid(self, temp_dir):
        """Test handling of invalid articles."""
        # Invalid article
        article = {
            "headline": "Test Headline",
            # Missing required fields
        }
        
        formatter = HSAFormatter(output_dir=temp_dir)
        result = formatter.save_article(article)
        
        # Should fail gracefully
        assert result is None
    
    def test_process_batch(self, temp_dir, sample_newspaper_metadata):
        """Test processing a batch of articles."""
        # Create a batch of test articles
        articles = [
            {
                "headline": f"Article {i}",
                "body": f"Content for article {i}",
                "section": "news",
                "tags": ["test"],
                "date": "1977-06-14",
                "publication": sample_newspaper_metadata["publication"],
                "source_issue": sample_newspaper_metadata["archive_id"],
                "source_url": sample_newspaper_metadata["source_url"]
            }
            for i in range(1, 4)
        ]
        
        formatter = HSAFormatter(output_dir=temp_dir)
        results = formatter.process_batch(articles)
        
        # Should process all articles
        assert len(results) == 3
        
        # All files should exist
        for path in results:
            assert path.exists()
        
        # All should be in the same date directory
        assert all("1977/06/14" in str(path) for path in results) 