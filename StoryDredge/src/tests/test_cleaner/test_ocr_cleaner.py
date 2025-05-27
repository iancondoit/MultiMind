"""
Tests for the OCRCleaner class.
"""

import os
import pytest
from pathlib import Path

# Import the component to test
from src.cleaner.ocr_cleaner import OCRCleaner


class TestOCRCleaner:
    """Test cases for OCRCleaner."""
    
    def test_init(self):
        """Test initialization of OCRCleaner."""
        cleaner = OCRCleaner()
        assert cleaner.common_ocr_errors is not None
        assert cleaner.noise_patterns is not None
    
    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        cleaner = OCRCleaner()
        
        # Test multiple spaces
        text = "This   has    multiple    spaces"
        result = cleaner._normalize_whitespace(text)
        assert result == "This has multiple spaces"
        
        # Test line whitespace
        text = "  Line with leading/trailing spaces  \n  Another line  "
        result = cleaner._normalize_whitespace(text)
        assert result == "Line with leading/trailing spaces\nAnother line"
    
    def test_remove_copyright_pages(self):
        """Test removal of copyright pages."""
        cleaner = OCRCleaner()
        
        # Test copyright page
        text = "Page 1 content\n\n\n\nCopyright 1977 San Antonio Express-News\nAll Rights Reserved\n\n\n\nPage 2 content"
        result = cleaner._remove_copyright_pages(text)
        assert "Page 1 content" in result
        assert "Page 2 content" in result
        assert "Copyright 1977" not in result
        
        # Test index page
        text = "Page 1\n\n\n\nINDEX\nNews....1\nSports....2\n\n\n\nPage 2"
        result = cleaner._remove_copyright_pages(text)
        assert "Page 1" in result
        assert "Page 2" in result
        assert "INDEX" not in result
        
        # Test advertisement page
        text = "Page 1\n\n\n\nADVERTISEMENTS\n\n\n\nPage 2"
        result = cleaner._remove_copyright_pages(text)
        assert "Page 1" in result
        assert "Page 2" in result
        assert "ADVERTISEMENTS" not in result
    
    def test_clean_text(self):
        """Test the main clean_text method."""
        cleaner = OCRCleaner()
        
        # Test empty input
        assert cleaner.clean_text("") == ""
        
        # Test normalization of line endings
        text = "Line 1\r\nLine 2\rLine 3\n"
        result = cleaner.clean_text(text)
        assert result == "Line 1\nLine 2\nLine 3"
        
        # Test removal of noise patterns
        text = "Content\n---\nMore content\n===="
        result = cleaner.clean_text(text)
        assert result == "Content\n\nMore content"
        
        # Test fixing common OCR errors
        text = "Uie quick brown fox jumps over Uiat lazy dog wiUi ease"
        result = cleaner.clean_text(text)
        assert "the quick" in result.lower()
        assert "over that lazy" in result.lower()
        assert "with ease" in result.lower()
        
        # Test paragraph normalization
        text = "Paragraph 1\n\n\n\n\nParagraph 2"
        result = cleaner.clean_text(text)
        assert result == "Paragraph 1\n\nParagraph 2"
    
    def test_process_file(self, test_data_dir, temp_dir):
        """Test processing a file."""
        # Setup
        input_file = test_data_dir / "sample_ocr.txt"
        output_file = temp_dir / "cleaned_ocr.txt"
        
        cleaner = OCRCleaner()
        
        # Test with explicit output file
        result = cleaner.process_file(input_file, output_file)
        assert result is not None
        assert result.exists()
        assert result == output_file
        
        # Verify content was cleaned
        with open(result, 'r') as f:
            content = f.read()
            assert "SAN ANTONIO EXPRESS" in content
            assert "LOCAL COUNCIL APPROVES NEW BUDGET" in content
            assert "====" not in content  # Separator lines should be removed
        
        # Test with default output file
        result = cleaner.process_file(input_file)
        assert result is not None
        assert result.exists()
        assert result.name == "sample_ocr-clean.txt"
        
        # Test with nonexistent input file
        result = cleaner.process_file(test_data_dir / "nonexistent.txt")
        assert result is None 