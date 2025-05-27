# HSA-Ready Format Documentation

This document describes the Human Story Atlas (HSA) ready format used by the StoryDredge pipeline.

## Overview

The HSA-ready format is a JSON structure designed to standardize historical newspaper articles for integration with the Human Story Atlas system. It captures key metadata while preserving the original content.

## Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `headline` | String | The headline or title of the article |
| `body` | String | The full text content of the article |
| `tags` | Array of Strings | Keywords or categories associated with the article |
| `section` | String | The newspaper section (e.g., "news", "sports") |
| `timestamp` | String | ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SS.000Z) |
| `publication` | String | Name of the source publication |
| `source_issue` | String | Original issue identifier (e.g., archive.org ID) |
| `source_url` | String | URL to the original source if available |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `byline` | String | Author of the article |
| `dateline` | String | Location and date information as it appeared in the original |

### Validation Rules

- `section` must be one of the valid section values (see below)
- `timestamp` must be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.000Z)
- `tags` must be a non-empty array of strings

### Valid Section Values

- `news`: General news articles
- `opinion`: Opinion pieces, editorials
- `sports`: Sports coverage
- `business`: Business and financial news
- `entertainment`: Arts, entertainment, and culture
- `politics`: Political news and coverage
- `science`: Science news and discoveries
- `health`: Health and medical news
- `technology`: Technology news
- `education`: Education-related news
- `local`: Local news
- `national`: National news
- `international`: International news
- `weather`: Weather reports
- `obituaries`: Death notices and obituaries
- `lifestyle`: Lifestyle articles
- `culture`: Cultural articles and reviews
- `arts`: Art-related news and reviews
- `food`: Food and dining articles
- `travel`: Travel articles
- `other`: Articles that don't fit into other categories

## Example

```json
{
  "headline": "BUILDING BOOM CONTINUES",
  "body": "BUILDING BOOM CONTINUES\n\nwing an unprecedented building boom in Atlanta, contractors report...",
  "tags": [
    "news",
    "construction",
    "economy",
    "Atlanta"
  ],
  "section": "news",
  "timestamp": "1922-01-01T00:00:00.000Z",
  "publication": "The Atlanta Constitution",
  "source_issue": "per_atlanta-constitution_1922-01-01_54_203",
  "source_url": "https://archive.org/details/per_atlanta-constitution_1922-01-01_54_203",
  "byline": "HENSON TATUM"
}
```

## Special Field Handling

### Bylines

Bylines are extracted from several possible patterns:

1. **Pattern 1**: From direct `byline` field in the source data
   ```json
   {
     "headline": "MAYOR'S ADDRESS TO COUNCIL",
     "byline": "Special Correspondent",
     "body": "The mayor addressed the city council yesterday regarding..."
   }
   ```

2. **Pattern 2**: When title/headline starts with "BY" (which is then moved to the byline field)
   ```json
   {
     "title": "BY HENSON TATUM",
     "body": "BUILDING BOOM CONTINUES\n\nDuring an unprecedented building boom..."
   }
   ```
   Becomes:
   ```json
   {
     "headline": "BUILDING BOOM CONTINUES",
     "byline": "HENSON TATUM",
     "body": "BUILDING BOOM CONTINUES\n\nDuring an unprecedented building boom..."
   }
   ```

3. **Pattern 3**: When first line of body starts with "BY"
   ```json
   {
     "title": "STOCK MARKETS IN DECLINE",
     "body": "BY FINANCIAL REPORTER\n\nStock markets showed significant decline..."
   }
   ```
   Becomes:
   ```json
   {
     "headline": "STOCK MARKETS IN DECLINE",
     "byline": "FINANCIAL REPORTER",
     "body": "BY FINANCIAL REPORTER\n\nStock markets showed significant decline..."
   }
   ```

When extracting bylines, the system removes the prefix "BY " and preserves only the author's name.

### Timestamps

Timestamps are standardized to ISO 8601 format with UTC timezone. The system will attempt to extract dates from:
1. Archive.org identifiers (e.g., `per_atlanta-constitution_1922-01-01_54_203`)
2. Explicit date fields in the source data
3. Fallback to current date if no date information is available

### Tags

Tags are generated from:
1. Explicit tags in the source data
2. Classification metadata (topic, people, organizations, locations)
3. Fallback to using the section name as a tag if no tags are available

## File Organization

HSA-ready files are organized into a directory structure by date:

```
output/hsa-ready/
├── 1922/
│   ├── 01/
│   │   ├── 01/
│   │   │   ├── building-boom-continues-1234567890.json
│   │   │   └── ...
│   │   ├── 02/
│   │   │   └── ...
│   └── ...
└── ...
```

This makes it easy to locate articles by their publication date.

## Implementation Notes

- A default headline will be extracted from the first non-byline line of the article body if no headline is specified.
- If no body text is found, a placeholder "No content available" will be used.
- If no tags are found, the section name will be used as a default tag.
- Articles that fail validation are logged but not included in the final output. 