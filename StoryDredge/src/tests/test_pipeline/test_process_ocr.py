"""
Tests for the pipeline/process_ocr.py module.

These tests verify the functionality of the process_ocr module,
which processes OCR text through the pipeline components.
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pipeline.process_ocr import process_ocr, main


@pytest.fixture
def mock_path_exists():
    """Fixture to mock Path.exists to return True"""
    with patch("pathlib.Path.exists", return_value=True) as mock_exists:
        yield mock_exists


@pytest.fixture
def mock_path_mkdir():
    """Fixture to mock Path.mkdir"""
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        yield mock_mkdir


@pytest.fixture
def mock_open_files():
    """Fixture to mock file opening operations"""
    mock_content = "Mock newspaper OCR content"
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = mock_content
    
    with patch("builtins.open", return_value=mock_file) as mock_open:
        yield mock_open


@pytest.fixture
def mock_cleaner():
    """Fixture to mock OCRCleaner"""
    with patch("src.cleaner.ocr_cleaner.OCRCleaner") as mock_cleaner_class:
        mock_cleaner_instance = MagicMock()
        mock_cleaner_instance.clean_text.return_value = "Cleaned OCR text"
        mock_cleaner_class.return_value = mock_cleaner_instance
        yield mock_cleaner_instance


@pytest.fixture
def mock_splitter():
    """Fixture to mock ArticleSplitter"""
    with patch("src.splitter.article_splitter.ArticleSplitter") as mock_splitter_class:
        mock_splitter_instance = MagicMock()
        mock_splitter_instance.detect_headlines.return_value = [
            (0, 10, "Headline 1"),
            (100, 110, "Headline 2")
        ]
        mock_splitter_instance.extract_articles.return_value = [
            {"title": "Headline 1", "raw_text": "Article 1 content"},
            {"title": "Headline 2", "raw_text": "Article 2 content"}
        ]
        mock_splitter_class.return_value = mock_splitter_instance
        yield mock_splitter_instance


@pytest.fixture
def mock_classifier():
    """Fixture to mock ArticleClassifier"""
    with patch("src.classifier.article_classifier.ArticleClassifier") as mock_classifier_class:
        mock_classifier_instance = MagicMock()
        mock_classifier_instance.classify_article.return_value = {
            "category": "news",
            "confidence": 0.95,
            "metadata": {
                "topic": "politics",
                "people": ["John Smith"],
                "organizations": ["Government"],
                "locations": ["Atlanta"]
            }
        }
        mock_classifier_class.return_value = mock_classifier_instance
        yield mock_classifier_instance


@pytest.fixture
def mock_formatter():
    """Fixture to mock HSAFormatter"""
    with patch("src.formatter.hsa_formatter.HSAFormatter") as mock_formatter_class:
        mock_formatter_instance = MagicMock()
        mock_formatter_class.return_value = mock_formatter_instance
        yield mock_formatter_instance


@pytest.fixture
def mock_progress():
    """Fixture to mock ProgressReporter"""
    with patch("src.utils.progress.ProgressReporter") as mock_progress_class:
        mock_progress_instance = MagicMock()
        mock_progress_class.return_value = mock_progress_instance
        yield mock_progress_instance


class TestProcessOcr:
    """Tests for the process_ocr module."""

    def test_process_ocr_with_existing_file(
        self, 
        mock_path_exists, 
        mock_path_mkdir,
        mock_open_files, 
        mock_cleaner, 
        mock_splitter, 
        mock_classifier, 
        mock_formatter,
        mock_progress
    ):
        """Test processing OCR with an existing file."""
        # Arrange
        issue_id = "per_atlanta-constitution_1922-01-01_54_203"
        
        # Act
        with patch("json.dump") as mock_json_dump:
            result = process_ocr(issue_id, skip_fetch=True)
            
        # Assert
        assert result is True
        # Verify cleaner was called with raw OCR text
        assert mock_cleaner.clean_text.call_count == 1
        # Verify splitter methods were called
        assert mock_splitter.detect_headlines.call_count == 1
        assert mock_splitter.extract_articles.call_count == 1
        # Verify classifier was called with each article
        assert mock_classifier.classify_article.call_count == 2  # Two mock articles
        # Verify formatter was called
        assert mock_formatter.format_issue.call_count == 1

    def test_process_ocr_with_fetch(
        self, 
        mock_cleaner, 
        mock_splitter, 
        mock_classifier, 
        mock_formatter,
        mock_progress
    ):
        """Test processing OCR with fetching."""
        # Arrange
        issue_id = "per_atlanta-constitution_1922-01-01_54_203"
        
        # Mock path.exists to return False first, then True for other calls
        path_exists_mock = MagicMock()
        path_exists_mock.side_effect = [False] + [True] * 10  # First call False, rest True
        
        # Mock fetcher
        mock_fetcher_instance = MagicMock()
        mock_fetcher_instance.fetch_issue.return_value = "mock_fetched_file.txt"
        mock_fetcher = MagicMock(return_value=mock_fetcher_instance)
        
        # Act
        with patch("pathlib.Path.exists", path_exists_mock):
            with patch("pathlib.Path.mkdir"):
                with patch("src.fetcher.archive_fetcher.ArchiveFetcher", mock_fetcher):
                    with patch("builtins.open", MagicMock()):
                        with patch("json.dump"):
                            result = process_ocr(issue_id, skip_fetch=False)
            
        # Assert
        assert result is True
        # Verify fetcher was called
        assert mock_fetcher_instance.fetch_issue.call_count == 1
        assert mock_fetcher_instance.fetch_issue.call_args[0][0] == issue_id

    def test_process_ocr_with_fetch_failure(self):
        """Test processing OCR with fetch failure."""
        # Arrange
        issue_id = "per_atlanta-constitution_1922-01-01_54_203"
        
        # Mock path.exists to return False first
        path_exists_mock = MagicMock(return_value=False)
        
        # Mock fetcher to return None (failure)
        mock_fetcher_instance = MagicMock()
        mock_fetcher_instance.fetch_issue.return_value = None
        mock_fetcher = MagicMock(return_value=mock_fetcher_instance)
        
        # Act
        with patch("pathlib.Path.exists", path_exists_mock):
            with patch("pathlib.Path.mkdir"):
                with patch("src.fetcher.archive_fetcher.ArchiveFetcher", mock_fetcher):
                    result = process_ocr(issue_id, skip_fetch=False)
            
        # Assert
        assert result is False
        # Verify fetcher was called
        assert mock_fetcher_instance.fetch_issue.call_count == 1

    def test_process_ocr_missing_file_with_skip_fetch(self):
        """Test processing OCR with missing file and skip_fetch."""
        # Arrange
        issue_id = "per_atlanta-constitution_1922-01-01_54_203"
        
        # Mock path.exists to return False
        path_exists_mock = MagicMock(return_value=False)
        
        # Act
        with patch("pathlib.Path.exists", path_exists_mock):
            with patch("pathlib.Path.mkdir"):
                result = process_ocr(issue_id, skip_fetch=True)
            
        # Assert
        assert result is False

    @patch("pipeline.process_ocr.process_ocr")
    def test_main_with_args(self, mock_process_ocr):
        """Test main function with command line arguments."""
        # Arrange
        mock_process_ocr.return_value = True
        test_args = ["program_name", "--issue", "test-issue", "--skip-fetch", "--output-dir", "test-output"]
        
        # Act
        with patch("sys.argv", test_args):
            main()
            
        # Assert
        assert mock_process_ocr.call_count == 1
        assert mock_process_ocr.call_args == call("test-issue", skip_fetch=True, output_dir="test-output")

    @patch("pipeline.process_ocr.process_ocr")
    @patch("sys.exit")
    def test_main_with_failure(self, mock_exit, mock_process_ocr):
        """Test main function with processing failure."""
        # Arrange
        mock_process_ocr.return_value = False
        test_args = ["program_name", "--issue", "test-issue"]
        
        # Act
        with patch("sys.argv", test_args):
            main()
            
        # Assert
        assert mock_process_ocr.call_count == 1
        # Verify sys.exit was called with error code
        assert mock_exit.call_count == 1
        assert mock_exit.call_args == call(1) 