#!/bin/bash
# Script to test the local import of a few articles

echo "Testing article import with sample data"

# Make sure we're in the virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
  echo "Activating virtual environment..."
  source .venv/bin/activate
fi

# Create test data
echo "Creating test data..."
python test_integration.py --input-dir output/atlanta-constitution --sample-size 10 --output-dir test_data

# Test import
echo "Running API client with test data..."
python storydredge_api_client.py \
  --input-dir test_data \
  --api-url http://localhost:8081 \
  --api-key test_api_key \
  --batch-size 5 \
  --threads 2 \
  --max-articles 10

echo "Test completed!" 