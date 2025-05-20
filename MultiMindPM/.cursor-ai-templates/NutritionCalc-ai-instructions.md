# NutritionCalc Developer Instructions

You are working on the **NutritionCalc** subproject, which is part of the larger **RecipeForge** system managed by MultiMind.

## Your Role

You are responsible for creating the second component in the recipe generation pipeline that:
1. Takes recipe JSON from IngredientEngine
2. Calculates nutritional information
3. Outputs structured nutrition data

## Important Files to Understand

- `/directives/nutrition.md`: Contains your current tasks and requirements
- `/reports/status.md`: Where you should document your progress

## MultiMind Integration

This project is managed through the MultiMind orchestration system:

- **Directives**: Your tasks are defined in the PM directory and synced to this project
- **Status Reporting**: Update `/reports/status.md` to report progress
- **File Structure**: Don't modify `/directives` files - they're managed by MultiMind

The input to your work comes from `/output/recipe.json` (created by IngredientEngine), and your output (`/output/nutrition.json`) will be consumed by the PageStyler module.

## Process

1. Read `/directives/nutrition.md` for your current tasks
2. Implement the required functionality according to the specifications
3. Update `/reports/status.md` with your progress
4. Focus only on the NutritionCalc component - other teams are handling the other parts 