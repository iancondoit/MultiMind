# Contributing to StoryDredge

Thank you for your interest in contributing to StoryDredge! This document provides guidelines and instructions for contributing to the project.

## Project Architecture

StoryDredge uses a modular architecture with clearly defined components:

1. **Fetcher**: Downloads and caches newspaper OCR from archive.org
2. **Cleaner**: Normalizes and cleans OCR text
3. **Splitter**: Identifies and extracts individual articles
4. **Classifier**: Uses local Llama model to classify and extract metadata
5. **Formatter**: Converts to HSA-ready output format

Each component is designed to be testable and maintainable, with clear interfaces between modules.

## Development Workflow

### Setup Development Environment

#### Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/storydredge.git
cd storydredge

# Run the automated setup script
./dev-setup.sh
```

#### Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/storydredge.git
cd storydredge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (including dev dependencies)
pip install -r requirements.txt
```

### Test-Driven Development

StoryDredge follows test-driven development principles. Always write tests before implementing features:

```bash
# Run tests
./run_tests.py

# Run tests with coverage
./run_tests.py --cov=src
```

### Code Style and Quality

We use the following tools to maintain code quality:

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Type checking
mypy src

# Linting
pylint src
```

## Project Structure Guidelines

### Where to Add New Code

- **New features**: Add to the appropriate module in `src/`
- **Bug fixes**: Fix in the relevant module and add tests
- **Documentation**: Update README.md, docstrings, or add to the docs directory

### ⚠️ IMPORTANT: Legacy Code and Archive Directory ⚠️

The `archive/` directory contains the legacy codebase that has been preserved for reference purposes only.

**DO NOT**:
- Modify or extend code in the `archive/` directory
- Import or use code from the `archive/` directory in new development
- Copy-paste code from the archive without thorough review and refactoring

**DO**:
- Reference the archived code only for understanding historical context
- Implement new features using the modular architecture in `src/`
- Migrate useful functionality from legacy code into proper modules with tests

## Pull Request Process

1. Create a feature branch from `main`
2. Implement your changes with appropriate tests
3. Ensure all tests pass
4. Update documentation as needed
5. Submit a pull request with a clear description of the changes

## Output Format

All processed articles must conform to the Human Story Atlas (HSA) format:

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

Output files must be organized by date: `output/hsa-ready/YYYY/MM/DD/filename.json`

## Getting Help

If you have questions or need help, please:
1. Check the documentation in the README.md
2. Look at the tests for examples of how components should work
3. Reach out to the maintainers 