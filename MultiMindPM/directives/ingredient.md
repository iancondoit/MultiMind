# IngredientEngine Directives

Version: 0.1.0

## Current Tasks

1. Implement a basic prompt-to-recipe converter that:
   - Accepts a text prompt from the user (e.g., "a vegan curry with mango and spice")
   - Parses the prompt to identify key ingredients and cooking style
   - Generates a structured recipe in JSON format
   - Outputs the result to `/output/recipe.json`

## JSON Output Format

The output should be a valid JSON file with the following structure:

```json
{
  "title": "Recipe name",
  "description": "Brief description",
  "cuisine": "Type of cuisine",
  "dietaryInfo": ["vegan", "gluten-free", etc],
  "prepTime": "30 minutes",
  "cookTime": "45 minutes",
  "servings": 4,
  "ingredients": [
    {
      "name": "Ingredient name",
      "amount": "1",
      "unit": "cup",
      "notes": "optional preparation notes"
    }
  ],
  "steps": [
    "Step 1 description",
    "Step 2 description"
  ],
  "notes": "Any additional recipe notes"
}
```

## Implementation Guidelines

- Focus on recipe structure over sophisticated content generation
- Ensure all JSON output is properly validated
- Create a simple folder structure with clear separation of concerns
- Add unit tests for the core functionality
- Document any assumptions made during implementation

## Dependencies

This module has no upstream dependencies but is required by the NutritionCalc module, which expects the JSON output as described above.

## Completion Reporting - IMPORTANT

Phase 1 is considered complete when you have:
- Implemented a basic prompt-to-recipe converter
- Successfully generated structured recipe JSON
- Implemented all features described in the Current Tasks section

When you have completed Phase 1, follow these exact steps:

1. Update your status report:
   ```
   cd IngredientEngine
   nano reports/status.md  # Update with your accomplishments
   ```

2. Create the completion marker file:
   ```
   mkdir -p ../output/completions
   nano ../output/completions/IngredientEngine-Phase1-complete.md
   ```
   
   Use this template for the completion marker:
   ```markdown
   # Project Completion: IngredientEngine - Phase1
   
   Version: 0.1.0
   Completed: YYYY-MM-DD  # Use today's date
   Project: IngredientEngine
   Phase: Phase1
   
   ## Completed Directives
   
   * Implemented prompt-to-recipe converter
   * Created JSON schema for recipe output
   * Added basic validation for ingredient format
   * Generated structured recipe from text input
   * [Add any other specific accomplishments]
   
   ## Notes
   
   [Add any implementation notes, challenges overcome, or design decisions]
   
   ## Next Phase
   
   Ready to begin work on enhanced parsing features for complex recipes.
   ```

3. Run the completion command:
   ```bash
   cd ..  # Return to project root
   ./multimind.py complete IngredientEngine Phase1
   ```
   
This completion reporting is a critical part of the MultiMind workflow and must be performed when the phase is complete. 