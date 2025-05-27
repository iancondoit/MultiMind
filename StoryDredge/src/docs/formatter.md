# HSA Formatter

The HSA Formatter is responsible for converting classified articles into Human Story Atlas (HSA) ready format. It provides the final step in the StoryDredge pipeline before data is imported into the HSA system.

## Overview

The formatter performs the following key tasks:

1. **Standardizing Format**: Converts various input formats to the standard HSA JSON structure
2. **Extracting Dates from Archive IDs**: Automatically determines historical dates from archive.org identifiers
3. **Organizing by Date**: Creates a date-based directory structure (YYYY/MM/DD)
4. **Field Mapping**: Converts fields like `title` to `headline` and `raw_text` to `body`
5. **Tag Extraction**: Extracts tags from classified articles' metadata (topic, people, organizations, locations)
6. **Section Mapping**: Maps category fields to valid HSA section values
7. **Validation**: Validates articles against the HSA schema requirements

## Date Extraction

A key feature of the formatter is its ability to extract dates from archive.org identifiers, which ensures that articles are properly organized even when explicit dates may be missing or incorrectly formatted in the source material.

The system supports multiple date formats in archive identifiers:
- `per_atlanta-constitution_1922-01-01_54_203` (standard format)
- `per_chicago-tribune_1934-05-22` (no suffix)
- `sim_newcastle-morning-herald_18931015` (compact date)

This extracted date is used for:
- Setting the correct timestamp on articles
- Creating the appropriate directory structure
- Ensuring source URLs and issue IDs are correctly formatted

## Usage

### From Command Line

To rebuild all HSA output from classified articles:

```bash
python scripts/rebuild_hsa_output.py
```

With custom directories:

```bash
python scripts/rebuild_hsa_output.py --input-dir custom_input --output-dir custom_output
```

### From Python

```python
from pathlib import Path
from src.formatter.hsa_formatter import HSAFormatter

# Initialize the formatter
formatter = HSAFormatter(output_dir=Path("output/hsa-ready"))

# Process a single article
article = {
    "headline": "Big News Story", 
    "body": "Article content...",
    "source_issue": "per_atlanta-constitution_1922-01-15_54_210" 
    # Date will be extracted from the source_issue
}
formatter.save_article(article)

# Process a batch of articles
articles = [article1, article2, article3]
formatter.process_batch(articles)

# Process all articles in a directory
formatter.process_directory("output/classified", recursive=True)
```

## Output Structure

HSA-ready articles are organized in the output directory with the following structure:

```
output/hsa-ready/
  └── YYYY/
      └── MM/
          └── DD/
              └── article-title-timestamp.json
```

## HSA JSON Format

The final JSON format follows this structure:

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