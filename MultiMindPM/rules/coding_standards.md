# RecipeForge Coding Standards

Version: 0.1.0

## Overview

This document defines the coding standards that all RecipeForge components must follow. Adhering to these standards ensures consistency, maintainability, and effective collaboration across projects.

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

### JavaScript (for PageStyler)

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
Recipe generator module for IngredientEngine.

This module parses user prompts and generates structured recipe data.
"""

import json
import logging
from typing import Dict, List, Optional

# Constants
DEFAULT_SERVINGS = 4
VALID_CUISINES = ["italian", "mexican", "asian", "american", "french"]

class RecipeGenerator:
    """
    Generates recipe data from user prompts.
    """
    
    def __init__(self, prompt: str):
        """
        Initialize the recipe generator.
        
        Args:
            prompt: User input describing desired recipe
        """
        self.prompt = prompt
        self.ingredients = []
        self.steps = []
        
    def parse_prompt(self) -> bool:
        """
        Parse the user prompt to extract recipe information.
        
        Returns:
            bool: True if parsing was successful
        """
        try:
            # Parsing logic would go here
            return True
        except Exception as e:
            logging.error(f"Failed to parse prompt: {e}")
            return False
            
    def generate_recipe(self) -> Dict:
        """
        Generate a complete recipe in JSON format.
        
        Returns:
            Dict: Recipe data structure
        """
        recipe = {
            "title": "Sample Recipe",
            "description": "A sample recipe",
            "cuisine": "italian",
            "ingredients": self.ingredients,
            "steps": self.steps
        }
        
        return recipe
        
    def save_recipe(self, output_path: str = "/output/recipe.json") -> None:
        """
        Save the recipe to a JSON file.
        
        Args:
            output_path: Path to the output file
        """
        recipe = self.generate_recipe()
        
        try:
            with open(output_path, 'w') as f:
                json.dump(recipe, f, indent=2)
            logging.info(f"Recipe saved to {output_path}")
        except IOError as e:
            logging.error(f"Failed to save recipe: {e}")
```

### JSON Example

```json
{
  "title": "Vegan Mango Curry",
  "description": "A delicious vegan curry with sweet mango and aromatic spices",
  "cuisine": "indian",
  "dietaryInfo": ["vegan", "gluten-free"],
  "prepTime": "15 minutes",
  "cookTime": "30 minutes",
  "servings": 4,
  "ingredients": [
    {
      "name": "ripe mango",
      "amount": "2",
      "unit": "whole",
      "notes": "peeled and cubed"
    },
    {
      "name": "coconut milk",
      "amount": "1",
      "unit": "can",
      "notes": "400ml"
    }
  ],
  "steps": [
    "Heat oil in a large pan over medium heat",
    "Add spices and toast for 30 seconds until fragrant"
  ]
}
``` 