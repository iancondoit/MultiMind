"""
Test the directory structure improvements in the pipeline.

These tests verify that:
1. The pipeline uses the temporary directory for intermediate files
2. The pipeline produces output in the correct hsa-ready directory structure
3. No duplicate directory structures are created
"""

import os
import sys
import shutil
import json
import pytest
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.classifier.article_classifier import ArticleClassifier
from src.formatter.hsa_formatter import HSAFormatter
from pipeline.process_ocr import process_ocr


class TestDirectoryStructure:
    """Tests for the pipeline directory structure improvements."""

    @pytest.fixture
    def setup_test_environment(self, tmp_path):
        """Set up a test environment with sample data."""
        test_dir = tmp_path / "test_output"
        test_dir.mkdir(exist_ok=True)
        
        # Create mock articles directory and files
        issue_id = "test_issue_1922-01-01_54_001"
        
        # Return the test directories and issue ID
        yield {
            "test_dir": test_dir,
            "issue_id": issue_id
        }
        
        # Clean up after test
        shutil.rmtree(test_dir)
    
    def test_process_ocr_directory_structure(self, setup_test_environment, monkeypatch):
        """Test that process_ocr creates the correct directory structure."""
        test_env = setup_test_environment
        test_dir = test_env["test_dir"]
        issue_id = test_env["issue_id"]
        
        # Mock the fetch and extraction functions to avoid actual API calls
        def mock_fetch(*args, **kwargs):
            # Create a mock raw.txt file
            raw_path = test_dir / "temp" / issue_id / "raw.txt"
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            with open(raw_path, "w") as f:
                f.write("Sample OCR text for testing\n\nARTICLE 1\n\nThis is a test article.")
            return True
            
        def mock_extract_articles(*args, **kwargs):
            # Create a mock article file
            articles_dir = test_dir / "temp" / issue_id / "articles"
            articles_dir.mkdir(parents=True, exist_ok=True)
            
            article = {
                "title": "Test Article",
                "raw_text": "This is a test article.",
                "source_issue": issue_id,
                "_file_name": "article_0001.json"
            }
            
            with open(articles_dir / "article_0001.json", "w") as f:
                json.dump(article, f)
                
            return [article]
            
        # Mock the necessary functions
        monkeypatch.setattr("src.utils.archive.fetch_ocr_for_issue", mock_fetch)
        monkeypatch.setattr("src.extractor.article_extractor.ArticleExtractor.extract_articles", 
                          mock_extract_articles)
        
        # Run the process_ocr function
        result = process_ocr(
            issue_id=issue_id,
            output_dir=str(test_dir),
            skip_fetch=False,
            skip_extraction=False,
            skip_classification=False,
            skip_formatting=False,
            fast_mode=True
        )
        
        assert result is True, "Process OCR should complete successfully"
        
        # Check temp directory structure
        assert (test_dir / "temp").exists(), "Temp directory should exist"
        assert (test_dir / "temp" / issue_id).exists(), "Issue temp directory should exist"
        assert (test_dir / "temp" / issue_id / "articles").exists(), "Articles directory should exist"
        assert (test_dir / "temp" / issue_id / "classified").exists(), "Classified directory should exist"
        
        # Check hsa-ready directory structure
        assert (test_dir / "hsa-ready").exists(), "HSA-ready directory should exist"
        assert (test_dir / "hsa-ready" / "1922").exists(), "Year directory should exist"
        assert (test_dir / "hsa-ready" / "1922" / "01").exists(), "Month directory should exist"
        assert (test_dir / "hsa-ready" / "1922" / "01" / "01").exists(), "Day directory should exist"
        
        # Verify that no issue_id directory exists directly in output_dir
        assert not (test_dir / issue_id).exists(), "Issue directory should not exist in main output dir"
        
        # Verify that no nested hsa-ready directory exists
        assert not (test_dir / "hsa-ready" / "hsa-ready").exists(), "No nested hsa-ready directory should exist"
    
    def test_hsa_formatter_output_paths(self):
        """Test that HSAFormatter creates correct output paths."""
        formatter = HSAFormatter(output_dir=Path("output"))
        
        # Test with standard output directory
        assert formatter.output_dir == Path("output/hsa-ready"), "Should add hsa-ready to path"
        
        # Test with output directory already ending with hsa-ready
        formatter = HSAFormatter(output_dir=Path("output/hsa-ready"))
        assert formatter.output_dir == Path("output/hsa-ready"), "Should not add duplicate hsa-ready"
        
        # Create a test article
        article = {
            "headline": "Test Article",
            "body": "This is a test article.",
            "timestamp": "1922-01-01T00:00:00.000Z",
            "source_issue": "test_issue_1922-01-01_54_001",
            "tags": ["news"],
            "section": "news",
            "publication": "Test Newspaper",
            "source_url": "https://example.com"
        }
        
        # Get the output path
        output_path = formatter.get_output_path(article)
        
        # Check path components
        assert "1922" in str(output_path), "Should contain year"
        assert "01" in str(output_path), "Should contain month"
        assert "01" in str(output_path), "Should contain day"
        assert "test_article_" in str(output_path), "Should contain sanitized headline" 