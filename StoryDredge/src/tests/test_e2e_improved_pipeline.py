"""
End-to-end test for the improved pipeline.

This test verifies that all the improvements work together correctly:
1. Fast rule-based classification
2. Entity extraction and tagging
3. Proper directory structure
"""

import os
import sys
import json
import shutil
import pytest
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline.process_ocr import process_ocr


class TestImprovedPipeline:
    """End-to-end tests for the improved pipeline."""

    @pytest.fixture
    def setup_test_environment(self, tmp_path):
        """Set up a test environment with sample data."""
        test_dir = tmp_path / "test_output"
        test_dir.mkdir(exist_ok=True)
        
        # Create a mock issue directory
        issue_id = "per_test-newspaper_1922-01-01_54_001"
        issue_dir = test_dir / "temp" / issue_id
        issue_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a mock raw.txt file
        raw_text = """
TEST NEWSPAPER
January 1, 1922

MAYOR SMITH ANNOUNCES NEW BUDGET

Mayor John Smith announced the new city budget yesterday. 
The $10 million budget includes funding for infrastructure and education.
City Council will vote on the proposal next week.
City Hall officials expressed support for the mayor's plan.

LOCAL TEAM WINS CHAMPIONSHIP

The Atlanta Hawks defeated the Boston Celtics 105-98 in the championship game on Sunday.
Star player Michael Jordan scored 42 points to lead his team to victory.
Coach Phil Jackson praised the team's performance.
The game was played at Atlanta Arena in front of a sold-out crowd.

STOCK MARKET HITS RECORD HIGH

The Dow Jones Industrial Average reached a record high of 25,000 points yesterday.
Technology stocks led the gains, with Apple and Microsoft both up over 3%.
Analysts at Goldman Sachs predict continued growth through the year.
Wall Street traders celebrated the milestone.
"""
        raw_path = issue_dir / "raw.txt"
        with open(raw_path, "w") as f:
            f.write(raw_text)
        
        # Return the test directory and issue ID
        return {
            "test_dir": test_dir,
            "issue_id": issue_id,
            "raw_path": raw_path
        }
    
    def test_e2e_pipeline(self, setup_test_environment, monkeypatch):
        """Test the entire pipeline end-to-end with all improvements."""
        test_env = setup_test_environment
        test_dir = test_env["test_dir"]
        issue_id = test_env["issue_id"]
        
        # Start timer for performance testing
        start_time = time.time()
        
        # Run the pipeline
        result = process_ocr(
            issue_id=issue_id,
            output_dir=str(test_dir),
            skip_fetch=True,  # Skip fetch since we created the raw.txt file
            skip_extraction=False,
            skip_classification=False,
            skip_formatting=False,
            fast_mode=True  # Use fast rule-based classification
        )
        
        # End timer
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Check that the pipeline completed successfully
        assert result is True, "Pipeline should complete successfully"
        
        # Check that the pipeline was fast (under 2 seconds)
        assert processing_time < 2, f"Pipeline should be fast (took {processing_time:.2f}s)"
        
        # Check directory structure
        assert (test_dir / "temp").exists(), "Temp directory should exist"
        assert (test_dir / "temp" / issue_id).exists(), "Issue temp directory should exist"
        assert (test_dir / "temp" / issue_id / "articles").exists(), "Articles directory should exist"
        assert (test_dir / "temp" / issue_id / "classified").exists(), "Classified directory should exist"
        
        # Check that issue directory is not in the main output
        assert not (test_dir / issue_id).exists(), "Issue directory should not be in main output"
        
        # Check HSA-ready directory structure
        assert (test_dir / "hsa-ready").exists(), "HSA-ready directory should exist"
        assert (test_dir / "hsa-ready" / "1922").exists(), "Year directory should exist"
        assert (test_dir / "hsa-ready" / "1922" / "01").exists(), "Month directory should exist"
        assert (test_dir / "hsa-ready" / "1922" / "01" / "01").exists(), "Day directory should exist"
        
        # Check that no nested hsa-ready directory exists
        assert not (test_dir / "hsa-ready" / "hsa-ready").exists(), "No nested hsa-ready directory should exist"
        
        # Check HSA-ready files
        hsa_files = list(Path(test_dir / "hsa-ready" / "1922" / "01" / "01").glob("*.json"))
        assert len(hsa_files) >= 3, f"Should create at least 3 HSA-ready files, found {len(hsa_files)}"
        
        # Check entity extraction in HSA-ready files
        entity_found = False
        for hsa_file in hsa_files:
            with open(hsa_file, "r") as f:
                article = json.load(f)
            
            # Check that tags field exists
            assert "tags" in article, "HSA article should have tags field"
            
            # Check for entities in tags (in at least one file)
            tags = article["tags"]
            for tag in tags:
                if tag in ["John Smith", "City Council", "City Hall", "Michael Jordan", "Atlanta Hawks", 
                          "Phil Jackson", "Atlanta", "Boston Celtics", "Apple", "Microsoft", "Goldman Sachs"]:
                    entity_found = True
                    break
        
        assert entity_found, "At least one entity should be found in the tags"
        
        # Check for artifacts to clean up
        return {
            "test_dir": test_dir,
        }

    def teardown_method(self, method):
        """Clean up after test."""
        if hasattr(method, "test_dir") and method.test_dir.exists():
            shutil.rmtree(method.test_dir) 