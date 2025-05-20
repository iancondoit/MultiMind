# ProjectThree Directives

Version: 0.2.0

## Current Tasks

1. Create an output generation system that:
   - Takes data from `/output/data.json`
   - Takes processed data from `/output/processed.json`
   - Generates formatted output for presentation
   - Outputs the result to `/output/output.md`

## Expected Input

The input will be two JSON files:
1. Data JSON from ProjectOne
2. Processed data JSON from ProjectTwo

## Output Format

The initial output should be a markdown file with the following sections:

```markdown
# [Data Title]

![Visualization Placeholder]

## Summary
[Summary from processed data]

## Key Metrics
- **Metric 1:** [value1]
- **Metric 2:** [value2]
...

## Insights
1. [Insight 1]
2. [Insight 2]
...

## Categories
- **[Category 1]:** [attributes]
- **[Category 2]:** [attributes]

## Additional Information
[Any other relevant details]

## Metadata
- **Generated:** [timestamp]
- **Source:** [source]
- **Version:** [version]
```

## Implementation Guidelines

- Focus on clean, readable formatting for the output
- Include all essential information from both input files
- Ensure proper handling of lists and sections
- Create a visually appealing layout
- Consider future extension to HTML and PDF formats

## Dependencies

This module depends on both the ProjectOne and ProjectTwo modules for its input data.

## Completion Reporting - IMPORTANT

When you have completed all the tasks in this directive:

1. Update your status report in `/reports/status.md` with details of what you've accomplished
2. Create a completion marker file in `/output/completions/ProjectThree-Phase1-complete.md` following the format in `/rules/completion_reporting.md`
3. Run the following command to notify the Project Manager:
   ```bash
   ./multimind.py complete ProjectThree Phase1
   ```
   
This completion reporting is a critical part of the MultiMind workflow and must be performed when the phase is complete. 