# Batch Processor

The Batch Processor is a pipeline orchestration component that processes multiple newspaper issues through the entire StoryDredge pipeline.

## Overview

The Batch Processor orchestrates the end-to-end processing of newspaper issues from archive.org through OCR cleaning, article splitting, and classification. It provides robust error handling, progress tracking, and checkpoint/resume capability for long-running batch jobs.

## Features

- **Complete Pipeline Integration**: Connects all processing components (fetcher, cleaner, splitter, classifier)
- **Batch Processing**: Handles multiple issues sequentially
- **Progress Tracking**: Real-time progress updates with estimated completion time
- **Error Handling**: Comprehensive error handling with retry logic
- **Checkpointing**: Automatically saves progress for resume capability
- **Detailed Reporting**: Generates processing reports and logs

## Usage

### Basic Usage

```python
from src.pipeline.batch_processor import BatchProcessor

# Create a batch processor
processor = BatchProcessor(
    output_dir="output",
    checkpoint_file="checkpoint.json",
    max_retries=3
)

# Process a single issue
processor.process_issue("archive_org_issue_id")

# Process a batch of issues
issue_ids = ["issue1", "issue2", "issue3"]
report = processor.process_batch(issue_ids)
```

### Command-line Interface

The batch processor can be used from the command line:

```bash
python -m src.pipeline.batch_processor --input issues.txt --output output_dir
```

Where `issues.txt` contains archive.org issue IDs, one per line.

### Overnight Processing Example

For long-running overnight processing, use the provided example script:

```bash
python examples/overnight_processing.py --input issue_list.txt --output output_dir
```

Options:
- `--input`, `-i`: File containing archive.org issue IDs (required)
- `--output`, `-o`: Output directory for processed results (default: "output")
- `--checkpoint`: Checkpoint file for resume capability (default: "checkpoint.json")
- `--max-retries`: Maximum retries for failed issues (default: 3)
- `--model`: Ollama model to use for classification (optional)
- `--concurrency`: Number of concurrent classifications (optional)

## Output Structure

The batch processor creates the following directory structure:

```
output/
├── issue_id_1/
│   ├── raw.txt
│   ├── cleaned.txt
│   ├── articles/
│   │   ├── article_0001.json
│   │   ├── article_0002.json
│   │   └── ...
│   └── classified/
│       ├── article_0001.json
│       ├── article_0002.json
│       └── ...
├── issue_id_2/
│   └── ...
└── processing_report.json
```

## Configuration

The batch processor uses the standard StoryDredge configuration system. The main relevant settings in `config/pipeline.yml`:

```yaml
parallel_processes: 4  # Overall parallelism

classifier:
  concurrency: 2       # Concurrent article classifications
  batch_size: 10       # Batch size for classification
  model_name: "llama2" # Ollama model to use
```

## Checkpointing

The batch processor keeps track of processed issues in a checkpoint file (default: `checkpoint.json`). If processing is interrupted and restarted, the processor will:

1. Load the checkpoint file
2. Skip already processed issues
3. Continue with unprocessed issues

This allows for efficient resumption of long-running jobs.

## Error Handling

The batch processor includes comprehensive error handling:

- **Issue-level retries**: Automatically retries failed issues (configurable)
- **Isolation**: Errors in one issue don't affect processing of others
- **Logging**: Detailed error logs for troubleshooting
- **Failed issue tracking**: Creates a list of failed issues for manual inspection

## Performance Considerations

For optimal overnight batch processing:

1. **Concurrency**: Set appropriate concurrency based on your system's capabilities
2. **Model Selection**: Choose the appropriate Ollama model
3. **Disk Space**: Ensure sufficient disk space for output files
4. **Memory Usage**: Monitor memory usage during long batch jobs
5. **Network Stability**: Ensure stable internet connection for archive.org access

## Implementation Details

### Classes

- **BatchProcessor**: Main class for orchestrating the pipeline
  - `process_issue(issue_id)`: Process a single issue
  - `process_batch(issue_ids)`: Process multiple issues
  - `_load_checkpoint()`: Load from checkpoint file
  - `_save_checkpoint()`: Save progress to checkpoint file

### Integration Points

The batch processor integrates with:

- **ArchiveFetcher**: For downloading newspaper issues
- **OCRCleaner**: For cleaning OCR text
- **ArticleSplitter**: For splitting text into articles
- **ArticleClassifier**: For classifying articles

## Extending

To extend the batch processor:

1. **Add new processing steps**: Modify `process_issue()` method
2. **Add parallelism**: Implement concurrent issue processing
3. **Add more reporting**: Enhance the reporting structure
4. **Add optimization**: Implement resource-aware processing

## Testing

To test the batch processor, run:

```bash
python -m pytest tests/test_pipeline/test_batch_processor.py -v
``` 