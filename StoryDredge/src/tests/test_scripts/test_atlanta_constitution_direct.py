"""
Tests for the Atlanta Constitution direct testing script.

These tests verify the functionality of the scripts/test_atlanta_constitution_direct.py script,
which downloads and processes Atlanta Constitution newspaper issues.
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.test_atlanta_constitution_direct import (
    download_ocr_with_curl,
    process_ocr_file,
    main
)


@pytest.fixture
def mock_subprocess():
    """Fixture to mock subprocess.run"""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        yield mock_run


@pytest.fixture
def mock_path_exists():
    """Fixture to mock Path.exists to return True"""
    with patch("pathlib.Path.exists", return_value=True) as mock_exists:
        yield mock_exists


@pytest.fixture
def mock_path_stat():
    """Fixture to mock Path.stat to return a file size"""
    mock_stat = MagicMock()
    mock_stat.st_size = 1000
    with patch("pathlib.Path.stat", return_value=mock_stat) as mock_stat_method:
        yield mock_stat_method


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
        yield mock_cleaner_class


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
        yield mock_splitter_class


class TestAtlantaConstitutionDirect:
    """Tests for the Atlanta Constitution direct testing script."""

    def test_download_ocr_with_curl(self, mock_subprocess, mock_path_exists, mock_path_stat, tmp_path):
        """Test downloading OCR with curl."""
        # Arrange
        issue_id = "per_atlanta-constitution_1922-01-01_54_203"
        output_dir = tmp_path
        
        # Act
        result = download_ocr_with_curl(issue_id, output_dir)
        
        # Assert
        assert result is not None
        assert mock_subprocess.call_count == 1
        # Verify curl command has correct arguments
        curl_args = mock_subprocess.call_args[0][0]
        assert curl_args[0] == "curl"
        assert curl_args[1] == "-L"  # Follows redirects
        assert issue_id in curl_args[-1]  # URL contains issue ID

    def test_download_ocr_failure(self, mock_subprocess, mock_path_exists, tmp_path):
        """Test handling of download failures."""
        # Arrange
        issue_id = "per_atlanta-constitution_1922-01-01_54_203"
        output_dir = tmp_path
        mock_subprocess.side_effect = Exception("Download failed")
        
        # Act
        result = download_ocr_with_curl(issue_id, output_dir)
        
        # Assert
        assert result is None

    def test_process_ocr_file(self, mock_open_files, mock_cleaner, mock_splitter, tmp_path):
        """Test processing an OCR file."""
        # Arrange
        issue_id = "per_atlanta-constitution_1922-01-01_54_203"
        ocr_file = tmp_path / f"{issue_id}.txt"
        
        # Create required directories
        (tmp_path / "output" / issue_id / "articles").mkdir(parents=True, exist_ok=True)
        
        # Set up expected paths to ensure they exist
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.mkdir"):
                with patch("json.dump") as mock_json_dump:
                    # Act
                    result = process_ocr_file(ocr_file, issue_id)
                    
                    # Assert
                    assert result is True
                    # Verify cleaners and splitters were called
                    assert mock_cleaner.call_count == 1
                    assert mock_splitter.call_count == 1
                    # Verify articles were saved
                    assert mock_json_dump.call_count >= 1

    @patch("scripts.test_atlanta_constitution_direct.download_ocr_with_curl")
    @patch("scripts.test_atlanta_constitution_direct.process_ocr_file")
    @patch("json.dump")
    def test_main(self, mock_json_dump, mock_process, mock_download, tmp_path):
        """Test the main function."""
        # Arrange
        test_file = tmp_path / "test.txt"
        mock_download.return_value = test_file
        mock_process.return_value = True
        
        # Act
        with patch("pathlib.Path.mkdir"):
            main()
        
        # Assert
        # Verify each test issue was downloaded and processed
        assert mock_download.call_count == 2  # Two test issues
        assert mock_process.call_count == 2
        # Verify results were saved
        assert mock_json_dump.call_count == 1 