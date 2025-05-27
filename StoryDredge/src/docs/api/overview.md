# StoryDredge API Reference

This section provides detailed API documentation for all StoryDredge components. It covers the public interfaces, classes, methods, and functions that developers can use to integrate with or extend the StoryDredge pipeline.

## Component APIs

The StoryDredge API is organized by components, with each component providing a well-defined interface for interaction:

- **Fetcher API**: Download and cache newspaper OCR text from archive.org
- **Cleaner API**: Normalize and correct OCR text
- **Splitter API**: Identify and extract individual articles
- **Classifier API**: Use local LLM to classify articles and extract metadata
- **Formatter API**: Convert classified articles to HSA-ready JSON format
- **Pipeline API**: Orchestrate the processing of newspaper issues

## Common Patterns

Each component API follows a similar pattern:

1. A main class that implements the core functionality
2. Configuration options that can be passed during initialization
3. Methods for processing input and generating output
4. Error handling through specific exceptions

## Example Usage

Here's a basic example of using the component APIs directly:

```python
from src.fetcher import ArchiveFetcher
from src.cleaner import OCRCleaner
from src.splitter import ArticleSplitter
from src.classifier import ArticleClassifier
from src.formatter import HSAFormatter

# Initialize components
fetcher = ArchiveFetcher(cache_dir="cache")
cleaner = OCRCleaner()
splitter = ArticleSplitter()
classifier = ArticleClassifier(model_name="llama2")
formatter = HSAFormatter(output_dir="output/hsa-ready")

# Process a newspaper issue
issue_id = "sn84026749-19220101"
ocr_text = fetcher.fetch_issue(issue_id)
cleaned_text = cleaner.clean(ocr_text)
articles = splitter.split(cleaned_text)
classified_articles = classifier.classify_batch(articles)
formatted_articles = formatter.format_batch(classified_articles)
```

## Error Handling

All components raise specific exception types that inherit from the base `StoryDredgeError` class. This allows for precise error handling in your applications.

## Detailed API Documentation

For detailed documentation of each component API, see the following sections:

- [Fetcher API](fetcher.md)
- [Cleaner API](cleaner.md)
- [Splitter API](splitter.md)
- [Classifier API](classifier.md)
- [Formatter API](formatter.md)
- [Pipeline API](pipeline.md)
- [Benchmarking API](benchmarking.md)
- [Utilities API](utils.md) 