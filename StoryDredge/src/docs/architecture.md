# StoryDredge Architecture

This document provides an overview of the StoryDredge architecture, explaining how the various components fit together to form a cohesive pipeline for processing newspaper OCR text.

## System Architecture Overview

StoryDredge follows a modular, pipeline-based architecture that processes newspaper issues through multiple stages. The system is designed to be:

1. **Modular**: Components can be swapped or improved independently
2. **Scalable**: Can process a single issue or batch process thousands
3. **Extensible**: New publications or formats can be added easily
4. **Resilient**: Handles errors gracefully and provides recovery mechanisms

## Components

### Core Components

The core components of the StoryDredge system are:

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐    ┌───────────┐
│           │    │           │    │           │    │           │    │           │
│  Fetcher  │───▶│  Cleaner  │───▶│ Splitter  │───▶│Classifier │───▶│ Formatter │
│           │    │           │    │           │    │           │    │           │
└───────────┘    └───────────┘    └───────────┘    └───────────┘    └───────────┘
```

1. **Fetcher** (`src/fetcher/`):
   - Retrieves OCR text from archive.org
   - Handles caching to minimize redundant downloads
   - Provides retry logic and error handling

2. **Cleaner** (`src/cleaner/`):
   - Normalizes OCR text by fixing common issues
   - Removes artifacts and standardizes formatting
   - Prepares text for article extraction

3. **Splitter** (`src/splitter/`):
   - Detects headlines and article boundaries
   - Extracts individual articles from the cleaned text
   - Handles different newspaper layouts and formats

4. **Classifier** (`src/classifier/`):
   - Categorizes articles by type (news, sports, opinion, etc.)
   - Extracts metadata like people, organizations, and locations
   - Uses NLP techniques to identify article content

5. **Formatter** (`src/formatter/`):
   - Transforms articles into the HSA-ready format
   - Ensures consistent output structure
   - Validates output against HSA requirements

### Pipeline Orchestration

The pipeline orchestration components coordinate the flow of data through the core components:

1. **Universal Pipeline** (`scripts/universal_newspaper_pipeline.py`):
   - Orchestrates the end-to-end process from fetching to formatting
   - Processes issues directly from archive.org
   - Produces HSA-ready output in the final directory structure

2. **Local Issue Processor** (`scripts/process_local_issue.py`):
   - Processes locally stored OCR files without needing to fetch
   - Shares most logic with the universal pipeline
   - Useful for processing already downloaded issues

3. **Batch Processor** (`scripts/batch_process_local_issues.py`):
   - Processes multiple local issues efficiently
   - Handles error recovery and reporting
   - Tracks progress and produces summary reports

### Utility Components

1. **Configuration** (`src/utils/config.py`):
   - Manages system-wide configuration
   - Handles environment-specific settings
   - Provides a centralized configuration system

2. **Progress Reporting** (`src/utils/progress.py`):
   - Tracks and displays progress during long-running operations
   - Provides ETA and completion percentage

3. **Logging** (integrated throughout):
   - Comprehensive logging system
   - Error tracking and diagnostics
   - Performance monitoring

## Data Flow

```
┌─────────┐      ┌──────────────┐      ┌─────────────┐
│         │      │              │      │             │
│ Archive │─────▶│ OCR Text     │─────▶│ Cleaned Text│
│   .org  │      │ (raw)        │      │             │
│         │      │              │      │             │
└─────────┘      └──────────────┘      └─────────────┘
                                             │
                                             ▼
┌────────────────┐      ┌──────────────┐     ┌─────────────┐
│                │      │              │     │             │
│ HSA-Ready JSON │◀─────│ Classified   │◀────│ Extracted   │
│ Articles       │      │ Articles     │     │ Articles    │
│                │      │              │     │             │
└────────────────┘      └──────────────┘     └─────────────┘
```

1. **Input**: OCR text from archive.org newspaper issues
2. **Processing**:
   - Text cleaning and normalization
   - Article extraction through headline detection
   - Classification and metadata enrichment
3. **Output**: HSA-ready JSON files in a structured directory hierarchy

## Directory Structure

The StoryDredge project follows this directory structure:

```
StoryDredge/
├── archive/              # Archived scripts and files
├── docs/                 # Documentation
├── logs/                 # Log files
├── output/               # Output directories
│   └── hsa-ready-final/  # Final HSA-ready output
├── reports/              # Processing reports
├── scripts/              # Pipeline scripts
├── src/                  # Core source code
│   ├── cleaner/          # Text cleaning components
│   ├── classifier/       # Article classification
│   ├── fetcher/          # Archive.org fetching
│   ├── formatter/        # HSA format conversion
│   ├── splitter/         # Article extraction
│   └── utils/            # Shared utilities
├── temp_downloads/       # Temporary download cache
└── tests/                # Unit and integration tests
```

## Integration Points

1. **Human Story Atlas (HSA)**:
   - Output formatted specifically for HSA integration
   - JSON structure conforming to HSA requirements

2. **Archive.org**:
   - Integration with archive.org for OCR text retrieval
   - Support for various archive.org identifiers and structures

## Future Extensions

The modular nature of StoryDredge allows for several future extensions:

1. **Additional Publications**:
   - Support for more newspaper publications
   - Customized handling for unique publication formats

2. **Enhanced NLP**:
   - Improved entity extraction
   - Better article classification
   - Sentiment analysis

3. **Performance Optimizations**:
   - Parallel processing of multiple issues
   - Distributed processing capabilities
   - GPU acceleration for NLP tasks 