"""
Test the entity tag extraction in the HSA formatter.

These tests verify that:
1. Entities from metadata are properly added to tags
2. Both direct and nested metadata fields are processed
3. The formatter handles various input formats correctly
"""

import os
import sys
import json
import pytest
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.formatter.hsa_formatter import HSAFormatter


class TestEntityTagExtraction:
    """Tests for entity tag extraction in the HSA formatter."""

    @pytest.fixture
    def sample_articles(self):
        """Create sample classified articles for testing."""
        return {
            "simple": {
                "headline": "Mayor Announces New Budget",
                "body": "Mayor John Smith announced the new city budget yesterday.",
                "category": "news",
                "people": ["John Smith"],
                "organizations": ["City Council"],
                "locations": ["City Hall"],
                "source_issue": "per_test-newspaper_1922-01-01_54_001",
                "publication": "Test Newspaper",
                "source_url": "https://example.com"
            },
            "nested": {
                "headline": "Sports Team Wins Championship",
                "body": "The Atlanta Hawks won the championship.",
                "category": "sports",
                "metadata": {
                    "people": ["Michael Jordan", "Phil Jackson"],
                    "organizations": ["Atlanta Hawks", "NBA"],
                    "locations": ["Atlanta", "Georgia"]
                },
                "source_issue": "per_test-newspaper_1922-01-01_54_001",
                "publication": "Test Newspaper",
                "source_url": "https://example.com"
            },
            "mixed": {
                "headline": "Business News Update",
                "body": "Acme Corporation announced record profits.",
                "category": "business",
                "people": ["John Doe"],
                "metadata": {
                    "organizations": ["Acme Corporation", "Wall Street"],
                    "locations": ["New York"]
                },
                "source_issue": "per_test-newspaper_1922-01-01_54_001",
                "publication": "Test Newspaper",
                "source_url": "https://example.com"
            }
        }
    
    def test_direct_entity_extraction(self, sample_articles, tmp_path):
        """Test extraction of entities directly in the article."""
        formatter = HSAFormatter(output_dir=tmp_path)
        
        # Format the article
        article = sample_articles["simple"]
        formatted = formatter.format_article(article)
        
        # Check that entities were added to tags
        assert "John Smith" in formatted["tags"], "Person entity should be in tags"
        assert "City Council" in formatted["tags"], "Organization entity should be in tags"
        assert "City Hall" in formatted["tags"], "Location entity should be in tags"
        
        # Check that category is also in tags
        assert "news" in formatted["tags"], "Category should be in tags"
    
    def test_nested_entity_extraction(self, sample_articles, tmp_path):
        """Test extraction of entities from nested metadata."""
        formatter = HSAFormatter(output_dir=tmp_path)
        
        # Format the article
        article = sample_articles["nested"]
        formatted = formatter.format_article(article)
        
        # Check that entities from nested metadata were added to tags
        assert "Michael Jordan" in formatted["tags"], "Person entity from metadata should be in tags"
        assert "Phil Jackson" in formatted["tags"], "Person entity from metadata should be in tags"
        assert "Atlanta Hawks" in formatted["tags"], "Organization entity from metadata should be in tags"
        assert "NBA" in formatted["tags"], "Organization entity from metadata should be in tags"
        assert "Atlanta" in formatted["tags"], "Location entity from metadata should be in tags"
        assert "Georgia" in formatted["tags"], "Location entity from metadata should be in tags"
        
        # Check that category is also in tags
        assert "sports" in formatted["tags"], "Category should be in tags"
    
    def test_mixed_entity_extraction(self, sample_articles, tmp_path):
        """Test extraction of entities from both direct and nested sources."""
        formatter = HSAFormatter(output_dir=tmp_path)
        
        # Format the article
        article = sample_articles["mixed"]
        formatted = formatter.format_article(article)
        
        # Check that entities from both sources were added to tags
        assert "John Doe" in formatted["tags"], "Person entity should be in tags"
        assert "Acme Corporation" in formatted["tags"], "Organization entity from metadata should be in tags"
        assert "Wall Street" in formatted["tags"], "Organization entity from metadata should be in tags"
        assert "New York" in formatted["tags"], "Location entity from metadata should be in tags"
        
        # Check that category is also in tags
        assert "business" in formatted["tags"], "Category should be in tags"
    
    def test_save_with_entities(self, sample_articles, tmp_path):
        """Test that saved articles contain the extracted entity tags."""
        formatter = HSAFormatter(output_dir=tmp_path)
        
        # Save the article
        article = sample_articles["mixed"]
        output_path = formatter.save_article(article)
        
        # Check that the file was created
        assert output_path.exists(), "Output file should exist"
        
        # Read the saved file
        with open(output_path, "r") as f:
            saved = json.load(f)
        
        # Check that entities were saved in tags
        assert "John Doe" in saved["tags"], "Person entity should be in saved tags"
        assert "Acme Corporation" in saved["tags"], "Organization entity should be in saved tags"
        assert "Wall Street" in saved["tags"], "Organization entity should be in saved tags"
        assert "New York" in saved["tags"], "Location entity should be in saved tags" 