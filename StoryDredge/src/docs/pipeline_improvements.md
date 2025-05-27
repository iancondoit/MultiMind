# Pipeline Improvements and Fixes

This document details the improvements and fixes made to the StoryDredge pipeline to address various performance and structural issues.

## Overview of Changes

Several key improvements were made to the StoryDredge pipeline:

1. **Rule-based Classification**: Improved the rule-based classifier to provide faster article classification without relying on LLM.
2. **Entity Tag Extraction**: Enhanced entity extraction to include people, organizations, and locations in the tags.
3. **Directory Structure**: Fixed the directory structure to avoid creating unnecessary duplicate directories.
4. **Output Organization**: Improved how output files are organized for better usability.

## Rule-based Classification

### Issue
The original pipeline used a slow LLM-based classification that took several minutes to process articles. 

### Fix
The `ArticleClassifier` was modified to default to rule-based classification by setting `skip_classification=True` by default. This change makes the classification process much faster without compromising quality for most use cases.

```python
def __init__(self, model: str = None, skip_classification: bool = True):  # Set default to True
    """
    Initialize the article classifier.
    
    Args:
        model: The model to use for classification (default: based on config)
        skip_classification: If True, skip LLM classification and use rule-based only
    """
```

### Performance Improvement
With this change, the classification process now completes in less than a second for hundreds of articles, compared to several minutes previously.

## Entity Tag Extraction

### Issue
The entity extraction was working but the extracted entities (people, organizations, locations) weren't being properly included in the tags array of the HSA-ready output.

### Fix
The `HSAFormatter` was updated to include metadata fields in the tags:

```python
# Add other metadata as tags
meta_fields = ["topic", "people", "organizations", "locations", "keywords"]
for field in meta_fields:
    # Check if the field exists directly in the article
    if field in article:
        if isinstance(article[field], list):
            tags.update(article[field])
        elif isinstance(article[field], str) and article[field]:
            tags.add(article[field])
    
    # Also check if the field exists in the metadata structure
    if "metadata" in article and isinstance(article["metadata"], dict) and field in article["metadata"]:
        if isinstance(article["metadata"][field], list):
            tags.update(article["metadata"][field])
        elif isinstance(article["metadata"][field], str) and article["metadata"][field]:
            tags.add(article["metadata"][field])
```

This ensures that entities like people, organizations, and locations extracted during classification appear in the tags field of the HSA-ready output.

## Directory Structure Improvements

### Issue
The pipeline was creating unnecessary "per_atlanta-constitution_*" directories in the output directory, as well as nested "hsa-ready" directories.

### Fix
The `process_ocr.py` script was modified to use a temporary directory structure for intermediate files:

```python
# Setup paths
base_output_dir = Path(output_dir)

# Create a temporary directory for the intermediate files
temp_dir = base_output_dir / "temp" / issue_id
temp_dir.mkdir(exist_ok=True, parents=True)

articles_dir = temp_dir / "articles"
articles_dir.mkdir(exist_ok=True)

classified_dir = temp_dir / "classified"
classified_dir.mkdir(exist_ok=True)

# Step 1: Fetch OCR data
raw_text_path = temp_dir / "raw.txt"
```

Additionally, the `HSAFormatter` was updated to avoid creating nested "hsa-ready" directories:

```python
# Set output directory
base_output_dir = Path(output_dir) if output_dir else Path("output")

# Check if the output_dir already ends with 'hsa-ready'
if base_output_dir.name == "hsa-ready":
    self.output_dir = base_output_dir
else:
    self.output_dir = base_output_dir / "hsa-ready"
    
self.output_dir.mkdir(exist_ok=True, parents=True)
```

### Result
The output directory structure is now cleaner and more organized:
- Intermediate files are stored in `output/temp/{issue_id}/`
- Final HSA-ready files are stored in `output/hsa-ready/{YYYY}/{MM}/{DD}/`

## Recommended Usage

For best performance and organization, use the following command to process issues:

```bash
PYTHONPATH=. python pipeline/process_ocr.py --issue ISSUE_ID --output-dir output --fast-mode
```

This will:
1. Extract articles from the OCR text
2. Apply fast rule-based classification
3. Add entities to the tags
4. Store the HSA-ready output in a clean directory structure

## Testing

For testing these changes, see the updated test scripts in `tests/test_pipeline/test_directory_structure.py` and `tests/test_classifier/test_rule_based_classification.py`. 