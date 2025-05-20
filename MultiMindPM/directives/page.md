# PageStyler Directives

Version: 0.1.0

## Current Tasks

1. Create a page styling system that:
   - Takes recipe data from `/output/recipe.json`
   - Takes nutrition data from `/output/nutrition.json`
   - Generates a beautifully formatted recipe card
   - Outputs the result to `/output/recipe_card.md`

## Expected Input

The input will be two JSON files:
1. Recipe JSON from IngredientEngine
2. Nutrition JSON from NutritionCalc

## Output Format

The initial output should be a markdown file with the following sections:

```markdown
# [Recipe Title]

![Recipe Image Placeholder]

## Description
[Recipe description from input]

## Ingredients
- [Ingredient 1]
- [Ingredient 2]
...

## Instructions
1. [Step 1]
2. [Step 2]
...

## Nutrition Information
- **Calories:** [calories] per serving
- **Protein:** [protein]g
- **Carbs:** [carbs]g
- **Fat:** [fat]g

## Dietary Information
[Vegan, Gluten-Free, etc.]

## Notes
[Any additional notes]
```

## Implementation Guidelines

- Focus on clean, readable formatting for the recipe card
- Include all essential information from both input files
- Ensure proper handling of lists and sections
- Create a visually appealing layout
- Consider future extension to HTML and PDF formats

## Dependencies

This module depends on both the IngredientEngine and NutritionCalc modules for its input data.

## Completion Reporting - IMPORTANT

Phase 1 is considered complete when you have:
- Created a functioning page styling system
- Successfully generated formatted recipe cards from input data
- Implemented all features described in the Current Tasks section

When you have completed Phase 1, follow these exact steps:

1. Update your status report:
   ```
   cd PageStyler
   nano reports/status.md  # Update with your accomplishments
   ```

2. Create the completion marker file:
   ```
   mkdir -p ../output/completions
   nano ../output/completions/PageStyler-Phase1-complete.md
   ```
   
   Use this template for the completion marker:
   ```markdown
   # Project Completion: PageStyler - Phase1
   
   Version: 0.1.0
   Completed: YYYY-MM-DD  # Use today's date
   Project: PageStyler
   Phase: Phase1
   
   ## Completed Directives
   
   * Created page styling system that generates recipe cards
   * Implemented formatting for all required sections
   * Successfully processed input from both JSON sources
   * Generated well-formatted markdown output
   * [Add any other specific accomplishments]
   
   ## Notes
   
   [Add any implementation notes, challenges overcome, or design decisions]
   
   ## Next Phase
   
   Ready to implement additional output formats (HTML, PDF) and enhanced styling options.
   ```

3. Run the completion command:
   ```bash
   cd ..  # Return to project root
   ./multimind.py complete PageStyler Phase1
   ```
   
This completion reporting is a critical part of the MultiMind workflow and must be performed when the phase is complete. 