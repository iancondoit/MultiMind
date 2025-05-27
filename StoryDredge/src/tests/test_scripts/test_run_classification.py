#!/usr/bin/env python3
"""
Tests for the run_classification.py script.
"""

import os
import sys
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import the script to test but avoid ProgressReporter problems
with patch('src.utils.progress.ProgressReporter'):
    import scripts.run_classification as run_classification


class TestRunClassification(unittest.TestCase):
    """Tests for the run_classification.py script."""

    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
        
        # Create an issue directory with articles
        self.issue_id = "test_issue_123"
        self.issue_dir = self.output_dir / self.issue_id
        self.articles_dir = self.issue_dir / "articles"
        self.classified_dir = self.issue_dir / "classified"
        
        # Create directory structure
        self.articles_dir.mkdir(parents=True)
        
        # Create test article files
        self.article_data = {
            "title": "Test Article",
            "raw_text": "This is a test article content."
        }
        
        # Create multiple test articles
        for i in range(3):
            with open(self.articles_dir / f"article_{i:04d}.json", "w") as f:
                json.dump(self.article_data, f)

    def tearDown(self):
        """Clean up after tests."""
        self.temp_dir.cleanup()

    @patch('scripts.run_classification.ArticleClassifier')
    def test_classify_issue(self, mock_classifier_class):
        """Test classifying a single issue."""
        # Setup mock classifier
        mock_classifier = MagicMock()
        classified_result = {
            "title": "Test Article",
            "raw_text": "This is a test article content.",
            "category": "News",
            "confidence": 0.9,
            "metadata": {
                "topic": "General",
                "people": [],
                "organizations": [],
                "locations": []
            }
        }
        mock_classifier.classify_article.return_value = classified_result
        mock_classifier_class.return_value = mock_classifier

        # Call function under test
        result = run_classification.classify_issue(self.issue_id, self.output_dir)

        # Verify results
        self.assertTrue(result)
        self.assertTrue(self.classified_dir.exists())
        self.assertEqual(len(list(self.classified_dir.glob("*.json"))), 3)
        mock_classifier.classify_article.assert_called()
        self.assertEqual(mock_classifier.classify_article.call_count, 3)

    @patch('scripts.run_classification.classify_issue')
    def test_classify_issues(self, mock_classify_issue):
        """Test classifying multiple issues."""
        # Setup mock
        mock_classify_issue.return_value = True

        # Call function under test
        issue_ids = ["issue1", "issue2", "issue3"]
        result = run_classification.classify_issues(issue_ids, self.output_dir)

        # Verify results
        self.assertEqual(result["total_issues"], 3)
        self.assertEqual(len(result["successful"]), 3)
        self.assertEqual(len(result["failed"]), 0)
        self.assertIn("processing_time", result)
        mock_classify_issue.assert_called()
        self.assertEqual(mock_classify_issue.call_count, 3)

    @patch('scripts.run_classification.classify_issue')
    def test_classify_issues_with_failures(self, mock_classify_issue):
        """Test classifying issues with some failures."""
        # Setup mock to alternate success/failure
        mock_classify_issue.side_effect = [True, False, True]

        # Call function under test
        issue_ids = ["issue1", "issue2", "issue3"]
        result = run_classification.classify_issues(issue_ids, self.output_dir)

        # Verify results
        self.assertEqual(result["total_issues"], 3)
        self.assertEqual(len(result["successful"]), 2)
        self.assertEqual(len(result["failed"]), 1)
        self.assertEqual(result["successful"], ["issue1", "issue3"])
        self.assertEqual(result["failed"], ["issue2"])

    @patch('json.dump')
    @patch('scripts.run_classification.classify_issues')
    def test_main_with_issues_file(self, mock_classify_issues, mock_json_dump):
        """Test main function with issues file."""
        # Setup mocks
        mock_json_data = ["issue1", "issue2"]
        mock_result = {
            "successful": ["issue1", "issue2"],
            "failed": []
        }
        mock_classify_issues.return_value = mock_result
        
        # Mock JSON dump to avoid serialization issues with MagicMock objects
        mock_json_dump.return_value = None
        
        with patch('builtins.open', unittest.mock.mock_open()):
            with patch('json.load', return_value=mock_json_data):
                with patch('sys.argv', ['run_classification.py', '--issues-file', 'test.json']):
                    # Make sure sys.exit doesn't terminate the test
                    with patch('sys.exit') as mock_exit:
                        # Call function under test
                        run_classification.main()
                        
                        # Verify sys.exit was not called with an error code
                        mock_exit.assert_not_called()

        # Verify results
        mock_classify_issues.assert_called_once()
        args, kwargs = mock_classify_issues.call_args
        self.assertEqual(args[0], mock_json_data)
        
        # Verify that json.dump was called to save results
        mock_json_dump.assert_called_once()

    @patch('scripts.run_classification.classify_issue')
    def test_main_with_single_issue(self, mock_classify_issue):
        """Test main function with single issue."""
        # Setup mock
        mock_classify_issue.return_value = True
        
        with patch('sys.argv', ['run_classification.py', '--issue', 'test_issue']):
            # Call function under test
            run_classification.main()

        # Verify results
        mock_classify_issue.assert_called_once()
        args, kwargs = mock_classify_issue.call_args
        self.assertEqual(args[0], 'test_issue')


if __name__ == '__main__':
    unittest.main() 