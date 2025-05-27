# HSA-Ready Data Restructuring Documentation

## Overview

This document describes the process used to restructure the StoryDredge HSA-ready data directory to ensure a clean, consistent structure for handoff to the Human Story Atlas (HSA) system.

## Goals

1. Organize data by publication, year, month, and day
2. Validate all files against HSA schema requirements
3. Fix any inconsistencies or missing data
4. Ensure all files follow consistent naming conventions
5. Remove any extraneous files (.DS_Store, .gitkeep, etc.)
6. Include all available publications (San Antonio Express-News and Atlanta Constitution)

## Structure

The restructured HSA-ready data follows this directory structure:

```
output/hsa-ready-clean/
├── [Publication]/                  # Publication name (e.g., san_antonio_express-news)
│   ├── YYYY/                       # Year (e.g., 1977) 
│   │   ├── MM/                     # Month (e.g., 08)
│   │   │   └── DD/                 # Day (e.g., 14)
│   │   │       └── article.json    # Individual article files
```

## Process

The restructuring was implemented through a series of scripts:

1. **Analysis** (`scripts/analyze_hsa_ready.py`)
   - Analyzed the existing HSA-ready directory structure
   - Identified valid and invalid files
   - Generated a report of publications, years, and issues

2. **Migration** (`scripts/migrate_hsa_data.py`)
   - Reorganized files into the new structure
   - Standardized file naming using headlines or unique IDs
   - Fixed timestamp formatting
   - Created publication-based directories

3. **Validation** (`scripts/validate_hsa_data.py`)
   - Validated all migrated files against HSA schema
   - Verified directory structure integrity
   - Identified any remaining issues

4. **Fixes** (`scripts/fix_hsa_validation_issues.py`)
   - Addressed validation issues found
   - Fixed missing or invalid values
   - Ensured 100% compliance with HSA schema

5. **Atlanta Constitution Processing** (`scripts/process_atlanta_constitution.py`)
   - Located Atlanta Constitution issues in output directory
   - Transformed classified articles to HSA-ready format
   - Added them to the cleaned directory structure

## File Format

Each HSA-ready JSON file contains the following structure:

```json
{
  "headline": "Article Headline",
  "byline": "Author Name or null",
  "dateline": "Location or null",
  "body": "Full article text content",
  "section": "news|editorial|sports|business|entertainment|lifestyle|other|unknown",
  "tags": ["tag1", "tag2", "..."],
  "timestamp": "YYYY-MM-DDT00:00:00.000Z",
  "publication": "Publication Name",
  "source_issue": "publication-name-YYYY-MM-DD",
  "source_url": "https://archive.org/details/publication-name-YYYY-MM-DD"
}
```

## Results Summary

- **Total articles**: 278 files in publication/year/month/day structure
- **Publications**: 
  - San Antonio Express-News (258 articles, 1970-1977)
  - Atlanta Constitution (20 articles, 1922)
- **Validation**: 100% of files pass schema validation
- **Fixed issues**: 7 files had validation issues, all successfully fixed

## Publications Details

### San Antonio Express-News
- **Articles**: 258
- **Years covered**: 1970, 1974, 1975, 1977
- **Content**: Primarily news articles with some editorial content

### Atlanta Constitution
- **Articles**: 20
- **Years covered**: 1922
- **Content**: Historical news articles from the early 20th century
- **Issues**: 
  - January 1, 1922
  - January 2, 1922

## Using the Restructured Data

To use the restructured HSA-ready data:

1. Navigate to the `output/hsa-ready-clean` directory
2. Files are organized by publication name, year, month, and day
3. All JSON files follow the standard HSA schema

## Scripts Reference

The following scripts were used in the restructuring process:

- **scripts/analyze_hsa_ready.py**: Analyzes the current HSA-ready data
- **scripts/migrate_hsa_data.py**: Migrates data to the new structure
- **scripts/validate_hsa_data.py**: Validates migrated data
- **scripts/fix_hsa_validation_issues.py**: Fixes validation issues
- **scripts/process_atlanta_constitution.py**: Processes Atlanta Constitution articles

To run these scripts:

```bash
# Analyze current data
python scripts/analyze_hsa_ready.py

# Migrate data to new structure
python scripts/migrate_hsa_data.py

# Process Atlanta Constitution data
python scripts/process_atlanta_constitution.py

# Validate migrated data
python scripts/validate_hsa_data.py

# Fix any validation issues
python scripts/fix_hsa_validation_issues.py
```

Reports for each step are saved in the `reports/` directory. 