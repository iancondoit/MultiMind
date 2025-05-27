# Atlanta Constitution Processing Pipeline

This document explains how to process issues of the Atlanta Constitution newspaper using the StoryDredge pipeline.

## Overview

The Atlanta Constitution is a major newspaper published in Atlanta, Georgia since 1868. The Internet Archive has a collection of digitized issues available at: https://archive.org/details/pub_atlanta-constitution

This project extracts articles from these issues and processes them into a structured format for analysis and research.

## Requirements

- Python 3.7+
- StoryDredge pipeline
- Internet connection to access archive.org

## Workflow

The process consists of three main steps:

1. **Fetching**: Find and download OCR text for issues in a specified date range
2. **Processing**: Extract articles, clean text, and classify content
3. **Reporting**: Generate statistics about the processed data

## Scripts

We've created several scripts to automate this workflow:

- `fetch_atlanta_issues.py`: Fetches issue IDs from archive.org using the ArchiveFetcher 
- `manual_process.py`: Downloads OCR text directly from archive.org
- `batch_process_local_issues.py`: Processes downloaded OCR files with the StoryDredge pipeline
- `fetch_and_process_100_more.py`: All-in-one script that fetches, downloads, and processes issues
- `update_summary.py`: Updates the summary markdown file with statistics

## How to Process More Issues

To process more issues of the Atlanta Constitution:

1. Run the all-in-one script with a new date range:

```bash
./fetch_and_process_100_more.py --start-date 1930-01-01 --end-date 1935-12-31 --max-issues 100
```

2. Wait for the processing to complete. This may take some time depending on the number of issues.

3. Update the summary statistics:

```bash
./update_summary.py
```

## Processing Parameters

The `fetch_and_process_100_more.py` script accepts the following parameters:

- `--start-date`: Start date for issue search (YYYY-MM-DD)
- `--end-date`: End date for issue search (YYYY-MM-DD)
- `--max-issues`: Maximum number of issues to process
- `--threads`: Number of threads for parallel downloads

## Output Structure

All processed articles are saved in the following directory structure:

```
output/atlanta-constitution/
└── atlanta-constitution/
    └── YEAR/
        └── MONTH/
            └── DAY/
                └── YEAR-MONTH-DAY--HEADLINE.json
```

Each article is saved as a JSON file with the following structure:

```json
{
  "headline": "Article headline",
  "body": "Full article text",
  "section": "Classified section (e.g., news, sports, business)",
  "tags": ["Automatically generated tags"],
  "timestamp": "YYYY-MM-DDT00:00:00.000Z",
  "publication": "Atlanta Constitution",
  "source_issue": "Issue identifier",
  "source_url": "URL to the original issue on archive.org"
}
```

## Troubleshooting

- **HTTP 302 errors**: Sometimes archive.org redirects requests. If this happens, try using the direct URL approach in `manual_process.py`.
- **OCR quality**: The quality of OCR varies by issue. Older issues may have more OCR errors.
- **Rate limiting**: Be mindful of archive.org's rate limits. Spread out large batch processing over time.

## Next Steps

After processing, you can:

1. Analyze article content for trends and patterns
2. Build a searchable database of articles
3. Apply machine learning to extract insights
4. Create visualizations of article frequency over time
5. Develop web interfaces to browse the collection

For more detailed information about the StoryDredge pipeline, refer to the main project documentation. 