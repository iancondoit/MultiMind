# ProjectTwo Directives

Version: 0.2.0

## Current Tasks

1. Develop a data processing system that:
   - Takes input JSON file from `/output/data.json`
   - Performs analysis and transformation on the data
   - Generates processed output in JSON format
   - Outputs the result to `/output/processed.json`

## Expected Input

The input will be a JSON file as produced by the ProjectOne, with the structure as specified in that project's directive.

## JSON Output Format

The output should be a valid JSON file with the following structure:

```json
{
  "id": "unique-identifier",
  "originalTitle": "Original data title",
  "processingTimestamp": "ISO-formatted timestamp",
  "analysisResults": {
    "summary": "Brief summary of analysis",
    "metrics": {
      "metric1": 95.7,
      "metric2": 42.1
    },
    "categories": [
      {
        "name": "Category name",
        "confidence": 0.95,
        "attributes": ["attr1", "attr2"]
      }
    ],
    "insights": [
      "Insight 1 description",
      "Insight 2 description"
    ]
  },
  "transformedData": {
    "field1": "transformed value1",
    "field2": "transformed value2"
  },
  "metadata": {
    "processingVersion": "1.0",
    "processingMode": "standard"
  }
}
```

## Implementation Guidelines

- Focus on accurate data processing and transformation
- Implement appropriate error handling for malformed input
- Create unit tests for the calculation logic
- Document assumptions and processing methods
- Provide warnings when processing might be incomplete

## Dependencies

This module depends on the ProjectOne module for its input and is required by the ProjectThree module, which expects the processed JSON as described above. 