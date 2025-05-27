# Article Classification in StoryDredge

This document outlines how to use the StoryDredge classification system to categorize newspaper articles.

## Classification Methods

StoryDredge supports two classification methods:

1. **Rule-based Classification** (Default, Fast): Uses keyword matching and NER to quickly classify articles without LLM
2. **LLM-based Classification** (Optional): Uses local LLMs through Ollama for more accurate but slower classification

## Prerequisites

- Python 3.10+
- For LLM classification only:
  - Ollama installed and running
  - Llama2 model pulled in Ollama

## Running Classification

### Method 1: Using the Shell Script

The shell script can run classification for multiple issues:

```bash
# Run classification for all issues in direct_test_results.json
./scripts/run_classification.sh

# Specify a different issues file
./scripts/run_classification.sh --issues-file path/to/issues.json

# Process a single issue
./scripts/run_classification.sh --issue per_atlanta-constitution_1922-01-01_54_203

# Specify output directory
./scripts/run_classification.sh --output-dir custom_output

# Use LLM-based classification (slower but more accurate)
./scripts/run_classification.sh --use-llm
```

### Method 2: Running the Python Script Directly

You can also run the Python script directly:

```bash
# Run classification for all issues in a file
python scripts/run_classification.py --issues-file direct_test_results.json

# Process a single issue
python scripts/run_classification.py --issue per_atlanta-constitution_1922-01-01_54_203

# Specify output directory
python scripts/run_classification.py --issues-file direct_test_results.json --output-dir custom_output

# Use LLM-based classification
python scripts/run_classification.py --issues-file direct_test_results.json --use-llm
```

## Classification Methods Comparison

### Rule-based Classification (Default)

The rule-based classifier is the default and preferred method for most use cases:

- **Speed**: Processes hundreds of articles in less than a second
- **Entity Extraction**: Identifies people, organizations, and locations 
- **Accuracy**: Good for standard newspaper articles
- **Dependencies**: No external dependencies required

### LLM-based Classification

For cases where more nuanced classification is needed:

- **Speed**: Slower (several minutes for hundreds of articles)
- **Entity Extraction**: More accurate entity extraction
- **Accuracy**: Better for edge cases and ambiguous content
- **Dependencies**: Requires Ollama and a LLM model

## How Classification Works

### Rule-based Classification

1. The classifier analyzes the text using keyword matching for categories
2. Named Entity Recognition (NER) extracts people, organizations, and locations
3. Results are determined by scoring different category matches
4. No external API calls or LLM dependencies

### LLM-based Classification

1. The classifier loads articles that have been split from newspaper issues
2. Each article is analyzed using a local LLM (Llama2) with a carefully crafted prompt
3. The LLM outputs a classification category and extracted metadata
4. Results are saved in the classified/ directory for each issue

## Troubleshooting

### Common Issues

- **Missing Ollama** (only for LLM classification): Ensure Ollama is installed and running with `ollama serve`
- **Model Not Found** (only for LLM classification): If the Llama2 model is missing, pull it with `ollama pull llama2`
- **Articles Not Found**: Ensure the issue has been properly processed through the splitting step

### Logs

Classification logs are stored in the `logs/classification.log` file.

## Output Format

Each classified article is saved as a JSON file with the following structure:

```json
{
  "title": "Article Title",
  "raw_text": "Original article text...",
  "classification": {
    "category": "News",
    "confidence": 0.95
  },
  "metadata": {
    "topic": "City Budget Approval",
    "people": ["Robert Johnson"],
    "organizations": ["City Council"],
    "locations": ["San Antonio"]
  }
}
```

## Integration with HSA Output

The entity data extracted during classification (people, organizations, locations) is automatically 
added to the tags field in the HSA-ready output files. This enables better searchability and discovery
of articles based on the entities mentioned within them. 