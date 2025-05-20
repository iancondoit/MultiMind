# PageStyler Developer Instructions

You are working on the **PageStyler** subproject, which is part of the larger **RecipeForge** system managed by MultiMind.

## Your Role

You are responsible for creating the final component in the recipe generation pipeline that:
1. Takes recipe JSON from IngredientEngine
2. Takes nutrition JSON from NutritionCalc
3. Generates beautifully formatted recipe cards

## Important Files to Understand

- `/directives/page.md`: Contains your current tasks and requirements
- `/reports/status.md`: Where you should document your progress

## MultiMind Integration

This project is managed through the MultiMind orchestration system:

- **Directives**: Your tasks are defined in the PM directory and synced to this project
- **Status Reporting**: Update `/reports/status.md` to report progress
- **File Structure**: Don't modify `/directives` files - they're managed by MultiMind

The inputs to your work come from `/output/recipe.json` (created by IngredientEngine) and `/output/nutrition.json` (created by NutritionCalc). Your output is `/output/recipe_card.md`, the final product of the RecipeForge pipeline.

## Process

1. Read `/directives/page.md` for your current tasks
2. Implement the required functionality according to the specifications
3. Update `/reports/status.md` with your progress
4. Focus only on the PageStyler component - other teams are handling the other parts 