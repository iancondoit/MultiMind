# ProjectOne Directives

Version: 0.2.0

## Current Tasks

1. Implement the core functionality that:
   - Accepts user input data
   - Processes it according to business requirements
   - Generates structured data in JSON format
   - Outputs the result to `/output/data.json`

## JSON Output Format

The output should be a valid JSON file with the following structure:

```json
{
  "id": "unique-identifier",
  "title": "Data title",
  "description": "Brief description",
  "category": "Type of data",
  "metadata": {
    "createdAt": "timestamp",
    "source": "origin of data",
    "version": "1.0"
  },
  "content": {
    "field1": "value1",
    "field2": "value2",
    "nestedField": {
      "subfield1": "subvalue1"
    }
  },
  "tags": ["tag1", "tag2"]
}
```

## Implementation Guidelines

- Focus on data structure and validation
- Ensure all JSON output is properly formatted and validated
- Create a simple folder structure with clear separation of concerns
- Add unit tests for the core functionality
- Document any assumptions made during implementation

## Dependencies

This module has no upstream dependencies but is required by the ProjectTwo module, which expects the JSON output as described above. 