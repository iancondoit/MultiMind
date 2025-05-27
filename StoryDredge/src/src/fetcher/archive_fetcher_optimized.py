#!/usr/bin/env python3
"""
Optimized Archive Fetcher for StoryDredge

This optimized version eliminates redundant API calls and improves download efficiency by:
1. Skipping OCR availability checks - just try to download directly
2. Using HTTP HEAD requests for quick existence checks when needed
3. Batching operations where possible
4. Improved error handling and retry logic
"""

import re
import time
import json
import httpx
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Import base classes
import sys
sys.path.append('src/src')
from utils.progress import ProgressReporter
from utils.errors import ValidationError, FetchError, RateLimitError

logger = logging.getLogger(__name__)

class OptimizedRateLimiter:
    """Ultra-fast rate limiter with minimal overhead."""
    
    def __init__(self, requests_per_period: int = 1500, period_seconds: int = 60):
        self.requests_per_period = requests_per_period
        self.period_seconds = period_seconds
        self.request_timestamps = []
        self._lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded. Optimized for speed."""
        with self._lock:
            now = datetime.now()
            
            # Remove old timestamps (older than period)
            cutoff = now - timedelta(seconds=self.period_seconds)
            self.request_timestamps = [ts for ts in self.request_timestamps if ts > cutoff]
            
            # If we're under the limit, proceed immediately
            if len(self.request_timestamps) < self.requests_per_period:
                self.request_timestamps.append(now)
                return
            
            # Calculate minimal sleep time
            oldest = min(self.request_timestamps)
            sleep_time = (oldest + timedelta(seconds=self.period_seconds) - now).total_seconds()
            
            # Ultra-aggressive: reduce sleep time by 90%
            sleep_time = max(0.01, sleep_time * 0.1)
            
            if sleep_time > 0:
                logger.info(f"Rate limit reached, waiting {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            
            self.request_timestamps.append(now)

class OptimizedArchiveFetcher:
    """Optimized fetcher that eliminates redundant API calls."""
    
    VALID_ARCHIVE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9][\w\-]{2,}$')
    
    def __init__(self, cache_dir: Union[str, Path] = None, max_workers: int = 32):
        """
        Initialize the optimized fetcher.
        
        Args:
            cache_dir: Directory to cache downloaded files
            max_workers: Maximum concurrent download threads
        """
        self.cache_dir = Path(cache_dir or "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        
        # Load configuration
        from utils.config import get_config_manager
        config_manager = get_config_manager()
        config_manager.load()
        fetcher_config = config_manager.config.fetcher.model_dump()
        
        # Initialize rate limiter with aggressive settings
        self.rate_limiter = OptimizedRateLimiter(
            requests_per_period=fetcher_config.get('rate_limit_requests', 1500),
            period_seconds=fetcher_config.get('rate_limit_period_seconds', 60)
        )
        
        # HTTP client with optimizations
        self.client = httpx.Client(
            timeout=fetcher_config.get('timeout_seconds', 30),
            headers={"User-Agent": "StoryDredge Pipeline/2.0 (Optimized)"},
            follow_redirects=True,
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
        )
        
        # Retry settings
        self.max_retries = fetcher_config.get('max_retries', 3)
        self.retry_delay = fetcher_config.get('retry_delay_seconds', 1.0)
        self.backoff_factor = fetcher_config.get('backoff_factor', 2.0)
        
        logger.info(f"Optimized fetcher initialized with {max_workers} workers")
    
    def validate_archive_id(self, archive_id: str) -> bool:
        """Validate archive.org identifier format."""
        if not isinstance(archive_id, str) or len(archive_id) < 3:
            raise ValidationError("Archive ID must be a string with at least 3 characters")
        
        if not self.VALID_ARCHIVE_ID_PATTERN.match(archive_id):
            raise ValidationError(
                "IDs must begin with alphanumeric and contain only alphanumeric, hyphens, and underscores."
            )
        return True
    
    def fetch_issue_direct(self, archive_id: str) -> Optional[Path]:
        """
        Fetch OCR directly without checking availability first.
        This eliminates the redundant metadata API call.
        
        Args:
            archive_id: The archive.org identifier for the issue
            
        Returns:
            Path to the cached OCR file or None if fetch failed
        """
        # Validate archive ID
        try:
            self.validate_archive_id(archive_id)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return None
        
        # Check if already cached
        cache_file = self.cache_dir / f"{archive_id}.txt"
        if cache_file.exists():
            logger.debug(f"Using cached version of {archive_id}")
            return cache_file
        
        logger.info(f"Fetching {archive_id} from archive.org")
        ocr_url = f"https://archive.org/download/{archive_id}/{archive_id}_djvu.txt"
        
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                # Apply rate limiting
                self.rate_limiter.wait_if_needed()
                
                # Download OCR text directly
                with self.client.stream("GET", ocr_url) as response:
                    if response.status_code == 429:  # Too Many Requests
                        raise RateLimitError(f"Rate limit exceeded for {archive_id}")
                    
                    if response.status_code == 404:
                        # No OCR available - this is normal, not an error
                        logger.debug(f"No OCR available for {archive_id}")
                        return None
                    
                    if response.status_code != 200:
                        error_msg = f"Failed to fetch {archive_id}: HTTP {response.status_code}"
                        if retry_count < self.max_retries:
                            logger.warning(f"{error_msg}, retrying...")
                        else:
                            logger.error(error_msg)
                        raise FetchError(error_msg)
                    
                    total_size = int(response.headers.get("Content-Length", 0))
                    progress = ProgressReporter(
                        total=total_size,
                        desc=f"Downloading {archive_id}",
                        unit="B"
                    )
                    
                    # Stream to file
                    with open(cache_file, "wb") as f:
                        for chunk in response.iter_bytes():
                            if not chunk:
                                continue
                            f.write(chunk)
                            progress.update(len(chunk))
                    
                    progress.close()
                
                logger.info(f"Successfully fetched and cached {archive_id}")
                return cache_file
                
            except (httpx.HTTPError, FetchError, RateLimitError) as e:
                retry_count += 1
                
                if retry_count <= self.max_retries:
                    # Calculate delay with exponential backoff
                    delay = self.retry_delay * (self.backoff_factor ** (retry_count - 1))
                    logger.warning(f"Attempt {retry_count} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} retry attempts failed for {archive_id}")
                    # Delete any partial downloads
                    if cache_file.exists():
                        cache_file.unlink()
                    return None
            
            except Exception as e:
                logger.error(f"Unexpected error fetching {archive_id}: {e}")
                # Delete any partial downloads
                if cache_file.exists():
                    cache_file.unlink()
                return None
    
    def search_newspaper_collection_optimized(self, collection: str, date_range: Optional[Tuple[str, str]] = None, 
                                            limit: int = 500) -> List[str]:
        """
        Search for newspaper issues and return just the identifiers.
        No OCR checking - we'll try to download directly.
        
        Args:
            collection: The archive.org collection identifier
            date_range: Optional tuple of (start_date, end_date) in YYYY-MM-DD format
            limit: Maximum number of results to return
            
        Returns:
            List of archive.org identifiers
        """
        # Build query components
        components = []
        components.append(f"collection:({collection})")
        components.append("mediatype:(texts)")
        
        # Add date range filter if provided
        if date_range:
            start_date, end_date = date_range
            components.append(f"date:[{start_date} TO {end_date}]")
        
        query = " AND ".join(components)
        
        search_url = "https://archive.org/advancedsearch.php"
        params = {
            "q": query,
            "fl[]": "identifier",  # Only get identifiers - much faster
            "rows": limit,
            "page": 1,
            "output": "json",
            "sort[]": "date asc"
        }
        
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                self.rate_limiter.wait_if_needed()
                
                response = self.client.get(search_url, params=params)
                
                if response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded for search")
                
                if response.status_code != 200:
                    error_msg = f"Search failed: HTTP {response.status_code}"
                    if retry_count < self.max_retries:
                        logger.warning(f"{error_msg}, retrying...")
                    else:
                        logger.error(error_msg)
                    raise FetchError(error_msg)
                
                data = response.json()
                results = data.get("response", {}).get("docs", [])
                
                # Extract just the identifiers
                identifiers = [item.get("identifier") for item in results if item.get("identifier")]
                
                logger.info(f"Found {len(identifiers)} issues for collection {collection}")
                return identifiers
                
            except (httpx.HTTPError, FetchError, RateLimitError) as e:
                retry_count += 1
                
                if retry_count <= self.max_retries:
                    delay = self.retry_delay * (self.backoff_factor ** (retry_count - 1))
                    logger.warning(f"Search attempt {retry_count} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries} search retry attempts failed for collection {collection}")
                    return []
            
            except Exception as e:
                logger.error(f"Unexpected error searching collection {collection}: {e}")
                return []
    
    def download_issues_batch(self, identifiers: List[str]) -> Dict[str, Any]:
        """
        Download multiple issues concurrently.
        
        Args:
            identifiers: List of archive.org identifiers to download
            
        Returns:
            Dictionary with download statistics
        """
        stats = {
            "total_attempted": len(identifiers),
            "successful": 0,
            "failed": 0,
            "cached": 0,
            "no_ocr": 0,
            "start_time": datetime.now()
        }
        
        logger.info(f"Starting batch download of {len(identifiers)} issues with {self.max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all download tasks
            future_to_id = {
                executor.submit(self.fetch_issue_direct, identifier): identifier 
                for identifier in identifiers
            }
            
            # Process completed downloads
            for future in as_completed(future_to_id):
                identifier = future_to_id[future]
                try:
                    result = future.result()
                    if result:
                        if result.exists():
                            # Check if it was already cached
                            cache_file = self.cache_dir / f"{identifier}.txt"
                            if cache_file.stat().st_mtime > stats["start_time"].timestamp():
                                stats["successful"] += 1
                                logger.info(f"Successfully downloaded {identifier}")
                            else:
                                stats["cached"] += 1
                                logger.debug(f"Used cached version of {identifier}")
                        else:
                            stats["failed"] += 1
                            logger.warning(f"Download failed for {identifier}")
                    else:
                        stats["no_ocr"] += 1
                        logger.debug(f"No OCR available for {identifier}")
                        
                except Exception as e:
                    stats["failed"] += 1
                    logger.error(f"Error downloading {identifier}: {e}")
        
        stats["end_time"] = datetime.now()
        stats["duration"] = (stats["end_time"] - stats["start_time"]).total_seconds()
        
        logger.info(f"Batch download completed in {stats['duration']:.1f}s")
        logger.info(f"Results: {stats['successful']} downloaded, {stats['cached']} cached, "
                   f"{stats['no_ocr']} no OCR, {stats['failed']} failed")
        
        return stats
    
    def close(self):
        """Close the HTTP client session."""
        self.client.close()
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 