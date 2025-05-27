"""
Tests for the run_atlanta_constitution_test.py script.

These tests verify the functionality of the script that runs Atlanta Constitution tests.
"""

import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.run_atlanta_constitution_test import main


@pytest.fixture
def mock_prepare_dataset():
    """Mock the prepare_dataset function."""
    with patch("scripts.run_atlanta_constitution_test.prepare_dataset") as mock_prepare:
        mock_prepare.return_value = Path("data/atlanta-constitution/sample_issues.json")
        yield mock_prepare


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for running commands."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        yield mock_run


@pytest.fixture
def mock_path_exists():
    """Mock Path.exists to return True."""
    with patch("pathlib.Path.exists", return_value=True) as mock_exists:
        yield mock_exists


@pytest.fixture
def mock_path_mkdir():
    """Mock Path.mkdir."""
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        yield mock_mkdir


@pytest.fixture
def mock_logging():
    """Mock logging."""
    with patch("scripts.run_atlanta_constitution_test.logging") as mock_log:
        yield mock_log


class TestRunAtlantaConstitutionTest:
    """Tests for the run_atlanta_constitution_test.py script."""

    @patch("scripts.run_atlanta_constitution_test.parse_args")
    def test_main_prepare_only(
        self, 
        mock_parse_args, 
        mock_prepare_dataset, 
        mock_subprocess,
        mock_path_exists,
        mock_path_mkdir,
        mock_logging
    ):
        """Test main function with prepare flag only."""
        # Arrange
        args = MagicMock()
        args.prepare = True
        args.test = False
        args.run_pipeline = False
        args.start_date = "1922-01-01"
        args.end_date = "1922-01-31"
        args.sample_size = 2
        mock_parse_args.return_value = args
        
        # Act
        with patch("sys.argv", ["program_name"]):
            main()
            
        # Assert
        assert mock_prepare_dataset.call_count == 1
        assert mock_subprocess.call_count == 0  # No commands should be run
        
    @patch("scripts.run_atlanta_constitution_test.parse_args")
    def test_main_with_test(
        self, 
        mock_parse_args, 
        mock_prepare_dataset, 
        mock_subprocess,
        mock_path_exists,
        mock_path_mkdir,
        mock_logging
    ):
        """Test main function with test flag."""
        # Arrange
        args = MagicMock()
        args.prepare = False
        args.test = True
        args.run_pipeline = False
        args.start_date = "1922-01-01"
        args.end_date = "1922-01-31"
        args.sample_size = 2
        mock_parse_args.return_value = args
        
        # Act
        with patch("sys.argv", ["program_name"]):
            with patch("json.load", return_value={"issues": ["issue1", "issue2"]}):
                with patch("builtins.open", MagicMock()):
                    main()
            
        # Assert
        assert mock_prepare_dataset.call_count == 0  # No preparation
        assert mock_subprocess.call_count >= 1  # At least one command (pytest)
        # Check that pytest was called
        assert any("pytest" in str(call_args) for call_args in mock_subprocess.call_args_list)
        
    @patch("scripts.run_atlanta_constitution_test.parse_args")
    def test_main_with_run_pipeline(
        self, 
        mock_parse_args, 
        mock_prepare_dataset, 
        mock_subprocess,
        mock_path_exists,
        mock_path_mkdir,
        mock_logging
    ):
        """Test main function with run_pipeline flag."""
        # Arrange
        args = MagicMock()
        args.prepare = False
        args.test = False
        args.run_pipeline = True
        args.start_date = "1922-01-01"
        args.end_date = "1922-01-31"
        args.sample_size = 2
        args.workers = 1
        mock_parse_args.return_value = args
        
        # Act
        with patch("sys.argv", ["program_name"]):
            with patch("json.load", return_value={"issues": ["issue1", "issue2"]}):
                with patch("builtins.open", MagicMock()):
                    main()
            
        # Assert
        assert mock_prepare_dataset.call_count == 0  # No preparation
        assert mock_subprocess.call_count >= 1  # At least one command
        # Check that pipeline/main.py was called
        pipeline_calls = [
            call_args for call_args in mock_subprocess.call_args_list 
            if "pipeline/main.py" in str(call_args)
        ]
        assert len(pipeline_calls) >= 1
        
    @patch("scripts.run_atlanta_constitution_test.parse_args")
    def test_main_with_all_flags(
        self, 
        mock_parse_args, 
        mock_prepare_dataset, 
        mock_subprocess,
        mock_path_exists,
        mock_path_mkdir,
        mock_logging
    ):
        """Test main function with all flags enabled."""
        # Arrange
        args = MagicMock()
        args.prepare = True
        args.test = True
        args.run_pipeline = True
        args.start_date = "1922-01-01"
        args.end_date = "1922-01-31"
        args.sample_size = 2
        args.workers = 2
        mock_parse_args.return_value = args
        
        # Act
        with patch("sys.argv", ["program_name"]):
            with patch("json.load", return_value={"issues": ["issue1", "issue2"]}):
                with patch("builtins.open", MagicMock()):
                    main()
            
        # Assert
        assert mock_prepare_dataset.call_count == 1  # Preparation called
        assert mock_subprocess.call_count >= 2  # At least two commands (test + pipeline)
        # Check that both pytest and pipeline calls were made
        pytest_calls = [
            call_args for call_args in mock_subprocess.call_args_list 
            if "pytest" in str(call_args)
        ]
        pipeline_calls = [
            call_args for call_args in mock_subprocess.call_args_list 
            if "pipeline/main.py" in str(call_args)
        ]
        assert len(pytest_calls) >= 1
        assert len(pipeline_calls) >= 1 