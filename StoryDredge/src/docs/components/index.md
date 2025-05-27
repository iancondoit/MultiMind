# StoryDredge Components

This directory contains detailed documentation for each component in the StoryDredge pipeline.

## Core Components

| Component | Status | Description |
|-----------|--------|-------------|
| [Fetcher](fetcher.md) | ✅ Complete | Downloads and caches newspaper OCR text from archive.org |
| [Cleaner](cleaner.md) | ✅ Complete | Normalizes and corrects OCR text |
| [Splitter](splitter.md) | ✅ Complete | Identifies and extracts individual articles |
| [Classifier](classifier.md) | ✅ Complete | Uses local LLM to classify articles and extract metadata |
| [Formatter](formatter.md) | ✅ Complete | Converts classified articles to HSA-ready JSON format |
| [Performance](performance.md) | ✅ Complete | Optimizes pipeline with benchmarking and parallel processing |

## Status Definitions

- ✅ **Complete**: Component is fully implemented and tested
- 🚧 **In Development**: Component is currently being implemented
- 📅 **Planned**: Component is planned but implementation has not started
- 🔄 **Refactoring**: Component is undergoing significant changes

## Component Dependencies

Each component depends on the successful completion of previous components in the pipeline:

```Fetcher → Cleaner → Splitter → Classifier → Formatter
```

## Component Structure

Each component follows a similar structure:

1. **Main class**: Implements the core functionality
2. **Helper classes**: Support the main class with specialized functionality
3. **Configuration**: Component-specific configuration
4. **Error handling**: Custom exceptions and recovery mechanisms
5. **Tests**: Comprehensive test cases

## Documentation Format

Each component's documentation includes:

- **Overview**: High-level description of the component's purpose
- **Key Features**: List of main capabilities
- **Usage**: Examples of how to use the component
- **Configuration**: Available configuration options
- **Implementation Details**: Technical details about the implementation
- **Dependencies**: External libraries and internal dependencies
- **Error Handling**: How errors are handled
- **Future Enhancements**: Planned improvements 