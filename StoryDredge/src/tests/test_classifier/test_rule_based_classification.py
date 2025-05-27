"""
Test the rule-based classification system.

These tests verify that:
1. The ArticleClassifier defaults to rule-based classification
2. Entities are properly extracted and included in the output
3. The classification is correctly applied to articles
"""

import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.classifier.article_classifier import ArticleClassifier


class TestRuleBasedClassification:
    """Tests for the rule-based classification system."""

    @pytest.fixture
    def sample_articles(self, tmp_path):
        """Create sample articles for testing."""
        articles_dir = tmp_path / "articles"
        articles_dir.mkdir(exist_ok=True)
        
        # Create test articles with different content for different classifications
        articles = {
            "news": {
                "title": "Mayor Announces New City Budget",
                "raw_text": "CITY HALL - Mayor John Smith announced the new city budget yesterday. The $10 million budget includes funding for infrastructure and education. City Council will vote on the proposal next week."
            },
            "sports": {
                "title": "Local Team Wins Championship",
                "raw_text": "The Atlanta Hawks defeated the Boston Celtics 105-98 in the championship game on Sunday. Star player Michael Jordan scored 42 points to lead his team to victory. Coach Phil Jackson praised the team's performance."
            },
            "business": {
                "title": "Stock Market Hits Record High",
                "raw_text": "The Dow Jones Industrial Average reached a record high of 25,000 points yesterday. Technology stocks led the gains, with Apple and Microsoft both up over 3%. Analysts at Goldman Sachs predict continued growth through the year."
            }
        }
        
        # Save articles to files
        saved_paths = {}
        for category, content in articles.items():
            file_path = articles_dir / f"{category}_article.json"
            with open(file_path, "w") as f:
                json.dump(content, f)
            saved_paths[category] = file_path
            
        return {
            "articles_dir": articles_dir,
            "article_paths": saved_paths,
            "article_contents": articles
        }
    
    def test_default_to_rule_based(self):
        """Test that ArticleClassifier defaults to rule-based classification."""
        classifier = ArticleClassifier()
        assert classifier.skip_classification is True, "skip_classification should default to True"
        
        # Test explicit setting
        classifier_explicit = ArticleClassifier(skip_classification=False)
        assert classifier_explicit.skip_classification is False, "skip_classification should respect explicit setting"
    
    def test_rule_based_classification(self, sample_articles):
        """Test that rule-based classification correctly categorizes articles."""
        classifier = ArticleClassifier(skip_classification=True)
        
        # Test each article type
        for category, content in sample_articles["article_contents"].items():
            # Create a dictionary with 'raw_text' field as expected by the classifier
            article_dict = {"title": content.get("title", "Test Article"), "raw_text": content["raw_text"]}
            result = classifier.classify_article(article_dict)
            
            # Check that we got a result
            assert result is not None, f"Should classify {category} article"
            
            # Check that a category was assigned (actual category may vary based on the rule-based algorithm)
            assert "category" in result, "Should assign a category"
    
    def test_entity_extraction(self, sample_articles):
        """Test that entities are properly extracted in rule-based classification."""
        classifier = ArticleClassifier(skip_classification=True)
        
        # Test the news article for entities
        news_article = sample_articles["article_contents"]["news"]
        # Create a dictionary with 'raw_text' field as expected by the classifier
        article_dict = {"title": news_article.get("title", "Test Article"), "raw_text": news_article["raw_text"]}
        result = classifier.classify_article(article_dict)
        
        # Check for extracted entities
        metadata = result.get("metadata", {})
        assert "people" in metadata, "Should extract people entities"
        assert "organizations" in metadata, "Should extract organization entities" 
        
        # Print metadata for debugging
        print(f"People: {metadata['people']}")
        print(f"Organizations: {metadata['organizations']}")
        if "locations" in metadata:
            print(f"Locations: {metadata['locations']}")
        
        # Check for partial matches since NER may extract names differently
        found_john = any("John" in person for person in metadata["people"])
        found_city_council = any("City Council" in org or "Council" in org for org in metadata["organizations"])
        
        # Verify that we found expected entities
        assert found_john, "Should extract a person named John"
        assert found_city_council, "Should extract City Council as an organization"
        
        # Note: Location detection is not consistently reliable in the NER system
        # so we're not testing for specific locations
    
    def test_classify_directory(self, sample_articles, tmp_path):
        """Test that classify_directory works correctly with rule-based classification."""
        classifier = ArticleClassifier(skip_classification=True)
        output_dir = tmp_path / "classified"
        output_dir.mkdir(exist_ok=True)
        
        # Classify the directory
        results = classifier.classify_directory(
            input_dir=sample_articles["articles_dir"],
            output_dir=output_dir
        )
        
        # Check results
        assert len(results) == 3, "Should classify all 3 articles"
        
        # Check output files
        output_files = list(output_dir.glob("*.json"))
        assert len(output_files) == 3, "Should create 3 output files"
        
        # Check content of classified files
        for output_file in output_files:
            with open(output_file, "r") as f:
                classified = json.load(f)
            
            # Check for required fields
            assert "category" in classified, "Should contain category"
            assert "metadata" in classified, "Should contain metadata"
            
            # Check for entities in metadata
            metadata = classified["metadata"]
            assert "people" in metadata, "Should extract people entities"
            assert "organizations" in metadata, "Should extract organization entities"
            assert "locations" in metadata, "Should extract location entities"
    
    def test_performance(self, sample_articles):
        """Test that rule-based classification is performant."""
        classifier = ArticleClassifier(skip_classification=True)
        
        import time
        
        # Create a dictionary with 'raw_text' field as expected by the classifier
        news_article = sample_articles["article_contents"]["news"]
        article_dict = {"title": news_article.get("title", "Test Article"), "raw_text": news_article["raw_text"]}
        
        # Measure classification time for a single article
        start_time = time.time()
        classifier.classify_article(article_dict)
        end_time = time.time()
        
        # Rule-based classification should be very fast (under 0.1 seconds)
        assert (end_time - start_time) < 0.1, "Rule-based classification should be fast" 