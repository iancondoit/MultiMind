#!/bin/bash
# Script to run the StoryDredge API client for importing articles to StoryMap

# Default values
INPUT_DIR="output/atlanta-constitution"
API_URL="http://localhost:8081"
API_KEY="test_api_key"
BATCH_SIZE=100
THREADS=4
MAX_ARTICLES=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --input-dir)
      INPUT_DIR="$2"
      shift 2
      ;;
    --api-url)
      API_URL="$2"
      shift 2
      ;;
    --api-key)
      API_KEY="$2"
      shift 2
      ;;
    --batch-size)
      BATCH_SIZE="$2"
      shift 2
      ;;
    --threads)
      THREADS="$2"
      shift 2
      ;;
    --max-articles)
      MAX_ARTICLES="--max-articles $2"
      shift 2
      ;;
    --test)
      # Test mode with only 10 articles
      MAX_ARTICLES="--max-articles 10"
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --input-dir DIR     Directory containing processed articles (default: $INPUT_DIR)"
      echo "  --api-url URL       StoryMap API base URL (default: $API_URL)"
      echo "  --api-key KEY       API key for authentication (default: $API_KEY)"
      echo "  --batch-size SIZE   Number of articles per batch (default: $BATCH_SIZE)"
      echo "  --threads NUM       Number of worker threads (default: $THREADS)"
      echo "  --max-articles NUM  Maximum number of articles to process (for testing)"
      echo "  --test              Test mode with only 10 articles"
      echo "  --help              Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check if the input directory exists
if [ ! -d "$INPUT_DIR" ]; then
  echo "Error: Input directory not found: $INPUT_DIR"
  exit 1
fi

# Check if API client script exists
if [ ! -f "storydredge_api_client.py" ]; then
  echo "Error: API client script not found: storydredge_api_client.py"
  exit 1
fi

# Make sure Python is available
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
  PYTHON_CMD="python"
else
  echo "Error: Python not found. Please install Python 3."
  exit 1
fi

# Run the API client
echo "Starting StoryDredge API client..."
echo "Input directory: $INPUT_DIR"
echo "API URL: $API_URL"
echo "Batch size: $BATCH_SIZE"
echo "Threads: $THREADS"
if [ -n "$MAX_ARTICLES" ]; then
  echo "Max articles: $MAX_ARTICLES"
fi

# Execute the command
COMMAND="$PYTHON_CMD storydredge_api_client.py --input-dir $INPUT_DIR --api-url $API_URL --api-key $API_KEY --batch-size $BATCH_SIZE --threads $THREADS $MAX_ARTICLES"
echo "Running: $COMMAND"
$COMMAND

# Check exit status
STATUS=$?
if [ $STATUS -eq 0 ]; then
  echo "Import completed successfully."
else
  echo "Import failed with status $STATUS."
fi

exit $STATUS 