# Inter-Project Handoff Protocol

Version: 0.1.0

## Overview

This document defines the standardized protocol for handoffs between project components in the RecipeForge system. Handoffs allow one component to request changes or clarifications from another component.

## Handoff File Structure

Handoffs are stored as Markdown files in the following locations:

1. **PM Handoff Directory**: `/MultiMindPM/handoffs/`
   - Contains all active handoffs
   - Named format: `YYYYMMDD-from_to-description.md`
   - Example: `20230615-ingredient_nutrition-schema_update.md`

2. **Output Handoff Directory**: `/output/handoffs/`
   - Used for direct project-to-project handoffs
   - Same naming convention as PM handoffs

## Handoff Document Format

Each handoff document must follow this structure:

```markdown
# Handoff: [Brief Description]

Version: [version]
Status: [PENDING | IN_PROGRESS | RESOLVED | REJECTED]
From: [Source Project]
To: [Target Project]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]

## Request

[Detailed description of the request]

## Context

[Background information explaining why this is needed]

## Implementation Details

[Specific technical details including:
- Files that need to be modified
- Schema changes
- API adjustments
- etc.]

## Response

[To be filled out by the receiving team]

## Resolution

[Final agreed-upon solution]
```

## Handoff Process

1. **Creation**
   - Create a handoff document in your project repository
   - Copy it to the PM handoff directory
   - Status should be "PENDING"

2. **Processing**
   - The PM will review the handoff and coordinate with the target project
   - Target project updates the "Response" section
   - Status changes to "IN_PROGRESS"

3. **Resolution**
   - Once completed, document the final solution in "Resolution"
   - Status changes to "RESOLVED" or "REJECTED"
   - PM archives the handoff document

## Example Handoff

```markdown
# Handoff: Add Allergen Detection to Recipe JSON

Version: 0.1.0
Status: PENDING
From: NutritionCalc
To: IngredientEngine
Created: 2023-06-15
Last Updated: 2023-06-15

## Request

IngredientEngine should enhance the recipe JSON to include an "allergens" array field that identifies common allergens in the recipe.

## Context

The nutrition calculator needs to highlight allergens in its output, but identifying them directly from ingredient names is error-prone. It would be more reliable if IngredientEngine identified them during recipe creation.

## Implementation Details

1. Update the recipe JSON schema to include:
   ```json
   {
     "allergens": ["dairy", "nuts", "gluten", "etc"]
   }
   ```
2. Modify the prompt parser to detect allergens
3. Ensure the allergen list is included in all recipe outputs

## Response

[To be filled by IngredientEngine team]

## Resolution

[Final agreement on implementation]
```

## Important Notes

- Always copy the PM on handoffs using the PM handoff directory
- Do not directly modify another project's files without a handoff
- Ensure your status reports mention any pending handoffs
- Use this process for all cross-component feature requests or API changes 