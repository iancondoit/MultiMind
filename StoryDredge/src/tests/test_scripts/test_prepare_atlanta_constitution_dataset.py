"""
Tests for the prepare_atlanta_constitution_dataset.py script.

These tests verify the functionality of the script that prepares Atlanta Constitution datasets.
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, call, mock_open
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.prepare_atlanta_constitution_dataset import (
    search_issues,
    check_ocr_availability,
    save_issues_file,
    prepare_dataset,
    main
)


@pytest.fixture
def mock_requests():
    """Mock requests module for testing API calls."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": {
            "docs": [
                {
                    "identifier": "per_atlanta-constitution_1922-01-01_54_203",
                    "title": "Atlanta Constitution, January 1, 1922",
                    "date": "1922-01-01T00:00:00Z"
                },
                {
                    "identifier": "per_atlanta-constitution_1922-01-02_54_204",
                    "title": "Atlanta Constitution, January 2, 1922",
                    "date": "1922-01-02T00:00:00Z"
                }
            ],
            "numFound": 2
        }
    }
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        yield mock_get


@pytest.fixture
def mock_metadata_response():
    """Mock response for metadata API calls."""
    def mock_get_response(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        
        # Different response based on issue ID in URL
        if "1922-01-01" in url:
            mock_resp.json.return_value = {
                "files": [
                    {"name": "per_atlanta-constitution_1922-01-01_54_203_djvu.txt", "format": "DjVuTXT"}
                ]
            }
        elif "1922-01-02" in url:
            mock_resp.json.return_value = {
                "files": [
                    {"name": "per_atlanta-constitution_1922-01-02_54_204_djvu.txt", "format": "DjVuTXT"}
                ]
            }
        else:
            mock_resp.json.return_value = {"files": []}
            
        return mock_resp
        
    with patch("requests.get", side_effect=mock_get_response) as mock_get:
        yield mock_get


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for download commands."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        yield mock_run


class TestPrepareAtlantaConstitutionDataset:
    """Tests for the Atlanta Constitution dataset preparation script."""

    def test_search_issues(self, mock_requests):
        """Test searching for issues."""
        # Arrange
        start_date = datetime(1922, 1, 1)
        end_date = datetime(1922, 1, 2)
        
        # Act
        results = search_issues(start_date, end_date)
        
        # Assert
        assert len(results) == 2
        assert results[0]["identifier"] == "per_atlanta-constitution_1922-01-01_54_203"
        assert results[1]["identifier"] == "per_atlanta-constitution_1922-01-02_54_204"
        # Verify API request
        assert mock_requests.call_count == 1
        assert "atlanta-constitution" in mock_requests.call_args[0][0]  # URL contains atlanta-constitution

    def test_check_ocr_availability(self, mock_metadata_response):
        """Test checking OCR availability."""
        # Arrange
        issues = [
            {
                "identifier": "per_atlanta-constitution_1922-01-01_54_203",
                "title": "Atlanta Constitution, January 1, 1922"
            },
            {
                "identifier": "per_atlanta-constitution_1922-01-02_54_204",
                "title": "Atlanta Constitution, January 2, 1922"
            }
        ]
        
        # Act
        ocr_issues = check_ocr_availability(issues)
        
        # Assert
        assert len(ocr_issues) == 2
        assert ocr_issues[0]["identifier"] == "per_atlanta-constitution_1922-01-01_54_203"
        assert ocr_issues[0]["has_ocr"] is True
        assert ocr_issues[1]["identifier"] == "per_atlanta-constitution_1922-01-02_54_204"
        assert ocr_issues[1]["has_ocr"] is True
        # Verify API calls
        assert mock_metadata_response.call_count == 2

    def test_save_issues_file(self, tmp_path):
        """Test saving issues to file."""
        # Arrange
        issues = [
            {
                "identifier": "per_atlanta-constitution_1922-01-01_54_203",
                "title": "Atlanta Constitution, January 1, 1922",
                "has_ocr": True
            }
        ]
        output_dir = tmp_path
        filename = "test_issues.json"
        
        # Act
        with patch("pathlib.Path.mkdir"):
            output_file = save_issues_file(issues, output_dir, filename)
            
        # Assert
        assert output_file == output_dir / filename
        # Verify file was created with correct content
        with open(output_dir / filename, "r") as f:
            saved_data = json.load(f)
            assert "issues" in saved_data
            assert len(saved_data["issues"]) == 1
            assert saved_data["issues"][0] == "per_atlanta-constitution_1922-01-01_54_203"

    @patch("scripts.prepare_atlanta_constitution_dataset.search_issues")
    @patch("scripts.prepare_atlanta_constitution_dataset.check_ocr_availability")
    @patch("scripts.prepare_atlanta_constitution_dataset.save_issues_file")
    @patch("scripts.prepare_atlanta_constitution_dataset.download_sample")
    def test_prepare_dataset(
        self, mock_download, mock_save, mock_check_ocr, mock_search
    ):
        """Test preparing a dataset."""
        # Arrange
        start_date = datetime(1922, 1, 1)
        end_date = datetime(1922, 1, 2)
        output_dir = Path("test_output")
        sample_size = 2
        
        # Setup mocks
        mock_search.return_value = [
            {"identifier": "issue1", "title": "Issue 1"},
            {"identifier": "issue2", "title": "Issue 2"}
        ]
        mock_check_ocr.return_value = [
            {"identifier": "issue1", "title": "Issue 1", "has_ocr": True},
            {"identifier": "issue2", "title": "Issue 2", "has_ocr": True}
        ]
        mock_save.return_value = output_dir / "test_issues.json"
        
        # Act
        result = prepare_dataset(
            start_date=start_date,
            end_date=end_date,
            output_dir=output_dir,
            sample_size=sample_size
        )
        
        # Assert
        assert result == output_dir / "test_issues.json"
        assert mock_search.call_count == 1
        assert mock_check_ocr.call_count == 1
        assert mock_save.call_count == 1
        assert mock_download.call_count == 1  # Should download sample issues

    @patch("scripts.prepare_atlanta_constitution_dataset.prepare_dataset")
    @patch("scripts.prepare_atlanta_constitution_dataset.parse_args")
    def test_main(self, mock_parse_args, mock_prepare_dataset):
        """Test the main function."""
        # Arrange
        args = MagicMock()
        args.start_date = "1922-01-01"
        args.end_date = "1922-01-31"
        args.output_dir = "data/test"
        args.sample_size = 2
        args.run_test = False
        mock_parse_args.return_value = args
        
        mock_prepare_dataset.return_value = Path("data/test/issues.json")
        
        # Act
        with patch("sys.argv", ["program_name"]):
            main()
            
        # Assert
        assert mock_prepare_dataset.call_count == 1
        assert mock_prepare_dataset.call_args[1]["start_date"] == datetime(1922, 1, 1)
        assert mock_prepare_dataset.call_args[1]["end_date"] == datetime(1922, 1, 31)
        assert mock_prepare_dataset.call_args[1]["output_dir"] == Path("data/test")
        assert mock_prepare_dataset.call_args[1]["sample_size"] == 2 