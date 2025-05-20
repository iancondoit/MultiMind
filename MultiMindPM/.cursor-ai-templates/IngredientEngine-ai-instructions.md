# IngredientEngine Developer Instructions

You are working on the **IngredientEngine** subproject, which is part of the larger **RecipeForge** system managed by MultiMind.

## Your Role

You are responsible for creating the first component in the recipe generation pipeline that:
1. Takes user prompts about desired recipes
2. Converts them to structured recipe JSON

## Important Files to Understand

- `/directives/ingredient.md`: Contains your current tasks and requirements
- `/reports/status.md`: Where you should document your progress

## MultiMind Integration

This project is managed through the MultiMind orchestration system:

- **Directives**: Your tasks are defined in the PM directory and synced to this project
- **Status Reporting**: Update `/reports/status.md` to report progress
- **File Structure**: Don't modify `/directives` files - they're managed by MultiMind

The output of your work (`/output/recipe.json`) will be consumed by the NutritionCalc module.

## Process

1. Read `/directives/ingredient.md` for your current tasks
2. Implement the required functionality according to the specifications
3. Update `/reports/status.md` with your progress
4. Focus only on the IngredientEngine component - other teams are handling the other parts 