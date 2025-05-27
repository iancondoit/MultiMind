# OCR Cleaner Component

The OCR Cleaner component is responsible for cleaning and normalizing OCR text from newspaper scans. It removes common OCR artifacts, normalizes whitespace, and filters out non-content pages to prepare the text for article splitting and classification.

## Overview

The OCR Cleaner is the second component in the StoryDredge pipeline. It:

1. Normalizes whitespace and line endings
2. Removes noise patterns like separator lines
3. Corrects common OCR errors
4. Filters out non-content pages like copyright notices and advertisements
5. Prepares clean text for the splitter component

## Key Features

### Text Normalization
- Normalizes whitespace and line endings
- Removes excessive line breaks
- Standardizes paragraph structure

### OCR Error Correction
- Fixes common OCR misrecognitions
- Corrects typical character substitutions (e.g., "Uie" → "the")
- Standardizes punctuation

### Page Structure Analysis
- Identifies and removes copyright pages
- Filters out index pages and advertisements
- Preserves actual content pages

### Content Filtering
- Removes noise patterns like separator lines
- Filters out irrelevant content
- Maintains semantic structure of the text

### Progress Reporting
- Integration with the StoryDredge progress tracking system
- Real-time processing status

## Usage

### Basic Usage

```python
from src.cleaner.ocr_cleaner import OCRCleaner

# Create a cleaner instance
cleaner = OCRCleaner()

# Clean OCR text
raw_text = "Uie quick brown fox jumps over Uiat lazy dog wiUi ease."
cleaned_text = cleaner.clean_text(raw_text)

print(cleaned_text)  # "The quick brown fox jumps over that lazy dog with ease."
```

### Processing a File

```python
from pathlib import Path
from src.cleaner.ocr_cleaner import OCRCleaner

# Create a cleaner instance
cleaner = OCRCleaner()

# Process a file
input_file = Path("data/raw/newspaper_1906_04_19.txt")
output_file = Path("data/cleaned/newspaper_1906_04_19_cleaned.txt")

result = cleaner.process_file(input_file, output_file)

if result:
    print(f"Successfully cleaned file and saved to: {result}")
else:
    print("Failed to clean file")
```

### Using Default Output Path

```python
from pathlib import Path
from src.cleaner.ocr_cleaner import OCRCleaner

# Create a cleaner instance
cleaner = OCRCleaner()

# Process a file with default output path (adds -clean suffix)
input_file = Path("data/raw/newspaper_1906_04_19.txt")
result = cleaner.process_file(input_file)

# Result will be: data/raw/newspaper_1906_04_19-clean.txt
```

## Configuration

The OCR Cleaner component can be configured through the StoryDredge configuration system. The relevant settings are in the `cleaner` section of the pipeline configuration file:

```yaml
cleaner:
  enabled: true
  debug_mode: false
  timeout_seconds: 300
  normalize_whitespace: true
  normalize_punctuation: true
  normalize_quotes: true
  fix_ocr_errors: true
  remove_boilerplate: true
  min_content_length: 50
```

## Implementation Details

### Core Classes

- **OCRCleaner**: Main class for cleaning and normalizing OCR text

### Key Methods

- **clean_text(text)**: Cleans and normalizes OCR text
- **process_file(input_file, output_file)**: Processes an OCR text file
- **_normalize_whitespace(text)**: Normalizes whitespace in text
- **_remove_copyright_pages(text)**: Removes copyright and non-content pages

### Dependencies

- **re**: Regular expression library for pattern matching
- **logging**: Logging facility
- **pathlib**: For managing file paths

## Error Handling

The component uses proper error handling:

- Proper logging of errors
- Graceful handling of missing files
- Fallback measures for empty or malformed content

## Future Enhancements

Potential improvements for the OCR Cleaner component:

1. Enhanced OCR error correction with dictionaries
2. Machine learning-based noise detection
3. Language-specific cleaning operations
4. More sophisticated page structure analysis
5. Parallel processing for large files 