# MultiMind Coding Standards

Version: 0.1.0

## Overview

This document defines the coding standards that all MultiMind components must follow. Adhering to these standards ensures consistency, maintainability, and effective collaboration across projects.

## File Organization

### Directory Structure

Each project should maintain the following directory structure:

```
/ProjectName
  ├── README.md              # Project overview
  ├── roadmap.md             # Project roadmap (synced from PM)
  ├── .cursor-ai-instructions.md # Agent instructions
  ├── directives/            # Task directives from PM
  ├── reports/               # Status reports
  ├── src/                   # Source code
  │     ├── main.py          # Entry point
  │     ├── models/          # Data models
  │     ├── utils/           # Utility functions
  │     └── tests/           # Unit tests
  └── output/                # Output files (shared)
```

### File Naming

- Use snake_case for Python files and directories
- Use PascalCase for class names
- Use snake_case for functions and variables
- Use UPPER_CASE for constants

## Code Style

### Python

- Follow PEP 8 guidelines
- Use 4 spaces for indentation (no tabs)
- Maximum line length: 88 characters
- Use docstrings for all functions and classes
- Import organization:
  1. Standard library imports
  2. Third-party imports
  3. Local application imports

### JavaScript

- Use ES6+ syntax
- Use 2 spaces for indentation
- Use semicolons after statements
- Use camelCase for variables and functions
- Use PascalCase for classes and React components

### JSON

- Use consistent indentation (2 spaces)
- Use camelCase for property names
- Ensure all JSON is validated before output

## Documentation

### Code Comments

- Add comments for complex logic
- Explain "why" not "what" (the code shows what it does)
- Keep comments up-to-date with code changes

### Function Documentation

Each function should have a docstring that includes:

```python
def example_function(param1, param2):
    """
    Brief description of function purpose.
    
    Args:
        param1: Description of parameter
        param2: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When and why this happens
    """
    # Function implementation
```

## Testing

- Write unit tests for all functions
- Aim for at least 80% code coverage
- Place tests in a `tests` directory
- Name test files to match the module they test (`test_module.py`)

## Version Control

- Keep project version in all key files
- Update version when making significant changes
- Format: `Major.Minor.Patch` (e.g., `0.1.0`)

## Error Handling

- Use try/except blocks for potential errors
- Log errors with appropriate context
- Provide meaningful error messages
- Handle edge cases explicitly

## Cross-Project Integration

- Follow the handoff protocol for API changes
- Ensure JSON schemas are fully documented
- Version all API contracts
- Validate inputs and outputs at boundaries

## Example Code

### Python Example

```python
#!/usr/bin/env python3
"""
Data processor module for ProjectOne.

This module parses user inputs and generates structured data.
"""

import json
import logging
from typing import Dict, List, Optional

# Constants
DEFAULT_ITEMS = 4
VALID_CATEGORIES = ["category1", "category2", "category3", "category4", "category5"]

class DataProcessor:
    """
    Generates structured data from user inputs.
    """
    
    def __init__(self, input_data: str):
        """
        Initialize the data processor.
        
        Args:
            input_data: User input describing desired data
        """
        self.input_data = input_data
        self.items = []
        self.attributes = []
        
    def parse_input(self) -> bool:
        """
        Parse the user input to extract data information.
        
        Returns:
            bool: True if parsing was successful
        """
        try:
            # Parsing logic would go here
            return True
        except Exception as e:
            logging.error(f"Failed to parse input: {e}")
            return False
            
    def generate_data(self) -> Dict:
        """
        Generate a complete data structure in JSON format.
        
        Returns:
            Dict: Structured data
        """
        data = {
            "id": "sample-data-id",
            "title": "Sample Data",
            "description": "A sample data structure",
            "category": "category1",
            "items": self.items,
            "attributes": self.attributes
        }
        
        return data
        
    def save_data(self, output_path: str = "/output/data.json") -> None:
        """
        Save the data to a JSON file.
        
        Args:
            output_path: Path to the output file
        """
        data = self.generate_data()
        
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Data saved to {output_path}")
        except IOError as e:
            logging.error(f"Failed to save data: {e}")
```

### JSON Example

```json
{
  "id": "data-123456",
  "title": "Sample Structured Data",
  "description": "A comprehensive data structure with metadata",
  "category": "category2",
  "metadata": ["type1", "type2"],
  "createdAt": "2023-06-15T10:30:00Z",
  "updatedAt": "2023-06-15T14:45:00Z",
  "items": [
    {
      "id": "item-001",
      "name": "First item",
      "value": 42,
      "attributes": ["attribute1", "attribute2"]
    },
    {
      "id": "item-002",
      "name": "Second item",
      "value": 73,
      "attributes": ["attribute2", "attribute3"]
    }
  ],
  "stats": [
    "Processed in 0.45 seconds",
    "Contains 2 unique items"
  ]
}
``` 