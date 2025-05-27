# Fetcher Component

The Fetcher component is responsible for retrieving and caching newspaper OCR text from archive.org. It provides an efficient and robust way to download newspaper issues while handling common network-related challenges.

## Overview

The Fetcher is the first component in the StoryDredge pipeline. It:

1. Downloads OCR text files from archive.org
2. Implements a caching mechanism to avoid redundant downloads
3. Manages rate limiting to avoid overwhelming archive.org servers
4. Provides robust error handling and retry logic
5. Validates input to prevent malformed requests

## Key Features

### Archive.org Integration
- Connects to archive.org's public APIs
- Downloads OCR text in the DJVU text format
- Implements search capability to find newspaper issues

### Caching System
- Stores downloaded content locally to prevent redundant downloads
- Validates cache integrity
- Provides cache management (e.g., clearing old cache entries)
- Uses configurable cache location

### Rate Limiting
- Prevents overwhelming archive.org with too many requests
- Configurable request rate (requests per time period)
- Self-regulating to ensure compliance with service limits

### Robust Error Handling
- Comprehensive retry logic with exponential backoff
- Graceful handling of network errors, timeouts, and service disruptions
- Custom exceptions for different error scenarios

### Input Validation
- Validates archive IDs before making requests
- Prevents malformed requests that would fail
- Provides clear error messages for invalid inputs

### Progress Reporting
- Real-time download progress reporting
- Integration with the StoryDredge progress tracking system
- Download speed and ETA estimation

## Usage

### Basic Usage

```python
from src.fetcher.archive_fetcher import ArchiveFetcher

# Create a fetcher instance
fetcher = ArchiveFetcher()

# Download a newspaper issue by its archive.org ID
result = fetcher.fetch_issue("san-francisco-chronicle-1906-04-19")

if result:
    # result is a Path to the cached file
    print(f"Successfully downloaded to {result}")
else:
    print("Download failed")
```

### Using Context Manager

```python
with ArchiveFetcher() as fetcher:
    # The client will be automatically closed when exiting the context
    results = fetcher.search_archive("san francisco earthquake 1906")
    for item in results:
        print(f"Found: {item['title']} - {item['date']}")
```

### Searching Archive.org

```python
with ArchiveFetcher() as fetcher:
    # Search for newspaper issues
    results = fetcher.search_archive("chicago tribune 1929 stock market crash")
    
    # Process search results
    for item in results:
        archive_id = item["identifier"]
        title = item["title"]
        date = item["date"]
        print(f"{title} ({date}): {archive_id}")
        
        # Download each found issue
        issue_path = fetcher.fetch_issue(archive_id)
```

### Cache Management

```python
fetcher = ArchiveFetcher()

# Clear the entire cache
fetcher.clear_cache()

# Or clear only files older than a certain number of days
fetcher.clear_cache(older_than_days=30)
```

## Configuration

The Fetcher component can be configured through the StoryDredge configuration system. The relevant settings are in the `fetcher` section of the pipeline configuration file:

```yaml
fetcher:
  enabled: true
  debug_mode: false
  timeout_seconds: 120
  rate_limit_requests: 10
  rate_limit_period_seconds: 60
  max_retries: 3
  retry_delay_seconds: 2
  backoff_factor: 2.0
  user_agent: "StoryDredge Pipeline/1.0"
  cache_dir: "cache"
```

## Implementation Details

### Core Classes

- **ArchiveFetcher**: Main class for fetching newspaper OCR text from archive.org
- **RateLimiter**: Helper class for managing request rates

### Key Methods

- **fetch_issue(archive_id)**: Downloads and caches a newspaper issue
- **search_archive(query, num_results, mediatype)**: Searches archive.org for newspaper issues
- **clear_cache(older_than_days)**: Clears the cache directory
- **validate_archive_id(archive_id)**: Validates an archive.org identifier

## Dependencies

- **httpx**: HTTP client library for making requests
- **pydantic**: Used for configuration management
- **pathlib**: For managing file paths and cache directory

## Error Handling

The component uses several custom exception types:

- **ValidationError**: Raised when an input validation fails
- **FetchError**: Raised when there's a problem fetching resources
- **RateLimitError**: Raised when rate limits are exceeded

Each error is properly logged and can be caught to implement custom recovery strategies.

## Future Enhancements

Potential improvements for the Fetcher component:

1. Parallel downloads for multiple issues
2. Alternative OCR text formats support
3. Enhanced metadata retrieval
4. Proxy support for distributed fetching
5. Integration with other archive sources 