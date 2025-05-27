"""
Tests for the ArticleSplitter class.
"""

import pytest
from pathlib import Path
import json

# The class we'll implement
from src.splitter.article_splitter import ArticleSplitter


class TestArticleSplitter:
    """Test cases for ArticleSplitter."""
    
    def test_init(self):
        """Test initialization of ArticleSplitter."""
        # ArticleSplitter should accept parameters to customize splitting
        splitter = ArticleSplitter(aggressive_mode=False)
        assert splitter.aggressive_mode is False
        
        splitter = ArticleSplitter(aggressive_mode=True)
        assert splitter.aggressive_mode is True
    
    def test_detect_headlines(self, sample_ocr_text):
        """Test headline detection in OCR text."""
        # Expected headlines in the sample text
        expected_headlines = [
            "LOCAL COUNCIL APPROVES NEW BUDGET",
            "WEATHER FORECAST",
            "CLASSIFIED ADVERTISEMENTS"
        ]
        
        splitter = ArticleSplitter()
        headlines = splitter.detect_headlines(sample_ocr_text)
        
        # Verify headline detection
        detected_headlines = [h[2] for h in headlines]  # Extract headline text
        for expected in expected_headlines:
            assert any(expected in headline for headline in detected_headlines)
    
    def test_detect_headlines_aggressive(self, sample_ocr_text):
        """Test aggressive headline detection."""
        splitter = ArticleSplitter(aggressive_mode=True)
        headlines = splitter.detect_headlines(sample_ocr_text)
        
        # Aggressive mode should detect more potential headlines
        assert len(headlines) >= 3  # At least the obvious ones
    
    def test_extract_articles(self, sample_ocr_text):
        """Test article extraction from headlines."""
        splitter = ArticleSplitter()
        headlines = splitter.detect_headlines(sample_ocr_text)
        articles = splitter.extract_articles(sample_ocr_text, headlines)
        
        # Verify article extraction
        assert len(articles) >= 3  # At least 3 articles
        
        # Check article structure
        for article in articles:
            assert "title" in article
            assert "raw_text" in article
            assert len(article["raw_text"]) > 0
    
    def test_extract_articles_empty_headlines(self, sample_ocr_text):
        """Test article extraction with no headlines detected."""
        splitter = ArticleSplitter()
        articles = splitter.extract_articles(sample_ocr_text, [])
        
        # Should create a fallback article with the entire text
        assert len(articles) == 1
        assert "title" in articles[0]
        assert "raw_text" in articles[0]
        assert articles[0]["raw_text"] == sample_ocr_text.strip()
    
    def test_extract_articles_aggressive(self, sample_ocr_text):
        """Test aggressive article extraction."""
        splitter = ArticleSplitter(aggressive_mode=True)
        headlines = splitter.detect_headlines(sample_ocr_text)
        articles = splitter.extract_articles(sample_ocr_text, headlines)
        
        # Aggressive mode might detect more articles
        assert len(articles) >= 3
    
    def test_split_file(self, test_data_dir, temp_dir):
        """Test splitting a file into articles."""
        # Setup
        input_file = test_data_dir / "sample_ocr.txt"
        output_dir = temp_dir / "articles"
        
        splitter = ArticleSplitter()
        result = splitter.split_file(
            input_file, 
            output_dir, 
            metadata={
                "date": "1977-06-14",
                "publication": "San Antonio Express",
                "archive_id": "san-antonio-express-1977-06-14"
            }
        )
        
        # Verify results
        assert len(result) >= 3  # At least 3 articles
        assert output_dir.exists()
        
        # Check output files
        for article_path in result:
            assert article_path.exists()
            
            with open(article_path, 'r') as f:
                article = json.load(f)
                assert "title" in article
                assert "raw_text" in article
                assert "date" in article
                assert "publication" in article
                assert "archive_id" in article
    
    def test_split_file_nonexistent(self, test_data_dir, temp_dir):
        """Test handling of nonexistent input file."""
        splitter = ArticleSplitter()
        result = splitter.split_file(
            test_data_dir / "nonexistent.txt",
            temp_dir / "articles"
        )
        
        assert result == []
    
    def test_verify_ocr_quality(self, sample_ocr_text):
        """Test OCR quality verification."""
        splitter = ArticleSplitter()
        quality_good = splitter.verify_ocr_quality(sample_ocr_text)
        
        # Our sample should have good quality
        assert quality_good is True
        
        # Test poor quality text
        poor_text = "Short text with few\nproblems."
        quality_good = splitter.verify_ocr_quality(poor_text)
        assert quality_good is False 