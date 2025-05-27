#!/usr/bin/env python3
"""
Tests for the ArticleClassifier component.
"""

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.classifier.article_classifier import ArticleClassifier, OllamaClient, PromptTemplates


class TestOllamaClient(unittest.TestCase):
    """Tests for the OllamaClient class."""

    @patch('requests.post')
    def test_generate_successful(self, mock_post):
        """Test successful text generation."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "model": "llama2",
            "response": "This is a test response",
            "done": True
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Create client and call generate
        client = OllamaClient()
        result = client.generate("Test prompt", model="llama2")

        # Verify results
        self.assertEqual(result["response"], "This is a test response")
        self.assertEqual(result["model"], "llama2")
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_generate_request_exception(self, mock_post):
        """Test handling of request exceptions."""
        # Setup mock to raise exception
        mock_post.side_effect = Exception("Connection error")

        # Create client and verify exception handling
        client = OllamaClient()
        with self.assertRaises(Exception):
            client.generate("Test prompt")

    @patch('requests.post')
    def test_generate_json_parse_error(self, mock_post):
        """Test handling of JSON parsing errors."""
        # Setup mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "This is not valid JSON but we handle it"
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Create client and call generate
        client = OllamaClient()
        result = client.generate("Test prompt")

        # Verify fallback response handling
        self.assertEqual(result["response"], "This is not valid JSON but we handle it")
        self.assertEqual(result["model"], "llama2")


class TestPromptTemplates(unittest.TestCase):
    """Tests for the PromptTemplates class."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary templates directory
        self.temp_dir = Path("temp_templates")
        self.temp_dir.mkdir(exist_ok=True)
        
        # Create a test template file
        test_template = "This is a test template with {variable}."
        with open(self.temp_dir / "test.txt", "w") as f:
            f.write(test_template)

    def tearDown(self):
        """Clean up after tests."""
        # Remove test template file and directory
        for file in self.temp_dir.glob("*.txt"):
            file.unlink()
        self.temp_dir.rmdir()

    def test_load_templates(self):
        """Test loading templates from directory."""
        templates = PromptTemplates(self.temp_dir)
        self.assertIn("test", templates.templates)
        self.assertEqual(templates.templates["test"], "This is a test template with {variable}.")

    def test_get_template_existing(self):
        """Test getting an existing template."""
        templates = PromptTemplates(self.temp_dir)
        template = templates.get_template("test")
        self.assertEqual(template, "This is a test template with {variable}.")

    def test_get_template_nonexistent(self):
        """Test getting a nonexistent template."""
        templates = PromptTemplates(self.temp_dir)
        template = templates.get_template("nonexistent")
        self.assertTrue("You are an expert" in template)  # Should return default template

    def test_format_template(self):
        """Test formatting a template with variables."""
        templates = PromptTemplates(self.temp_dir)
        formatted = templates.format_template("test", variable="value")
        self.assertEqual(formatted, "This is a test template with value.")

    def test_format_template_missing_variable(self):
        """Test formatting with missing variable."""
        templates = PromptTemplates(self.temp_dir)
        with self.assertRaises(Exception):
            templates.format_template("test")  # Missing required variable


class TestArticleClassifier(unittest.TestCase):
    """Tests for the ArticleClassifier class."""

    def setUp(self):
        """Set up test environment."""
        # Create test article
        self.test_article = {
            "title": "Test Article",
            "raw_text": "This is a test article about politics and government. The mayor announced a new policy yesterday."
        }

    @patch('src.classifier.article_classifier.OllamaClient')
    def test_init(self, mock_ollama_client):
        """Test initialization of ArticleClassifier."""
        classifier = ArticleClassifier()
        self.assertIsNotNone(classifier)
        mock_ollama_client.assert_called_once()

    @patch('src.classifier.article_classifier.OllamaClient')
    def test_classify_article(self, mock_ollama_client):
        """Test classifying a single article."""
        # Setup mock response
        mock_client_instance = mock_ollama_client.return_value
        mock_client_instance.generate.return_value = {
            "response": """```json
{
  "category": "Politics",
  "confidence": 0.95,
  "metadata": {
    "topic": "Local Government",
    "people": ["Mayor"],
    "organizations": ["City Council"],
    "locations": ["City"]
  }
}
```"""
        }

        # Create classifier and classify article
        classifier = ArticleClassifier()
        result = classifier.classify_article(self.test_article)

        # Verify classification structure matches actual output
        self.assertEqual(result["category"], "Politics")
        self.assertEqual(result["confidence"], 0.95)
        self.assertEqual(result["metadata"]["topic"], "Local Government")
        self.assertEqual(result["title"], "Test Article")
        self.assertEqual(result["raw_text"], self.test_article["raw_text"])

    @patch('src.utils.progress.ProgressReporter')
    @patch('src.classifier.article_classifier.ArticleClassifier.classify_article')
    def test_classify_batch(self, mock_classify_article, mock_progress_reporter):
        """Test classifying a batch of articles."""
        # Setup mocks to avoid ProgressReporter issues
        expected_result = {
            "category": "Politics",
            "confidence": 0.95,
            "metadata": {
                "topic": "Local Government",
                "people": ["Mayor"],
                "organizations": ["City Council"],
                "locations": ["City"]
            },
            "title": "Test Article",
            "raw_text": "This is a test article about politics and government."
        }
        mock_classify_article.return_value = expected_result
        
        # Mock the progress reporter
        mock_progress_instance = MagicMock()
        mock_progress_reporter.return_value = mock_progress_instance

        # Create classifier and classify batch
        classifier = ArticleClassifier()
        articles = [self.test_article, self.test_article]
        results = classifier.classify_batch(articles)

        # Verify classification
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertEqual(result["category"], "Politics")
            self.assertEqual(result["confidence"], 0.95)
        
        # Verify mock was called correctly
        self.assertEqual(mock_classify_article.call_count, 2)

    @patch('src.classifier.article_classifier.OllamaClient')
    def test_classify_article_no_text(self, mock_ollama_client):
        """Test classifying an article with no text."""
        # Create empty article
        empty_article = {"title": "Empty Article"}

        # Create classifier and classify article
        classifier = ArticleClassifier()
        result = classifier.classify_article(empty_article)

        # Verify default classification is used
        self.assertEqual(result["category"], "miscellaneous")
        self.assertEqual(result["confidence"], 0.0)
        self.assertEqual(result["title"], "Empty Article")
        
        # Ensure LLM wasn't called
        mock_client_instance = mock_ollama_client.return_value
        mock_client_instance.generate.assert_not_called()

    @patch('src.classifier.article_classifier.OllamaClient')
    def test_classify_article_invalid_response(self, mock_ollama_client):
        """Test handling of invalid LLM responses."""
        # Setup mock with invalid JSON response
        mock_client_instance = mock_ollama_client.return_value
        mock_client_instance.generate.return_value = {
            "response": "This is not valid JSON"
        }

        # Create classifier and classify article
        classifier = ArticleClassifier()
        result = classifier.classify_article(self.test_article)

        # Verify fallback classification
        self.assertEqual(result["category"], "miscellaneous")
        self.assertEqual(result["confidence"], 0.0)
        self.assertEqual(result["title"], "Test Article")

    @patch('src.classifier.article_classifier.PromptTemplates')
    @patch('src.classifier.article_classifier.OllamaClient')
    def test_classify_file(self, mock_ollama_client, mock_prompt_templates):
        """Test classifying an article from a file."""
        # Setup mocks
        mock_client_instance = mock_ollama_client.return_value
        mock_client_instance.generate.return_value = {
            "response": """```json
{
  "category": "News",
  "confidence": 0.9,
  "metadata": {
    "topic": "General",
    "people": [],
    "organizations": [],
    "locations": []
  }
}
```"""
        }
        
        # Mock prompt templates to avoid file operations
        mock_templates_instance = MagicMock()
        mock_prompt_templates.return_value = mock_templates_instance
        mock_templates_instance.get_template.return_value = "Test template"
        mock_templates_instance.format_template.return_value = "Formatted template"

        # Use a nested mock for open to isolate file operations
        with patch('builtins.open', unittest.mock.mock_open(read_data='{"title": "Test", "raw_text": "Test content"}')) as m:
            # Create classifier and classify from file
            classifier = ArticleClassifier()
            result = classifier.classify_file("test_article.json")

            # Verify classification matches structure
            self.assertEqual(result["category"], "News")
            self.assertEqual(result["confidence"], 0.9)
            self.assertIn("metadata", result)
            
            # Verify open was called with the right parameters
            m.assert_any_call("test_article.json", "r", encoding="utf-8")


if __name__ == '__main__':
    unittest.main() 