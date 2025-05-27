"""
Tests for the BatchProcessor class.
"""

import os
import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.pipeline.batch_processor import BatchProcessor


class TestBatchProcessor:
    """Test cases for the BatchProcessor class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name) / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        self.checkpoint_file = Path(self.temp_dir.name) / "checkpoint.json"
        
        # Mock config manager
        self.config_patcher = patch('src.pipeline.batch_processor.get_config_manager')
        self.mock_config = self.config_patcher.start()
        self.mock_config.return_value.config = MagicMock()
        self.mock_config.return_value.load = MagicMock()
        
        # Mock pipeline components
        self.fetcher_patcher = patch('src.pipeline.batch_processor.ArchiveFetcher')
        self.cleaner_patcher = patch('src.pipeline.batch_processor.OCRCleaner')
        self.splitter_patcher = patch('src.pipeline.batch_processor.ArticleSplitter')
        self.classifier_patcher = patch('src.pipeline.batch_processor.ArticleClassifier')
        
        self.mock_fetcher = self.fetcher_patcher.start()
        self.mock_cleaner = self.cleaner_patcher.start()
        self.mock_splitter = self.splitter_patcher.start()
        self.mock_classifier = self.classifier_patcher.start()
        
        # Initialize actual mock instances
        self.mock_fetcher_instance = MagicMock()
        self.mock_cleaner_instance = MagicMock()
        self.mock_splitter_instance = MagicMock()
        self.mock_classifier_instance = MagicMock()
        
        self.mock_fetcher.return_value = self.mock_fetcher_instance
        self.mock_cleaner.return_value = self.mock_cleaner_instance
        self.mock_splitter.return_value = self.mock_splitter_instance
        self.mock_classifier.return_value = self.mock_classifier_instance
        
        # Configure mock behavior
        self.mock_fetcher_instance.fetch_issue.return_value = "Raw OCR text"
        self.mock_cleaner_instance.clean_text.return_value = "Cleaned OCR text"
        self.mock_splitter_instance.split_articles.return_value = [
            {"title": "Article 1", "raw_text": "Content 1"},
            {"title": "Article 2", "raw_text": "Content 2"}
        ]
        self.mock_classifier_instance.classify_batch.return_value = [
            {"title": "Article 1", "raw_text": "Content 1", "category": "News"},
            {"title": "Article 2", "raw_text": "Content 2", "category": "Sports"}
        ]
        
    def teardown_method(self):
        """Tear down test environment."""
        self.temp_dir.cleanup()
        self.config_patcher.stop()
        self.fetcher_patcher.stop()
        self.cleaner_patcher.stop()
        self.splitter_patcher.stop()
        self.classifier_patcher.stop()
        
    def test_init(self):
        """Test initialization of BatchProcessor."""
        processor = BatchProcessor(
            output_dir=str(self.output_dir),
            checkpoint_file=str(self.checkpoint_file)
        )
        
        assert processor.output_dir == self.output_dir
        assert processor.checkpoint_file == self.checkpoint_file
        assert processor.enable_checkpointing is True
        assert processor.max_retries == 3
        assert isinstance(processor.processed_issues, set)
        assert isinstance(processor.failed_issues, set)
        
    def test_process_issue(self):
        """Test processing a single issue."""
        processor = BatchProcessor(
            output_dir=str(self.output_dir),
            checkpoint_file=str(self.checkpoint_file)
        )
        
        # Process a test issue
        result = processor.process_issue("test_issue_123")
        
        # Check result
        assert result is True
        assert "test_issue_123" in processor.processed_issues
        
        # Verify all pipeline steps were called
        self.mock_fetcher_instance.fetch_issue.assert_called_once_with("test_issue_123")
        self.mock_cleaner_instance.clean_text.assert_called_once()
        self.mock_splitter_instance.split_articles.assert_called_once()
        self.mock_classifier_instance.classify_batch.assert_called_once()
        
        # Verify output directory structure
        issue_dir = self.output_dir / "test_issue_123"
        assert issue_dir.exists()
        assert (issue_dir / "raw.txt").exists()
        assert (issue_dir / "cleaned.txt").exists()
        assert (issue_dir / "articles").exists()
        assert (issue_dir / "classified").exists()
        
        # Verify checkpoint was saved
        assert self.checkpoint_file.exists()
        with open(self.checkpoint_file, "r") as f:
            checkpoint = json.load(f)
            assert "test_issue_123" in checkpoint["processed_issues"]
            
    def test_process_issue_error(self):
        """Test error handling during issue processing."""
        processor = BatchProcessor(
            output_dir=str(self.output_dir),
            checkpoint_file=str(self.checkpoint_file)
        )
        
        # Make fetcher raise an exception
        self.mock_fetcher_instance.fetch_issue.side_effect = Exception("Test error")
        
        # Process a test issue
        result = processor.process_issue("error_issue_456")
        
        # Check result
        assert result is False
        assert "error_issue_456" not in processor.processed_issues
        assert "error_issue_456" in processor.failed_issues
        
    def test_process_batch(self):
        """Test processing a batch of issues."""
        processor = BatchProcessor(
            output_dir=str(self.output_dir),
            checkpoint_file=str(self.checkpoint_file)
        )
        
        # Configure different responses for different issues
        def mock_fetch(issue_id):
            if issue_id == "fail_issue":
                raise Exception("Test failure")
            return f"Raw OCR text for {issue_id}"
        
        self.mock_fetcher_instance.fetch_issue.side_effect = mock_fetch
        
        # Create a batch of issues
        issue_ids = ["issue1", "issue2", "fail_issue", "issue3"]
        
        # Mock progress reporter
        with patch('src.pipeline.batch_processor.ProgressReporter') as mock_progress:
            mock_progress_instance = MagicMock()
            mock_progress.return_value = mock_progress_instance
            
            # Process the batch
            report = processor.process_batch(issue_ids)
            
            # Check report
            assert report["total_issues"] == 4
            assert report["successful"] == 3
            assert report["failed"] == 1
            assert report["skipped"] == 0
            assert "fail_issue" in report["failed_issues"]
            
            # Verify progress reporting
            assert mock_progress_instance.update.call_count == 4
            
    def test_load_checkpoint(self):
        """Test loading checkpoint file."""
        # Create a checkpoint file
        checkpoint_data = {
            "processed_issues": ["issue1", "issue2"],
            "failed_issues": ["issue3"],
            "timestamp": "2023-01-01T12:00:00"
        }
        
        with open(self.checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f)
            
        processor = BatchProcessor(
            output_dir=str(self.output_dir),
            checkpoint_file=str(self.checkpoint_file)
        )
        
        # Check that issues were loaded
        assert "issue1" in processor.processed_issues
        assert "issue2" in processor.processed_issues
        assert len(processor.processed_issues) == 2
        
    def test_checkpointing_disabled(self):
        """Test batch processor with checkpointing disabled."""
        processor = BatchProcessor(
            output_dir=str(self.output_dir),
            checkpoint_file=str(self.checkpoint_file),
            enable_checkpointing=False
        )
        
        # Process a test issue
        processor.process_issue("test_issue_789")
        
        # Verify checkpoint was not saved
        assert not self.checkpoint_file.exists()
        
    def test_skip_already_processed(self):
        """Test skipping already processed issues."""
        # Create a checkpoint file
        checkpoint_data = {
            "processed_issues": ["already_done"],
            "failed_issues": [],
            "timestamp": "2023-01-01T12:00:00"
        }
        
        with open(self.checkpoint_file, "w") as f:
            json.dump(checkpoint_data, f)
            
        processor = BatchProcessor(
            output_dir=str(self.output_dir),
            checkpoint_file=str(self.checkpoint_file)
        )
        
        # Try to process the already processed issue
        result = processor.process_issue("already_done")
        
        # Check result
        assert result is True
        
        # Verify fetcher was not called
        self.mock_fetcher_instance.fetch_issue.assert_not_called()
        
    def test_retry_logic(self):
        """Test retry logic for failed issues."""
        processor = BatchProcessor(
            output_dir=str(self.output_dir),
            checkpoint_file=str(self.checkpoint_file),
            max_retries=2
        )
    
        # Configure mock behavior for process_issue
        # The processor will use a separate process_issue method for the retry
        # so we need to mock the entire method
        original_process_issue = processor.process_issue
        attempt_count = 0
        
        def mock_process_issue(issue_id):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                return False  # First attempt fails
            return True  # Second attempt succeeds
            
        processor.process_issue = mock_process_issue
    
        # First, let's completely replace the ProgressReporter with a mock
        mock_progress = MagicMock()
        
        # Process a batch with the test issue
        with patch('src.pipeline.batch_processor.ProgressReporter', return_value=mock_progress):
            with patch('src.pipeline.batch_processor.time.sleep'):  # Don't actually sleep in tests
                result = processor.process_batch(["retry_issue"])
    
        # Check that the issue was successfully processed on retry
        assert attempt_count == 2  # Should have attempted twice
        assert "retry_issue" in result["successful_issues"]
        assert len(result["failed_issues"]) == 0
        
        # Restore original method
        processor.process_issue = original_process_issue 