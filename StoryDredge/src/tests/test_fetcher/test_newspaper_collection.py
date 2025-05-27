"""
Tests for ArchiveFetcher with specific newspaper collections.

These tests verify the enhanced functionality for searching and fetching issues 
from specific newspaper collections like the Atlanta Constitution.
"""

import os
import pytest
import httpx
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

from src.fetcher.archive_fetcher import ArchiveFetcher


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, status_code=200, content=None, headers=None):
        self.status_code = status_code
        self._content = content if content is not None else b""
        self.headers = headers or {}
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def iter_bytes(self):
        yield self._content
    
    def json(self):
        if isinstance(self._content, dict):
            return self._content
        if isinstance(self._content, bytes):
            import json
            return json.loads(self._content)
        return {}


class TestNewspaperCollection:
    """Test cases for newspaper collection functionality in ArchiveFetcher."""
    
    def test_search_newspaper_collection(self, temp_dir):
        """Test searching for issues in a specific newspaper collection."""
        # Mock data for Atlanta Constitution collection search
        mock_atlanta_response = {
            "response": {
                "numFound": 3,
                "start": 0,
                "docs": [
                    {
                        "identifier": "pub_atlanta-constitution_19220101",
                        "title": "Atlanta Constitution (January 1, 1922)",
                        "date": "1922-01-01T00:00:00Z",
                        "mediatype": "texts",
                        "collection": ["pub_atlanta-constitution"]
                    },
                    {
                        "identifier": "pub_atlanta-constitution_19220102",
                        "title": "Atlanta Constitution (January 2, 1922)",
                        "date": "1922-01-02T00:00:00Z",
                        "mediatype": "texts",
                        "collection": ["pub_atlanta-constitution"]
                    },
                    {
                        "identifier": "pub_atlanta-constitution_19220103",
                        "title": "Atlanta Constitution (January 3, 1922)",
                        "date": "1922-01-03T00:00:00Z",
                        "mediatype": "texts",
                        "collection": ["pub_atlanta-constitution"]
                    }
                ]
            }
        }
        
        # Test the search_newspaper_collection method
        with patch('httpx.Client.get') as mock_get:
            mock_get.return_value = MockResponse(status_code=200, content=mock_atlanta_response)
            
            fetcher = ArchiveFetcher()
            results = fetcher.search_newspaper_collection(
                collection="pub_atlanta-constitution",
                date_range=("1922-01-01", "1922-01-03"),
                limit=10
            )
            
            # Verify the correct API endpoint was called
            mock_get.assert_called_once()
            call_args = mock_get.call_args[1]
            assert "params" in call_args
            assert "q" in call_args["params"]
            query_str = call_args["params"]["q"]
            
            # Check that collection and date filters are in the query
            assert "collection:(pub_atlanta-constitution)" in query_str
            assert "date:[1922-01-01 TO 1922-01-03]" in query_str
            
            # Verify the results
            assert len(results) == 3
            assert results[0]["identifier"] == "pub_atlanta-constitution_19220101"
            assert results[1]["identifier"] == "pub_atlanta-constitution_19220102"
            assert results[2]["identifier"] == "pub_atlanta-constitution_19220103"
    
    def test_check_ocr_availability(self, temp_dir):
        """Test checking if OCR is available for a newspaper issue."""
        # Mock data for file metadata response
        mock_file_metadata = {
            "result": [
                {"name": "pub_atlanta-constitution_19220101_djvu.txt", "size": "500000"},
                {"name": "pub_atlanta-constitution_19220101.pdf", "size": "10000000"},
                {"name": "pub_atlanta-constitution_19220101_djvu.xml", "size": "600000"}
            ]
        }
        
        # Test the check_ocr_availability method
        with patch('httpx.Client.get') as mock_get:
            mock_get.return_value = MockResponse(status_code=200, content=mock_file_metadata)
            
            fetcher = ArchiveFetcher()
            has_ocr = fetcher.check_ocr_availability("pub_atlanta-constitution_19220101")
            
            # Verify the correct API endpoint was called
            mock_get.assert_called_once()
            assert "metadata" in mock_get.call_args[0][0]
            assert "pub_atlanta-constitution_19220101" in mock_get.call_args[0][0]
            
            # Verify the result
            assert has_ocr is True
    
    def test_check_ocr_availability_not_found(self, temp_dir):
        """Test checking OCR availability when no OCR file exists."""
        # Mock data without OCR file
        mock_file_metadata = {
            "result": [
                {"name": "pub_atlanta-constitution_19220101.pdf", "size": "10000000"},
                {"name": "pub_atlanta-constitution_19220101_djvu.xml", "size": "600000"}
            ]
        }
        
        # Test the check_ocr_availability method
        with patch('httpx.Client.get') as mock_get:
            mock_get.return_value = MockResponse(status_code=200, content=mock_file_metadata)
            
            fetcher = ArchiveFetcher()
            has_ocr = fetcher.check_ocr_availability("pub_atlanta-constitution_19220101")
            
            # Verify the result
            assert has_ocr is False
    
    def test_get_newspaper_issues(self, temp_dir):
        """Test getting a list of issues with OCR from a newspaper collection."""
        # Mock search response
        mock_search_response = {
            "response": {
                "numFound": 3,
                "start": 0,
                "docs": [
                    {
                        "identifier": "pub_atlanta-constitution_19220101",
                        "title": "Atlanta Constitution (January 1, 1922)",
                        "date": "1922-01-01T00:00:00Z"
                    },
                    {
                        "identifier": "pub_atlanta-constitution_19220102",
                        "title": "Atlanta Constitution (January 2, 1922)",
                        "date": "1922-01-02T00:00:00Z"
                    },
                    {
                        "identifier": "pub_atlanta-constitution_19220103",
                        "title": "Atlanta Constitution (January 3, 1922)",
                        "date": "1922-01-03T00:00:00Z"
                    }
                ]
            }
        }
        
        # Mock OCR availability responses
        ocr_availability = {
            "pub_atlanta-constitution_19220101": True,
            "pub_atlanta-constitution_19220102": False,
            "pub_atlanta-constitution_19220103": True
        }
        
        def mock_ocr_check(identifier):
            return {
                "result": [
                    {"name": f"{identifier}_djvu.txt"} if ocr_availability[identifier] else {"name": f"{identifier}.pdf"}
                ]
            }
        
        with patch('src.fetcher.archive_fetcher.ArchiveFetcher.search_newspaper_collection') as mock_search:
            mock_search.return_value = mock_search_response["response"]["docs"]
            
            with patch('httpx.Client.get') as mock_get:
                mock_get.side_effect = lambda url, **kwargs: MockResponse(
                    status_code=200,
                    content=mock_ocr_check(url.split('/')[-2])
                )
                
                fetcher = ArchiveFetcher()
                issues = fetcher.get_newspaper_issues(
                    collection="pub_atlanta-constitution",
                    date_range=("1922-01-01", "1922-01-03"),
                    limit=10
                )
                
                # Verify the correct methods were called
                mock_search.assert_called_once()
                assert mock_get.call_count == 3  # Check OCR for all 3 issues
                
                # Verify the results - should filter out the issue without OCR
                assert len(issues) == 2
                assert issues[0]["identifier"] == "pub_atlanta-constitution_19220101"
                assert issues[1]["identifier"] == "pub_atlanta-constitution_19220103"
                assert issues[0]["has_ocr"] is True
                assert issues[1]["has_ocr"] is True
    
    def test_save_issues_file(self, temp_dir):
        """Test saving issues to a JSON file for batch processing."""
        issues = [
            {
                "identifier": "pub_atlanta-constitution_19220101",
                "title": "Atlanta Constitution (January 1, 1922)",
                "date": "1922-01-01T00:00:00Z",
                "has_ocr": True
            },
            {
                "identifier": "pub_atlanta-constitution_19220103",
                "title": "Atlanta Constitution (January 3, 1922)",
                "date": "1922-01-03T00:00:00Z",
                "has_ocr": True
            }
        ]
        
        output_file = Path(temp_dir) / "atlanta_issues.json"
        
        fetcher = ArchiveFetcher()
        fetcher.save_issues_file(issues, output_file)
        
        # Verify the file was created
        assert output_file.exists()
        
        # Verify the content
        with open(output_file, 'r') as f:
            saved_data = json.load(f)
            
        assert "issues" in saved_data
        assert len(saved_data["issues"]) == 2
        assert saved_data["issues"][0] == "pub_atlanta-constitution_19220101"
        assert saved_data["issues"][1] == "pub_atlanta-constitution_19220103" 