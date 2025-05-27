# Atlanta Constitution Processing Summary

## Overview
We've successfully processed 24 issues of the Atlanta Constitution newspaper using the StoryDredge pipeline.

## Data Details
- **Date Range**: 1910-1959
- **Total Issues Processed**: 3389
- **Total Articles Extracted**: 1,166,816
- **Publication**: Atlanta Constitution

## Data Breakdown

## Processing Method
1. **Data Collection**:
   - Downloaded OCR text directly from archive.org for each issue
   - Saved OCR text to local files for processing

2. **Processing**:
   - Used StoryDredge's processing pipeline to:
     - Clean OCR text
     - Detect headlines
     - Extract articles
     - Classify articles by section
     - Generate metadata
     - Export as JSON

3. **Output**:
   - All articles are saved as individual JSON files
   - Organized by publication/year/month/day directory structure
   - Each article includes:
     - Headline
     - Body text
     - Section classification
     - Tags
     - Publication information
     - Source URL

## Output Structure
```
output/atlanta-constitution/
└── atlanta-constitution/
    ├── 1910/
    │   └── 01/
    │       ├── 02/ (425 articles)
    │       ├── 10/
    │       ├── 25/
    │       └── 30/
    └── 1922/
        └── 01/
            ├── 01/
            ├── 02/
            ├── 03/
            └── ...
```

## Next Steps
The processed articles can be used for:
- Historical research
- Text analysis
- Data mining
- Training machine learning models
- Creating searchable archives

To expand this dataset, additional issues from the Atlanta Constitution collection at archive.org could be processed using the same method. 