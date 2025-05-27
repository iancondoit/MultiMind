# Article Classifier Component

The ArticleClassifier component is responsible for classifying newspaper articles into categories and extracting metadata using local large language models (LLMs) through Ollama.

## Features

- Article classification using local LLMs
- Metadata extraction (topic, people, organizations, locations)
- Batch processing of multiple articles
- Configurable models and parameters
- Error recovery and fallback mechanisms
- Progress reporting

## Requirements

- Ollama installed and running (https://ollama.com/)
- At least one LLM model pulled (e.g., `llama2`)

## Installation

1. Install Ollama by following the instructions at https://ollama.com/
2. Pull a model:
   ```bash
   ollama pull llama2
   ```
3. Make sure Ollama is running before using the classifier

## Usage

### Basic Usage

```python
from src.classifier.article_classifier import ArticleClassifier

# Create a classifier instance
classifier = ArticleClassifier()

# Classify a single article
article = {
    "title": "LOCAL COUNCIL APPROVES NEW BUDGET",
    "raw_text": "The San Antonio City Council yesterday approved..."
}
result = classifier.classify_article(article)

# Print the classification result
print(f"Category: {result['category']}")
print(f"Confidence: {result['confidence']}")
print(f"Topic: {result['metadata']['topic']}")
print(f"People: {', '.join(result['metadata']['people'])}")
```

### Batch Processing

```python
# Process a batch of articles
articles = [
    {"title": "Article 1", "raw_text": "Content of article 1..."},
    {"title": "Article 2", "raw_text": "Content of article 2..."}
]
results = classifier.classify_batch(articles)
```

### Processing Files

```python
# Process a single article file
result = classifier.classify_file("path/to/article.json")

# Process all articles in a directory
results = classifier.classify_directory("path/to/articles", "path/to/output")
```

## Configuration

The classifier can be configured through the `config/pipeline.yml` file:

```yaml
classifier:
  enabled: true
  debug_mode: false
  timeout_seconds: 900
  model_name: "llama2"
  batch_size: 10
  concurrency: 2
  prompt_template: "article_classification.txt"
  confidence_threshold: 0.6
  fallback_section: "miscellaneous"
```

## Prompt Templates

The classifier uses prompt templates from the `config/prompts` directory. The default template is `article_classification.txt`.

## Error Handling

The classifier includes comprehensive error handling features:

- Retry logic for API failures
- Fallback to simpler prompts if template loading fails
- Default category assignment for unclassifiable articles
- Structured data extraction from malformed responses

## Testing

Run the tests for the classifier:

```bash
python -m pytest tests/test_classifier/test_llama_classifier.py -v
```

Try the example script:

```bash
python examples/test_classifier.py
```

## Output Format

The classifier outputs a dictionary with the following structure:

```json
{
  "title": "Original article title",
  "raw_text": "Original article text",
  "category": "News",
  "confidence": 0.95,
  "metadata": {
    "topic": "City Budget",
    "people": ["Robert Johnson", "Maria Rodriguez"],
    "organizations": ["City Council"],
    "locations": ["San Antonio"]
  }
}
```

## Implementation Details

### Classes

1. **ArticleClassifier**: Main class for classifying articles
2. **OllamaClient**: Client for interacting with the Ollama API
3. **PromptTemplates**: Manager for classification prompt templates

### Key Methods

- `classify_article(article)`: Classify a single article
- `classify_batch(articles)`: Classify multiple articles
- `classify_file(file_path)`: Classify an article from a JSON file
- `classify_directory(input_dir, output_dir)`: Classify all articles in a directory

## Performance Considerations

- Use a more powerful model for better classification accuracy
- Adjust batch size for processing large collections
- Set appropriate concurrency level based on system capabilities
- Consider GPU acceleration if available

## Limitations

- Classification accuracy depends on the quality of the LLM model
- Processing speed is limited by the local LLM performance
- Very short articles may be difficult to classify accurately
- Requires Ollama to be installed and running 