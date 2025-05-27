# Testing with the Atlanta Constitution Dataset

This document provides instructions for testing the StoryDredge pipeline with the Atlanta Constitution newspaper archive from archive.org.

## Overview

The [Atlanta Constitution newspaper collection](https://archive.org/details/pub_atlanta-constitution) on archive.org provides an excellent test set for the StoryDredge pipeline:

- It's a major historical newspaper with issues spanning from 1881 to 1945
- Most issues have OCR text available
- It contains diverse content types (news, advertisements, editorials)
- The OCR quality varies across different time periods

## Test Dataset Preparation

We've created tools to easily prepare test datasets from the Atlanta Constitution archive:

### Using the Dataset Preparation Script

Use the `prepare_atlanta_constitution_dataset.py` script to prepare a dataset of OCR files for testing:

```bash
python scripts/prepare_atlanta_constitution_dataset.py --start-date 1922-01-01 --end-date 1922-01-31 --sample-size 10
```

This will:
1. Search for Atlanta Constitution issues within the specified date range
2. Check OCR availability for each issue
3. Create a JSON file with issue metadata for batch processing
4. Download a sample of OCR files for immediate testing

### Direct Testing Approach

For direct testing with specific issues, use the `test_atlanta_constitution_direct.py` script:

```bash
PYTHONPATH=. python scripts/test_atlanta_constitution_direct.py
```

This script:
1. Downloads OCR files from archive.org for two sample issues from January 1922
2. Cleans the OCR text using the pipeline's cleaner component
3. Splits the text into articles using the splitter component
4. Saves the results for review

## Key Findings

Through our testing with the Atlanta Constitution dataset, we've identified several important considerations:

1. **Archive.org Access**: When accessing OCR files from archive.org, follow HTTP redirects when downloading. The URLs redirect to the actual content location.

2. **OCR Quality**: The OCR quality varies across issues. Issues from the 1920s generally have good OCR quality that works well with our headline detection algorithms.

3. **Article Extraction**: The Atlanta Constitution typically yields hundreds of articles per issue (500+ in some cases), demonstrating that our splitter works well with real-world newspaper content.

4. **Document Structure**: The Atlanta Constitution issues from the 1920s have consistent structure with clear headlines, making them ideal for testing the article extraction components.

## Known Issues

1. **HTTP Redirects**: When directly downloading OCR text from archive.org, always use tools that follow HTTP redirects (curl's -L flag or equivalent).

2. **Classification Load**: The large number of articles per issue means classification can be time-consuming. Consider processing a subset of articles when testing classification functionality.

3. **OCR Artifacts**: Some common OCR artifacts in the Atlanta Constitution include confusion between "t" and "i", and "m" and "in", which the cleaner component should address.

## Recommended Test Issues

These Atlanta Constitution issues have been verified to work well with the pipeline:

- January 1, 1922: `per_atlanta-constitution_1922-01-01_54_203`
- January 2, 1922: `per_atlanta-constitution_1922-01-02_54_204`

These issues have good OCR quality and a variety of content types.

## Running Tests

### Unit and Integration Tests

Run the dedicated tests for the Atlanta Constitution dataset:

```bash
# Run just the Atlanta Constitution tests
pytest tests/test_pipeline/test_atlanta_constitution.py -v

# Run with individual test selection
pytest tests/test_pipeline/test_atlanta_constitution.py::TestAtlantaConstitution::test_fetch_atlanta_issue -v
```

### Processing a Single Issue

Process a single Atlanta Constitution issue through the pipeline:

```bash
python pipeline/main.py --issue pub_atlanta-constitution_19220101
```

### Batch Processing

Process multiple issues from a prepared dataset:

```bash
python pipeline/main.py --issues-file data/atlanta-constitution/atlanta_constitution_19220101_to_19220131.json
```

To utilize parallel processing:

```bash
python pipeline/main.py --issues-file data/atlanta-constitution/atlanta_constitution_19220101_to_19220131.json --workers 4
```

## Verifying Results

After processing, examine the results:

1. **Raw OCR Text**: Check the raw downloaded text in the issue output directory
2. **Cleaned Text**: Review the cleaning/normalization results
3. **Article Extraction**: Verify that articles were correctly split from the full issue
4. **Article Classification**: Check the metadata extraction and classification accuracy
5. **HSA Output**: Ensure the HSA-ready JSON files have the required format

The output will be organized in:
```
output/
├── [issue_id]/
│   ├── raw.txt
│   ├── cleaned.txt
│   ├── articles/
│   │   └── article_NNNN.json
│   └── classified/
│       └── article_NNNN.json
└── hsa-ready/
    └── YYYY/MM/DD/
        └── article_files.json
```

## Common Issues and Troubleshooting

### OCR Quality Variations

- Early issues (1880s-1890s) may have lower OCR quality
- Issues from the 1920s-1940s generally have better OCR quality
- Adjust cleaner and splitter parameters if needed for different time periods

### Rate Limiting

Archive.org may rate-limit requests if too many are made in quick succession. If you encounter errors:

1. Reduce the number of parallel workers
2. Add delays between requests by adjusting the rate limiter configuration
3. Use the checkpoint feature to resume interrupted processing

### Missing OCR

Some issues may not have OCR text available. The dataset preparation script automatically filters these out. If processing fails for an issue, check if OCR is available by examining the metadata at:

```
https://archive.org/metadata/[issue_id]/files
```

Look for a file named `[issue_id]_djvu.txt`.

## Performance Benchmarking

To benchmark performance with the Atlanta Constitution dataset:

```bash
python pipeline/main.py --issues-file data/atlanta-constitution/atlanta_constitution_19220101_to_19220131.json --benchmark
```

This will run the pipeline and analyze performance bottlenecks.

## Adding More Test Data

To expand the test dataset:

1. Use the preparation script with different date ranges
2. Combine multiple issues files into a larger dataset
3. Focus on specific time periods to test OCR quality variations

For example, to create datasets from different decades:

```bash
# 1890s sample
python scripts/prepare_atlanta_constitution_dataset.py --start-date 1890-01-01 --end-date 1890-01-31 --output-dir data/atlanta-constitution/1890s

# 1920s sample
python scripts/prepare_atlanta_constitution_dataset.py --start-date 1920-01-01 --end-date 1920-01-31 --output-dir data/atlanta-constitution/1920s

# 1940s sample
python scripts/prepare_atlanta_constitution_dataset.py --start-date 1940-01-01 --end-date 1940-01-31 --output-dir data/atlanta-constitution/1940s
``` 