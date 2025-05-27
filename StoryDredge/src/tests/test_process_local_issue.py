#!/usr/bin/env python3
"""
Test Local Issue Processing

This script tests the functionality of the process_local_issue.py script.
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.process_local_issue import (
    clean_publication_name,
    parse_issue_id,
    create_output_directory,
    generate_article_filename,
    process_local_issue
)


class TestProcessLocalIssue(unittest.TestCase):
    """Tests for the process_local_issue.py script."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path("test_output")
        self.test_dir.mkdir(exist_ok=True)
        
        # Sample article data
        self.article = {
            "headline": "Test Article Headline",
            "body": "This is a test article body.",
            "section": "news",
            "tags": ["test", "article", "news"],
            "timestamp": "1922-01-09T00:00:00.000Z",
            "publication": "Test Newspaper",
            "source_issue": "test_newspaper_1922-01-09_001",
            "source_url": "https://archive.org/details/test_newspaper_1922-01-09_001"
        }
        
        # Sample OCR file
        self.sample_ocr_text = """
        THE TEST NEWSPAPER
        January 9, 1922
        
        HEADLINE ONE
        This is the content of the first article.
        It spans multiple lines and contains
        various details about some topic.
        
        HEADLINE TWO
        This is another article with different content.
        It also spans multiple lines.
        """
        
        # Create a sample OCR file
        self.ocr_file = self.test_dir / "sample_ocr.txt"
        with open(self.ocr_file, 'w', encoding='utf-8') as f:
            f.write(self.sample_ocr_text)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test files and directories
        if self.test_dir.exists():
            for file in self.test_dir.glob("**/*"):
                if file.is_file():
                    file.unlink()
            for dir_path in sorted(self.test_dir.glob("**/*"), key=lambda x: str(x), reverse=True):
                if dir_path.is_dir():
                    dir_path.rmdir()
            self.test_dir.rmdir()
    
    def test_clean_publication_name(self):
        """Test the clean_publication_name function."""
        test_cases = [
            ("Atlanta Constitution", "atlanta-constitution"),
            ("The New York Times", "the-new-york-times"),
            ("Chicago Tribune!", "chicago-tribune"),
            ("Washington Post (1877-1954)", "washington-post-1877-1954"),
            ("San Francisco Chronicle & Examiner", "san-francisco-chronicle-examiner")
        ]
        
        for input_name, expected_output in test_cases:
            with self.subTest(input_name=input_name):
                self.assertEqual(clean_publication_name(input_name), expected_output)
    
    def test_parse_issue_id(self):
        """Test the parse_issue_id function."""
        test_cases = [
            (
                "per_atlanta-constitution_1922-01-01_54_203",
                ("atlanta-constitution", "1922", "01", "01")
            ),
            (
                "pub_chicago-tribune_19220215",
                ("chicago-tribune", "", "", "")
            ),
            (
                "atlanta-constitution_1922-03-15_001",
                ("atlanta-constitution", "1922", "03", "15")
            ),
        ]
        
        for issue_id, expected_output in test_cases:
            with self.subTest(issue_id=issue_id):
                self.assertEqual(parse_issue_id(issue_id), expected_output)
    
    def test_create_output_directory(self):
        """Test the create_output_directory function."""
        publication = "test-newspaper"
        year = "1922"
        month = "01"
        day = "09"
        
        expected_dir = self.test_dir / publication / year / month / day
        result_dir = create_output_directory(self.test_dir, publication, year, month, day)
        
        self.assertEqual(result_dir, expected_dir)
        self.assertTrue(expected_dir.exists())
        self.assertTrue(expected_dir.is_dir())
    
    def test_generate_article_filename(self):
        """Test the generate_article_filename function."""
        year = "1922"
        month = "01"
        day = "09"
        
        test_cases = [
            (
                {"headline": "Test Article Headline"},
                "1922-01-09--test-article-headline.json"
            ),
            (
                {"headline": "Very Long Title That Should Be Truncated To Fifty Characters Maximum For The Filename Requirements"},
                "1922-01-09--very-long-title-that-should-be-truncated-to-fifty.json"
            ),
            (
                {"headline": "Special Characters! @#$%^&*() Should Be Removed"},
                "1922-01-09--special-characters-should-be-removed.json"
            ),
            (
                {"headline": ""},
                "1922-01-09--untitled.json"
            ),
        ]
        
        for article, expected_filename in test_cases:
            with self.subTest(headline=article["headline"]):
                self.assertEqual(generate_article_filename(article, year, month, day), expected_filename)
    
    @patch('scripts.process_local_issue.OCRCleaner')
    @patch('scripts.process_local_issue.ArticleSplitter')
    @patch('scripts.process_local_issue.ArticleClassifier')
    def test_process_local_issue(self, mock_classifier_class, mock_splitter_class, mock_cleaner_class):
        """Test the process_local_issue function with mocked dependencies."""
        # Setup mocks
        mock_cleaner = MagicMock()
        mock_cleaner.clean_text.return_value = "Mock cleaned text"
        mock_cleaner_class.return_value = mock_cleaner
        
        mock_splitter = MagicMock()
        mock_headlines = [(0, 10, "Headline 1"), (100, 110, "Headline 2")]
        mock_splitter.detect_headlines.return_value = mock_headlines
        mock_articles = [
            {"title": "Headline 1", "raw_text": "Article 1 text"}, 
            {"title": "Headline 2", "raw_text": "Article 2 text"}
        ]
        mock_splitter.extract_articles.return_value = mock_articles
        mock_splitter_class.return_value = mock_splitter
        
        mock_classifier = MagicMock()
        mock_classified = {
            "title": "Headline 1",
            "raw_text": "Article 1 text",
            "category": "news",
            "metadata": {
                "people": ["John Doe"],
                "organizations": ["Acme Corp"],
                "locations": ["Atlanta"],
                "tags": ["important"]
            }
        }
        mock_classifier.classify_article.return_value = mock_classified
        mock_classifier_class.return_value = mock_classifier
        
        # Test process_local_issue
        issue_id = "per_atlanta-constitution_1922-01-09_54_211"
        output_dir = self.test_dir
        
        result = process_local_issue(issue_id, self.ocr_file, output_dir)
        
        # Verify result
        self.assertTrue(result)
        
        # Verify expected directory structure
        expected_dir = output_dir / "atlanta-constitution" / "1922" / "01" / "09"
        self.assertTrue(expected_dir.exists())
        
        # Verify calls to mocked components
        mock_cleaner.clean_text.assert_called_once()
        mock_splitter.detect_headlines.assert_called_once_with("Mock cleaned text")
        mock_splitter.extract_articles.assert_called_once_with("Mock cleaned text", mock_headlines)
        self.assertEqual(mock_classifier.classify_article.call_count, 2)
    
    def test_process_local_issue_file_not_found(self):
        """Test process_local_issue with a non-existent file."""
        issue_id = "per_atlanta-constitution_1922-01-09_54_211"
        nonexistent_file = self.test_dir / "nonexistent.txt"
        output_dir = self.test_dir
        
        result = process_local_issue(issue_id, nonexistent_file, output_dir)
        
        # Should return False when file not found
        self.assertFalse(result)
    
    def test_process_local_issue_invalid_issue_id(self):
        """Test process_local_issue with an invalid issue ID."""
        issue_id = "invalid_issue_id_format"
        output_dir = self.test_dir
        
        result = process_local_issue(issue_id, self.ocr_file, output_dir)
        
        # Should handle invalid issue ID gracefully
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main() 