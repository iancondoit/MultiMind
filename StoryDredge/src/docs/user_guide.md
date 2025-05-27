# StoryDredge User Guide

This guide provides comprehensive instructions for using the StoryDredge pipeline to process historical newspaper OCR from archive.org and prepare it for integration with the Human Story Atlas (HSA).

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Pipeline Configuration](#pipeline-configuration)
4. [Processing Multiple Issues](#processing-multiple-issues)
5. [Parallel Processing](#parallel-processing)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Common Issues and Troubleshooting](#common-issues-and-troubleshooting)
8. [Performance Optimization](#performance-optimization)
9. [Output Format and Structure](#output-format-and-structure)
10. [Advanced Usage](#advanced-usage)

## Installation

### Prerequisites

- Python 3.8 or higher
- Ollama for local LLM support (for classification)
- Sufficient disk space for caching downloaded OCR text
- Internet connection for downloading from archive.org

### Setup Process

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/storydredge.git
   cd storydredge
   ```

2. Run the automated setup script (recommended):
   ```bash
   ./dev-setup.sh
   ```

   This script will:
   - Check Python version
   - Create and activate a virtual environment
   - Install dependencies
   - Set up the required directory structure
   - Configure git hooks for code quality

3. Manual setup (alternative):
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

4. Set up Ollama for local LLM support:
   - Visit https://ollama.ai/download for platform-specific instructions
   - Install the recommended model (default is llama2):
     ```bash
     ollama pull llama2
     ```

## Basic Usage

### Processing a Single Newspaper Issue

To process a single newspaper issue, use:

```bash
python pipeline/main.py --issue <archive_id>
```

Example:
```bash
python pipeline/main.py --issue sn84026749-19220101
```

The pipeline will:
1. Download OCR text from archive.org
2. Clean and normalize the text
3. Split the text into individual articles
4. Classify the articles with the local LLM
5. Format the articles for HSA integration
6. Save the output in the designated directory

### Checking the Results

After processing, the results are saved in the `output` directory by default, organized by date:

```bash
output/hsa-ready/YYYY/MM/DD/
```

Each article is saved as a separate JSON file with a structured format.

## Pipeline Configuration

### Command-Line Options

The pipeline can be configured using various command-line options:

- `--issue`: Process a single archive.org issue ID
- `--issues-file`: Path to a JSON file containing multiple issue IDs
- `--workers`: Number of issues to process in parallel
- `--sequential`: Force sequential processing even if parallel workers are specified
- `--output-dir`: Directory for output files (default: "output")
- `--checkpoint-file`: Checkpoint file for resume capability (default: "checkpoint.json")
- `--benchmark`: Run benchmarks after processing

### Configuration Files

You can customize component behavior through configuration files in the `config` directory:

- `config/fetcher.yml`: Configure fetcher behavior (caching, retries, timeouts)
- `config/cleaner.yml`: Configure OCR cleaning options (patterns, rules)
- `config/splitter.yml`: Configure article splitting parameters (headline detection)
- `config/classifier.yml`: Configure classification settings (model, prompt templates)
- `config/formatter.yml`: Configure output formatting options

## Processing Multiple Issues

### Creating an Issues File

Create a JSON file containing the list of issues to process:

```json
{
  "issues": [
    "sn84026749-19220101",
    "sn84026749-19220102",
    "sn84026749-19220103"
  ]
}
```

Alternatively, the file can be a simple JSON array:

```json
[
  "sn84026749-19220101",
  "sn84026749-19220102",
  "sn84026749-19220103"
]
```

### Running Batch Processing

Process all issues in the file:

```bash
python pipeline/main.py --issues-file issues.json
```

### Checkpoint and Resume

The pipeline supports checkpointing, which allows you to resume processing if it's interrupted:

```bash
python pipeline/main.py --issues-file issues.json --checkpoint-file my_checkpoint.json
```

If processing is interrupted, simply run the same command again to resume from where it left off.

## Parallel Processing

### Enabling Parallel Processing

Process multiple issues in parallel for faster throughput:

```bash
python pipeline/main.py --issues-file issues.json --workers 4
```

This will process 4 issues simultaneously.

### Choosing the Optimal Worker Count

- For CPU-bound tasks, set workers approximately equal to your CPU core count
- For I/O-bound tasks, you can set workers higher than your CPU core count
- Start with a conservative number and increase gradually based on system performance

## Monitoring and Logging

### Log Files

The pipeline generates detailed logs in the `logs` directory:

```bash
logs/pipeline_YYYYMMDD_HHMMSS.log
```

### Real-Time Progress

During processing, the pipeline displays real-time progress information:

- Current issue being processed
- Overall batch progress
- Estimated time remaining
- Success/failure counts

## Common Issues and Troubleshooting

### Connection Issues

If you encounter connection problems with archive.org:

1. Check your internet connection
2. Verify that the issue ID is valid
3. Increase retry count and delay in `config/fetcher.yml`
4. Check if archive.org is experiencing downtime

### OCR Quality Issues

If the OCR quality is poor, leading to article extraction problems:

1. Adjust the splitter parameters in `config/splitter.yml` to be more forgiving
2. Use the aggressive mode for article extraction

### Classification Issues

If article classification is not working correctly:

1. Ensure Ollama is running and the selected model is available
2. Check the model's performance with the test script:
   ```bash
   python examples/test_classifier.py
   ```
3. Adjust the classification prompts in `config/classifier.yml`

## Performance Optimization

### Benchmarking

Run benchmarks to identify performance bottlenecks:

```bash
python -m src.benchmarking.pipeline_benchmarks --component all
```

### Optimizing Performance

To improve processing speed:

1. Enable parallel processing with an appropriate worker count
2. Use a local SSD for the cache directory
3. Use a faster LLM for classification if available
4. Allocate more memory to the LLM process

### Overnight Processing

For processing large batches overnight:

```bash
python examples/overnight_processing.py --issues-file issues.json --workers 4
```

This script includes additional monitoring and email notification when processing completes.

## Output Format and Structure

### Directory Structure

Output files are organized by date:

```
output/hsa-ready/YYYY/MM/DD/article_N.json
```

### JSON Format

Each article is saved as a JSON file with this structure:

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

### HSA Integration

The output files are ready for direct integration with the Human Story Atlas system, conforming to the HSA schema requirements.

## Advanced Usage

### Component Access

You can access individual components directly for custom processing:

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

# Custom processing pipeline
issue_id = "sn84026749-19220101"
ocr_text = fetcher.fetch_issue(issue_id)
cleaned_text = cleaner.clean(ocr_text)
articles = splitter.split(cleaned_text)
classified_articles = classifier.classify_batch(articles)
formatted_articles = formatter.format_batch(classified_articles)
```

### Customizing Classification

You can customize the classification prompts and behavior by modifying `config/classifier.yml` or by passing parameters directly:

```python
from src.classifier import ArticleClassifier

classifier = ArticleClassifier(
    model_name="llama2",
    temperature=0.1,
    custom_prompts=True,
    prompt_template_path="my_prompts/article_classification.txt"
)
```

### Extending the Pipeline

The modular architecture allows you to extend the pipeline with custom components. Create a new component that follows the input/output conventions of the existing components and integrate it into the pipeline. 

To execute the test pipeline:
```bash
python scripts/run_atlanta_constitution_test.py --prepare --test --run-pipeline
```

This will prepare a dataset from the Atlanta Constitution, run the tests, and process the issues through the pipeline. 