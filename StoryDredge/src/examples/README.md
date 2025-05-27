# StoryDredge Examples

This directory contains example scripts demonstrating various features of the StoryDredge pipeline.

## Progress Demo

The `progress_demo.py` script demonstrates the progress reporting capabilities of StoryDredge, showing:

- Real-time progress updates in the terminal
- Progress bars with percentage completion
- Animated spinners for active tasks
- Metrics display for component-specific information
- ETA estimation for time remaining
- Multi-stage pipeline tracking

To run the demo:

```bash
# From the project root directory
./examples/progress_demo.py

# Or with Python directly
python examples/progress_demo.py
```

The demo simulates a complete pipeline run with all major components:
1. Fetching data from archive.org
2. Cleaning OCR text
3. Splitting text into articles
4. Classifying articles with LLM
5. Formatting articles for HSA

Watch the terminal for real-time progress updates, including metrics and ETA estimates. 