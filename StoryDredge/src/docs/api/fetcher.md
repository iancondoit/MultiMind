# Fetcher API

The Fetcher API provides functionality for downloading and caching newspaper OCR text from archive.org.

## ArchiveFetcher

The main class for downloading and caching newspaper OCR from the Internet Archive.

### Initialization

```python
from src.fetcher import ArchiveFetcher

fetcher = ArchiveFetcher(
    cache_dir="cache",
    use_cache=True,
    retry_count=3,
    retry_delay=5,
    timeout=60
)
```

#### Parameters

- `cache_dir` (str, optional): Directory for caching downloaded OCR. Default: "cache"
- `use_cache` (bool, optional): Whether to use cached data when available. Default: True
- `retry_count` (int, optional): Number of retries for failed downloads. Default: 3
- `retry_delay` (int, optional): Seconds to wait between retries. Default: 5
- `timeout` (int, optional): Connection timeout in seconds. Default: 60

### Methods

#### fetch_issue

Downloads OCR text for a specific newspaper issue.

```python
ocr_text = fetcher.fetch_issue(issue_id)
```

**Parameters:**
- `issue_id` (str): The archive.org identifier for the newspaper issue

**Returns:**
- `str`: The OCR text content

**Raises:**
- `FetcherError`: If the issue cannot be retrieved
- `InvalidIssueIDError`: If the issue ID format is invalid
- `ArchiveAPIError`: If there's an error communicating with the archive.org API

#### fetch_batch

Downloads multiple newspaper issues.

```python
results = fetcher.fetch_batch(issue_ids, progress_callback=None)
```

**Parameters:**
- `issue_ids` (list of str): List of archive.org identifiers
- `progress_callback` (callable, optional): Function to call with progress updates

**Returns:**
- `dict`: Dictionary mapping issue IDs to their OCR text or None if failed

**Raises:**
- `FetcherError`: If there are issues with the batch operation

#### is_cached

Checks if an issue is already in the cache.

```python
is_available = fetcher.is_cached(issue_id)
```

**Parameters:**
- `issue_id` (str): The archive.org identifier for the newspaper issue

**Returns:**
- `bool`: True if the issue is in the cache, False otherwise

#### clear_cache

Clears the cache directory.

```python
fetcher.clear_cache()
```

**Parameters:**
- `older_than` (int, optional): Clear only files older than this many days

**Returns:**
- `int`: Number of files removed

## Exceptions

### FetcherError

Base exception for all fetcher-related errors.

### InvalidIssueIDError

Raised when an invalid issue ID format is provided.

### ArchiveAPIError

Raised when there's an error communicating with the archive.org API.

### CacheError

Raised when there's an error with the cache operations.

## Examples

### Basic Usage

```python
from src.fetcher import ArchiveFetcher

# Initialize the fetcher
fetcher = ArchiveFetcher(cache_dir="cache")

# Fetch a single issue
issue_id = "sn84026749-19220101"
try:
    ocr_text = fetcher.fetch_issue(issue_id)
    print(f"Downloaded {len(ocr_text)} characters of OCR text")
except Exception as e:
    print(f"Error fetching issue: {e}")
```

### Batch Processing with Progress Tracking

```python
from src.fetcher import ArchiveFetcher
from src.utils.progress import ProgressTracker

# Initialize the fetcher
fetcher = ArchiveFetcher(cache_dir="cache")

# Define a list of issues to fetch
issue_ids = [
    "sn84026749-19220101",
    "sn84026749-19220102",
    "sn84026749-19220103",
]

# Create a progress tracker
progress = ProgressTracker(total=len(issue_ids), description="Fetching issues")

# Define a progress callback
def update_progress(current, total, issue_id):
    progress.update(1, f"Fetched {issue_id}")

# Fetch multiple issues with progress tracking
results = fetcher.fetch_batch(issue_ids, progress_callback=update_progress)

# Report results
successful = sum(1 for v in results.values() if v is not None)
print(f"Successfully fetched {successful} of {len(issue_ids)} issues")
``` 