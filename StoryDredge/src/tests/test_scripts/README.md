# Testing Atlanta Constitution Scripts

This directory contains tests for the scripts used to test the StoryDredge pipeline with the Atlanta Constitution dataset.

## Overview

The Atlanta Constitution testing suite consists of several scripts that test the pipeline's ability to process real newspaper OCR data from archive.org.

### Key Scripts

1. **`test_atlanta_constitution_direct.py`**: Tests downloading OCR files directly from archive.org and processing them through the cleaning and splitting components.

2. **`test_prepare_atlanta_constitution_dataset.py`**: Tests the dataset preparation functionality which creates datasets for batch processing.

3. **`test_run_atlanta_constitution_test.py`**: Tests the driver script that runs the complete test workflow.

## Running the Tests

### Unit Tests

To run the unit tests for the scripts:

```bash
# Run all script tests
PYTHONPATH=. pytest tests/test_scripts/

# Run tests for a specific script
PYTHONPATH=. pytest tests/test_scripts/test_atlanta_constitution_direct.py

# Run with verbose output
PYTHONPATH=. pytest tests/test_scripts/ -v
```

### Verification Script

For a quick verification that all Atlanta Constitution testing components are working correctly:

```bash
PYTHONPATH=. python scripts/verify_atlanta_constitution_testing.py
```

This script checks:
- File existence
- Directory structure
- Curl functionality
- Module imports

### Direct Testing Script

To test the pipeline directly with Atlanta Constitution data:

```bash
PYTHONPATH=. python scripts/test_atlanta_constitution_direct.py
```

This will:
1. Download sample Atlanta Constitution issues
2. Clean the OCR text
3. Split the text into articles
4. Save the results for inspection

## Extending the Tests

### Adding New Test Issues

To test with different issues:

1. Edit `TEST_ISSUES` in `scripts/test_atlanta_constitution_direct.py`:

```python
TEST_ISSUES = [
    "per_atlanta-constitution_1922-01-01_54_203",
    "per_atlanta-constitution_1922-01-02_54_204",
    # Add new issue IDs here
]
```

2. Alternatively, use the preparation script to generate a list of issues:

```bash
python scripts/prepare_atlanta_constitution_dataset.py --start-date 1930-01-01 --end-date 1930-01-31 --sample-size 5
```

### Adding New Test Cases

When adding new test cases, follow these principles:

1. **Isolation**: Each test should focus on testing one specific aspect
2. **Mocking**: Use pytest fixtures to mock external dependencies
3. **Documentation**: Document the purpose of each test

Example:

```python
def test_new_functionality(self, mock_dependencies):
    """
    Test description here.
    """
    # Arrange
    # Act
    # Assert
```

## Maintaining the Tests

### Updating Mock Responses

When the API responses or file formats change, update the mock responses in the test fixtures:

```python
@pytest.fixture
def mock_response():
    """Update mock response data when necessary."""
    mock_data = {
        # Update response format here
    }
    return mock_data
```

### Troubleshooting

If tests fail:

1. Check if archive.org API responses have changed
2. Verify the OCR file format hasn't changed
3. Ensure dependencies are correctly installed
4. Review pipeline component changes that might affect test expectations

## Continuous Integration

These tests are designed to work in CI environments. When adding to CI workflows:

1. Include environment setup:
   ```yaml
   - name: Install dependencies
     run: pip install -r requirements.txt
   ```

2. Run verification first:
   ```yaml
   - name: Verify Atlanta Constitution testing
     run: python scripts/verify_atlanta_constitution_testing.py
   ```

3. Run the actual tests:
   ```yaml
   - name: Run Atlanta Constitution tests
     run: python -m pytest tests/test_scripts/
   ``` 