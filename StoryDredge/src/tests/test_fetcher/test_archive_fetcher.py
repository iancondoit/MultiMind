"""
Tests for the ArchiveFetcher class.
"""

import os
import pytest
import httpx
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import the component to test
from src.fetcher.archive_fetcher import ArchiveFetcher


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, status_code=200, content=b"", headers=None):
        self.status_code = status_code
        self._content = content
        self.headers = headers or {}
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def iter_bytes(self):
        yield self._content
    
    def json(self):
        import json
        return json.loads(self._content)


class TestArchiveFetcher:
    """Test cases for ArchiveFetcher."""
    
    def test_init(self, temp_dir):
        """Test initialization of ArchiveFetcher."""
        # Test with default cache directory
        fetcher = ArchiveFetcher()
        assert isinstance(fetcher.cache_dir, Path)
        assert fetcher.cache_dir.name == "cache"
        
        # Test with custom cache directory
        custom_cache = temp_dir / "custom_cache"
        fetcher = ArchiveFetcher(cache_dir=custom_cache)
        assert fetcher.cache_dir == custom_cache
        assert custom_cache.exists()
    
    def test_fetch_issue_cached(self, temp_dir):
        """Test fetching an already cached issue."""
        # Setup
        cache_dir = temp_dir / "cache"
        cache_dir.mkdir()
        archive_id = "san-antonio-express-news-1977-06-14"
        cache_file = cache_dir / f"{archive_id}.txt"
        
        # Create a mock cached file
        with open(cache_file, 'w') as f:
            f.write("Cached OCR text")
        
        # Test
        fetcher = ArchiveFetcher(cache_dir=cache_dir)
        result = fetcher.fetch_issue(archive_id)
        
        # Assert
        assert result == cache_file
        assert result.exists()
        with open(result, 'r') as f:
            assert f.read() == "Cached OCR text"
    
    @patch('httpx.Client.stream')
    def test_fetch_issue_success(self, mock_stream, temp_dir):
        """Test successfully fetching an issue from archive.org."""
        # Setup
        cache_dir = temp_dir / "cache"
        cache_dir.mkdir()
        archive_id = "san-antonio-express-news-1977-06-14"
        
        # Mock the HTTP response
        mock_response = MockResponse(
            status_code=200,
            content=b"OCR Text from archive.org",
            headers={"Content-Length": "26"}
        )
        mock_stream.return_value = mock_response
        
        # Test
        fetcher = ArchiveFetcher(cache_dir=cache_dir)
        result = fetcher.fetch_issue(archive_id)
        
        # Assert
        assert result is not None
        assert result.exists()
        with open(result, 'r') as f:
            assert f.read() == "OCR Text from archive.org"
        
        # Verify the correct URL was called
        expected_url = f"https://archive.org/download/{archive_id}/{archive_id}_djvu.txt"
        mock_stream.assert_called_once_with("GET", expected_url)
    
    @patch('httpx.Client.stream')
    def test_fetch_issue_http_error(self, mock_stream, temp_dir):
        """Test handling HTTP errors when fetching an issue."""
        # Setup
        cache_dir = temp_dir / "cache"
        cache_dir.mkdir()
        archive_id = "nonexistent-issue"
        
        # Mock a 404 response
        mock_response = MockResponse(status_code=404)
        mock_stream.return_value = mock_response
        
        # Test
        fetcher = ArchiveFetcher(cache_dir=cache_dir)
        result = fetcher.fetch_issue(archive_id)
        
        # Assert
        assert result is None
    
    @patch('httpx.Client.get')
    def test_search_archive_success(self, mock_get, mock_archive_response):
        """Test successfully searching archive.org."""
        # Setup
        mock_get.return_value = MockResponse(
            status_code=200,
            content=bytes(str(mock_archive_response).encode('utf-8'))
        )
        
        # Test
        fetcher = ArchiveFetcher()
        results = fetcher.search_archive("san antonio express news 1977")
        
        # Assert
        assert len(results) == 3
        assert results[0]["identifier"] == "san-antonio-express-news-1977-06-14"
        
        # Verify search parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args[1]
        assert "q" in call_args["params"]
        assert call_args["params"]["q"] == "san antonio express news 1977"
    
    @patch('httpx.Client.get')
    def test_search_archive_error(self, mock_get):
        """Test handling errors when searching archive.org."""
        # Setup
        mock_get.return_value = MockResponse(status_code=500)
        
        # Test
        fetcher = ArchiveFetcher()
        results = fetcher.search_archive("invalid query")
        
        # Assert
        assert results == []
    
    def test_context_manager(self):
        """Test using ArchiveFetcher as a context manager."""
        with patch('httpx.Client.close') as mock_close:
            with ArchiveFetcher() as fetcher:
                assert isinstance(fetcher, ArchiveFetcher)
            
            # Assert close was called when exiting context
            mock_close.assert_called_once() 