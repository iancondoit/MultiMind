"""
Integration tests for processing Atlanta Constitution newspaper issues.

These tests verify that the StoryDredge pipeline can successfully process
issues from the Atlanta Constitution newspaper archive.
"""

import os
import sys
import pytest
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Ensure we can import from project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.pipeline.batch_processor import BatchProcessor
from src.fetcher.archive_fetcher import ArchiveFetcher


# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atlanta_test")


@pytest.fixture
def sample_issues_file(tmp_path):
    """
    Create a temporary sample issues file for testing.
    
    This fixture creates a minimal issues file with just one or two issues
    for testing the pipeline without requiring a full dataset.
    """
    # Define test issues - you can replace with actual archive.org IDs for testing
    issues = ["pub_atlanta-constitution_19220101", "pub_atlanta-constitution_19220102"]
    
    # Create the issues file
    issues_file = tmp_path / "test_atlanta_issues.json"
    with open(issues_file, 'w') as f:
        json.dump({"issues": issues}, f)
    
    return issues_file


class TestAtlantaConstitution:
    """Tests for processing Atlanta Constitution issues."""
    
    def test_fetch_atlanta_issue(self, tmp_path):
        """Test fetching a single Atlanta Constitution issue."""
        # Use a real issue ID for testing
        issue_id = "pub_atlanta-constitution_19220101"
        
        # Initialize the fetcher with a test cache directory
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir(exist_ok=True)
        
        # Fetch the issue
        fetcher = ArchiveFetcher(cache_dir=cache_dir)
        result = fetcher.fetch_issue(issue_id)
        
        # Verify the result
        assert result is not None, f"Failed to fetch {issue_id}"
        assert result.exists(), f"OCR file not found at {result}"
        
        # Check that the file has content
        file_size = result.stat().st_size
        assert file_size > 0, f"OCR file is empty ({file_size} bytes)"
        
        # Check that we can read the file
        with open(result, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read(1000)  # Read first 1000 characters
        
        assert len(content) > 0, "Could not read content from OCR file"
        logger.info(f"Successfully fetched and read OCR from {issue_id}")
    
    def test_process_single_atlanta_issue(self, tmp_path):
        """Test processing a single Atlanta Constitution issue through the pipeline."""
        # Use a real issue ID for testing
        issue_id = "pub_atlanta-constitution_19220101"
        
        # Set up output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Initialize batch processor
        processor = BatchProcessor(
            output_dir=str(output_dir),
            checkpoint_file=str(tmp_path / "checkpoint.json")
        )
        
        # Process the issue
        success = processor.process_issue(issue_id)
        
        # Verify the result
        assert success, f"Failed to process issue {issue_id}"
        
        # Check that output was generated
        issue_output_dir = output_dir / issue_id
        assert issue_output_dir.exists(), f"Output directory not created for {issue_id}"
        
        # Check that we have raw and cleaned text
        raw_file = issue_output_dir / "raw.txt"
        cleaned_file = issue_output_dir / "cleaned.txt"
        
        assert raw_file.exists(), "Raw OCR file not found"
        assert cleaned_file.exists(), "Cleaned OCR file not found"
        
        # Check that articles were extracted
        articles_dir = issue_output_dir / "articles"
        assert articles_dir.exists(), "Articles directory not found"
        
        article_files = list(articles_dir.glob("*.json"))
        assert len(article_files) > 0, "No articles were extracted"
        
        logger.info(f"Successfully processed issue {issue_id} and found {len(article_files)} articles")
    
    def test_batch_process_atlanta_issues(self, sample_issues_file, tmp_path):
        """Test batch processing of Atlanta Constitution issues."""
        # Set up output directory
        output_dir = tmp_path / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Initialize batch processor
        processor = BatchProcessor(
            output_dir=str(output_dir),
            checkpoint_file=str(tmp_path / "checkpoint.json")
        )
        
        # Load the issues file
        with open(sample_issues_file, 'r') as f:
            issues_data = json.load(f)
        
        issue_ids = issues_data.get("issues", [])
        assert len(issue_ids) > 0, "No issues found in sample file"
        
        # Process the batch
        results = processor.process_batch(issue_ids)
        
        # Verify the results
        assert results is not None, "Batch processing returned None"
        assert "successful" in results, "Results missing 'successful' count"
        assert "failed" in results, "Results missing 'failed' count"
        
        success_count = results["successful"]
        failed_count = results["failed"]
        
        assert success_count > 0, "No issues were successfully processed"
        assert failed_count == 0, f"{failed_count} issues failed processing"
        
        # Check for HSA-ready output
        hsa_dir = output_dir / "hsa-ready"
        assert hsa_dir.exists(), "HSA-ready directory not found"
        
        # Find JSON files in the HSA output directory (recursively)
        hsa_files = list(hsa_dir.glob("**/*.json"))
        assert len(hsa_files) > 0, "No HSA-ready JSON files were created"
        
        logger.info(f"Successfully processed {success_count} issues with {len(hsa_files)} total articles")
        
        # Verify the structure of one HSA file
        if hsa_files:
            with open(hsa_files[0], 'r') as f:
                article_data = json.load(f)
            
            # Check required HSA fields
            required_fields = ["headline", "body", "timestamp", "publication", "source_issue"]
            for field in required_fields:
                assert field in article_data, f"Required HSA field '{field}' missing"


if __name__ == "__main__":
    # This allows running the tests directly with more detailed output
    pytest.main(["-xvs", __file__]) 