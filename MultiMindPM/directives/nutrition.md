# NutritionCalc Directives

Version: 0.1.0

## Current Tasks

1. Develop a nutrition calculator that:
   - Takes a recipe JSON file as input from `/output/recipe.json`
   - Calculates nutritional information based on ingredients
   - Generates a nutrition summary in JSON format
   - Outputs the result to `/output/nutrition.json`

## Expected Input

The input will be a recipe JSON file as produced by the IngredientEngine, with the structure as specified in that project's directive.

## JSON Output Format

The output should be a valid JSON file with the following structure:

```json
{
  "recipeTitle": "Recipe name",
  "servingSize": "1 serving",
  "servings": 4,
  "nutritionPerServing": {
    "calories": 350,
    "fat": {
      "total": 12,
      "unit": "g",
      "saturated": 2,
      "unsaturated": 10
    },
    "carbohydrates": {
      "total": 45,
      "unit": "g",
      "fiber": 5,
      "sugar": 8
    },
    "protein": {
      "total": 15,
      "unit": "g"
    },
    "vitamins": [
      {
        "name": "Vitamin A",
        "amount": 80,
        "unit": "mcg",
        "percentDailyValue": 10
      }
    ],
    "minerals": [
      {
        "name": "Iron",
        "amount": 2.5,
        "unit": "mg",
        "percentDailyValue": 15
      }
    ]
  },
  "allergens": ["nuts", "soy"],
  "dietaryNotes": "This recipe is vegan and gluten-free"
}
```

## Implementation Guidelines

- Focus on accurate nutrition calculation based on USDA or similar nutrition database
- Implement reasonable estimates for ingredients without exact measurements
- Create unit tests for the calculation logic
- Document assumptions and data sources used
- Provide warnings when nutrition information might be imprecise

## Dependencies

This module depends on the IngredientEngine module for its input and is required by the PageStyler module, which expects the nutrition JSON as described above.

## Completion Reporting - IMPORTANT

Phase 1 is considered complete when you have:
- Developed a functioning nutrition calculator
- Successfully processed recipe JSON input
- Generated accurate nutritional information output
- Implemented all features described in the Current Tasks section

When you have completed Phase 1, follow these exact steps:

1. Update your status report:
   ```
   cd NutritionCalc
   nano reports/status.md  # Update with your accomplishments
   ```

2. Create the completion marker file:
   ```
   mkdir -p ../output/completions
   nano ../output/completions/NutritionCalc-Phase1-complete.md
   ```
   
   Use this template for the completion marker:
   ```markdown
   # Project Completion: NutritionCalc - Phase1
   
   Version: 0.1.0
   Completed: YYYY-MM-DD  # Use today's date
   Project: NutritionCalc
   Phase: Phase1
   
   ## Completed Directives
   
   * Developed nutrition calculator that consumes recipe JSON input
   * Calculated nutritional information based on ingredients
   * Generated nutrition summary in JSON format
   * Created output file at /output/nutrition.json
   * [Add any other specific accomplishments]
   
   ## Notes
   
   [Add any implementation notes, challenges overcome, or design decisions]
   
   ## Next Phase
   
   Ready to enhance the nutrition database and implement more sophisticated ingredient matching algorithms.
   ```

3. Run the completion command:
   ```bash
   cd ..  # Return to project root
   ./multimind.py complete NutritionCalc Phase1
   ```
   
This completion reporting is a critical part of the MultiMind workflow and must be performed when the phase is complete. 