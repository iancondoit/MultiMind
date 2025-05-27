# Article Splitter Component

The Article Splitter component is responsible for identifying and extracting individual articles from cleaned OCR text. It analyzes text patterns to detect headlines, identifies article boundaries, and extracts metadata like bylines and datelines.

## Overview

The Article Splitter is the third component in the StoryDredge pipeline. It:

1. Identifies headlines through pattern recognition
2. Determines article boundaries based on headline positions
3. Extracts article metadata (bylines, datelines)
4. Filters out advertisements and irrelevant content
5. Verifies OCR quality for reliable processing

## Key Features

### Headline Detection
- Identifies headlines using pattern recognition
- Detects ALL CAPS headlines, centered text, and section separators
- Adjustable aggressiveness for different OCR quality levels

### Article Boundary Identification
- Determines article boundaries based on headline positions
- Handles cases with missing or ambiguous boundaries
- Includes fallback detection for texts with no clear headlines

### Metadata Extraction
- Extracts bylines (author attribution)
- Extracts datelines (location and date information)
- Associates metadata with corresponding articles

### Advertisement Detection
- Identifies and optionally filters advertisement content
- Uses pattern recognition to detect classified ads
- Configurable thresholds for advertisement identification

### OCR Quality Verification
- Assesses text quality to ensure reliable processing
- Falls back to more aggressive modes for lower quality text
- Reports quality metrics for monitoring

## Usage

### Basic Usage

```python
from src.splitter.article_splitter import ArticleSplitter

# Create a splitter instance
splitter = ArticleSplitter()

# Process OCR-cleaned text
with open("cleaned_ocr.txt", "r") as f:
    text = f.read()

# Detect headlines
headlines = splitter.detect_headlines(text)

# Extract articles
articles = splitter.extract_articles(text, headlines)

# Print article titles
for article in articles:
    print(f"Article: {article['title']}")
```

### Processing a File

```python
from pathlib import Path
from src.splitter.article_splitter import ArticleSplitter

# Create a splitter instance
splitter = ArticleSplitter()

# Process a file
input_file = Path("data/cleaned/newspaper_1906_04_19_cleaned.txt")
output_dir = Path("data/articles/newspaper_1906_04_19")

# Add metadata to include with each article
metadata = {
    "date": "1906-04-19",
    "publication": "San Francisco Chronicle",
    "archive_id": "sfchronicle_19060419"
}

# Split the file into articles
article_files = splitter.split_file(input_file, output_dir, metadata)

# Print the paths to the created article files
for file_path in article_files:
    print(f"Created article file: {file_path}")
```

### Using Aggressive Mode

```python
from src.splitter.article_splitter import ArticleSplitter

# Create a splitter with aggressive mode for lower quality OCR
splitter = ArticleSplitter(aggressive_mode=True)

# Process OCR text with aggressive headline detection
headlines = splitter.detect_headlines(text)
```

## Configuration

The Article Splitter component can be configured through the StoryDredge configuration system. The relevant settings are in the `splitter` section of the pipeline configuration file:

```yaml
splitter:
  enabled: true
  debug_mode: false
  timeout_seconds: 600
  headline_detection_threshold: 0.7
  min_article_length: 100
  max_article_length: 10000
  enable_fuzzy_boundaries: true
  remove_advertisements: true
  quality_threshold: 0.5
```

## Implementation Details

### Core Classes

- **ArticleSplitter**: Main class for identifying and extracting articles from OCR text

### Key Methods

- **detect_headlines(text)**: Identifies potential headlines in the text
- **extract_articles(text, headlines)**: Extracts articles based on detected headlines
- **verify_ocr_quality(text)**: Checks if the OCR quality is sufficient for reliable processing
- **split_file(input_file, output_dir, metadata)**: Processes a file and saves articles

### Dependencies

- **re**: Regular expression library for pattern matching
- **json**: For serializing articles to JSON files
- **logging**: For logging operations and errors
- **pathlib**: For path management

## Error Handling

The component implements robust error handling:

- Graceful handling of missing input files
- Fallback strategies for low-quality OCR text
- Special handling for texts with no detectable headlines
- Proper validation to prevent empty or invalid articles

## Future Enhancements

Potential improvements for the Article Splitter component:

1. Machine learning-based headline detection for better accuracy
2. Improved boundary detection using semantic analysis
3. More sophisticated advertisement detection
4. Support for different newspaper layouts and formats
5. Integration with the classifier for better article categorization 