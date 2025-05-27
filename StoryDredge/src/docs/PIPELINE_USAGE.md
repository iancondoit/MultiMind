# Universal Newspaper Pipeline Usage Guide

## Overview

The Universal Newspaper Pipeline provides a streamlined process for converting newspaper issues from archive.org into a format compatible with the Human Story Atlas (HSA). This unified pipeline combines multiple processing steps:

1. **Fetching** OCR text from archive.org
2. **Cleaning and normalizing** the OCR text
3. **Splitting** the text into individual articles
4. **Classifying** articles by type/category
5. **Formatting** and saving in the HSA-ready structure

The key advantage of this unified pipeline is that it processes each issue in memory without creating unnecessary intermediate directories, and produces a clean, standardized output structure.

## Output Directory Structure

All processed files are stored in a standardized directory structure:

```
output/
└── hsa-ready-final/
    └── publication-name/
        └── year/
            └── month/
                └── day/
                    ├── yyyy-mm-dd--article-title-1.json
                    ├── yyyy-mm-dd--article-title-2.json
                    └── ...
```

For example, articles from the Atlanta Constitution from January 1, 1922 would be stored in:
```
output/hsa-ready-final/atlanta-constitution/1922/01/01/
```

## Usage

The pipeline script can process either a single newspaper issue or multiple issues from a file.

### Basic Command Structure

```bash
python scripts/universal_newspaper_pipeline.py [options]
```

### Command-line Options

| Option | Description |
|--------|-------------|
| `--issue ISSUE_ID` | Process a single issue with the given ID |
| `--issues-file FILE` | Process multiple issues listed in the specified file |
| `--output DIR` | Output directory (default: `output/hsa-ready-final`) |

### Examples

#### Processing a Single Issue

To process a single newspaper issue:

```bash
python scripts/universal_newspaper_pipeline.py --issue per_atlanta-constitution_1922-01-01_54_203
```

This will process the Atlanta Constitution issue from January 1, 1922, and store the extracted articles in the default output directory.

#### Processing Multiple Issues

To process multiple issues listed in a file:

```bash
python scripts/universal_newspaper_pipeline.py --issues-file data/issue_list.txt --output output/hsa-ready
```

The `issue_list.txt` file should contain one issue ID per line:

```
per_atlanta-constitution_1922-01-01_54_203
per_atlanta-constitution_1922-01-02_54_204
per_atlanta-constitution_1922-01-03_54_205
...
```

## Issue ID Format

The pipeline supports various issue ID formats from archive.org:

- `per_atlanta-constitution_1922-01-01_54_203`
- `pub_atlanta-constitution_19220101`

The pipeline extracts publication name and date information from these IDs to organize the output correctly.

## Requirements

Before running the pipeline, ensure:

1. The project dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Your archive.org credentials are properly configured if fetching directly from archive.org

## Logging and Reporting

The pipeline logs its progress and any errors to:

- Console output
- Log files in the `logs/` directory
- A JSON report file in the `reports/` directory when processing multiple issues

## Comparison with Previous Workflow

Previously, processing newspaper issues required several separate steps:

1. Run `test_atlanta_constitution_direct.py` to download and extract articles
2. Run `run_classification.py` to classify the extracted articles
3. Run `migrate_hsa_data.py` to organize the classified articles into the HSA structure

This created multiple intermediate directories and required manual tracking of the process.

The new Universal Newspaper Pipeline combines all these steps into a single command, eliminating intermediate directories and streamlining the entire process.

## Troubleshooting

### Common Issues

- **Missing OCR Data**: Ensure the issue ID is valid and OCR data is available on archive.org
- **Publication/Date Extraction Failure**: Check that the issue ID follows one of the supported formats
- **No Articles Extracted**: This may indicate unusual formatting in the OCR; try adjusting the splitter configuration

### Debugging

For detailed debugging, check the log files in the `logs/` directory. Each pipeline run creates a timestamped log file with complete processing information. 