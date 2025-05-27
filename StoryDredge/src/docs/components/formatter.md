# HSA Formatter Component

The HSA Formatter is responsible for transforming classified articles into the standardized Human Story Atlas (HSA) format and organizing them into the appropriate directory structure.

## Features

- Article validation against HSA schema requirements
- Field mapping from classified articles to HSA format
- Timestamp standardization to ISO 8601 format
- Output organization by date in YYYY/MM/DD directory structure
- Pretty-printed JSON output (configurable)
- Batch processing of multiple articles
- Comprehensive validation and error handling

## Requirements

- Python 3.8+
- JSON schema validation
- Date parsing and formatting

## Installation

The HSA Formatter is a core component of the StoryDredge pipeline and is installed with the main project. No additional installation steps are required.

## Usage

### Basic Usage

```python
from src.formatter.hsa_formatter import HSAFormatter

# Create a formatter instance
formatter = HSAFormatter()

# Format and save a single article
article = {
    "headline": "Sample Article",
    "body": "This is the article content...",
    "section": "news",
    "tags": ["tag1", "tag2"],
    "date": "2023-08-15",  # Non-standard format, will be converted
    "publication": "The Daily Example",
    "source_issue": "daily-example-20230815",
    "source_url": "https://example.com/issues/2023-08-15"
}

# Format the article to HSA standards
formatted_article = formatter.format_article(article)

# Save the article to the appropriate location
output_path = formatter.save_article(article)
```

### Batch Processing

```python
# Process a batch of articles
articles = [
    # List of article dictionaries
]

# Process and save them all
results = formatter.process_batch(articles)

# Each returned path is the location of a saved article
for path in results:
    print(f"Saved article to: {path}")
```

### Processing a Directory

```python
# Process all JSON files in a directory
input_dir = "path/to/classified_articles"
results = formatter.process_directory(input_dir, recursive=True)
```

## Configuration

The formatter can be configured through the `config/pipeline.yml` file:

```yaml
formatter:
  enabled: true
  debug_mode: false
  timeout_seconds: 60
  validate_output: true
  organize_by_date: true
  output_format: "json"
  include_metadata: true
  pretty_print: true
```

## HSA Output Format

All processed articles conform to the Human Story Atlas (HSA) format:

```json
{
  "headline": "Story Title or Headline",
  "body": "Full text content of the story...",
  "tags": ["tag1", "tag2", "tag3"],
  "section": "news",
  "timestamp": "YYYY-MM-DDTHH:MM:SS.000Z",
  "publication": "Publication Source Name",
  "source_issue": "Original source issue identifier",
  "source_url": "URL or reference to original source",
  "byline": "Author name (if available)",
  "dateline": "Location and date information (if available)"
}
```

## Required Fields

The following fields are required in the HSA output format:

- **headline**: The headline or title of the article
- **body**: The full text content of the article
- **tags**: Array of tags related to the article content
- **section**: Category/section name (e.g., "news", "sports")
- **timestamp**: ISO 8601 formatted date/time (YYYY-MM-DDTHH:MM:SS.000Z)
- **publication**: Name of the source publication
- **source_issue**: Original issue identifier
- **source_url**: URL or reference to the original source

## Directory Structure

The formatter organizes output files in the following structure:

```
output/hsa-ready/
├── YYYY/
│   ├── MM/
│   │   ├── DD/
│   │   │   ├── article-1-12345.json
│   │   │   ├── article-2-12346.json
│   │   │   └── ...
```

This structure allows for easy organization and retrieval of articles by date.

## Testing

Run the tests for the formatter component:

```bash
python -m pytest tests/test_formatter/test_hsa_formatter.py -v
```

Try the example script:

```bash
python examples/formatter_example.py
```

## Limitations and Future Improvements

- Currently limited to JSON output format
- No compression/optimization for large volumes of articles
- Future versions may include additional validation rules
- Plan to add support for different output formats (e.g., CSV, XML) 