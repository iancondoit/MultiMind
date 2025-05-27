#!/usr/bin/env python3
"""
Test script for StoryDredge to StoryMap integration

This script tests the API client with a small sample of articles.
"""

import os
import sys
import json
import argparse
import random
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_integration")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test StoryDredge API Integration")
    parser.add_argument("--input-dir", type=str, default="output/atlanta-constitution",
                       help="Directory containing processed articles")
    parser.add_argument("--sample-size", type=int, default=10,
                       help="Number of articles to sample for testing")
    parser.add_argument("--output-dir", type=str, default="test_data",
                       help="Directory to save test data")
    parser.add_argument("--api-url", type=str, default="http://localhost:8081",
                       help="StoryMap API base URL for testing")
    return parser.parse_args()

def find_random_articles(input_dir, sample_size=10):
    """Find random article files for testing"""
    input_path = Path(input_dir)
    all_json_files = []
    
    # Find all JSON files
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith('.json'):
                all_json_files.append(os.path.join(root, file))
    
    # Sample random files
    if len(all_json_files) <= sample_size:
        return all_json_files
    
    return random.sample(all_json_files, sample_size)

def transform_article(file_path):
    """Transform StoryDredge article format to StoryMap API format"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        # Extract the filename without extension as fallback ID
        filename = os.path.basename(file_path)
        article_id = filename.split('.')[0]
        
        # Transform to StoryMap API format
        transformed = {
            "id": article_data.get('source_issue', '') + '_' + article_id,
            "title": article_data.get('headline', ''),
            "content": article_data.get('body', ''),
            "source": article_data.get('publication', 'Atlanta Constitution'),
            "date": article_data.get('timestamp', '').split('T')[0],
            "category": article_data.get('section', 'news'),
            "tags": article_data.get('tags', []),
            "metadata": {
                "word_count": len(article_data.get('body', '').split()) if article_data.get('body') else 0,
                "source_url": article_data.get('source_url', ''),
                "source_issue": article_data.get('source_issue', '')
            }
        }
        
        return transformed
    
    except Exception as e:
        logger.error(f"Error transforming {file_path}: {e}")
        return None

def create_test_batch(articles, output_dir):
    """Create a test batch JSON file"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    batch_file = output_path / "test_batch.json"
    
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump({"articles": articles}, f, indent=2)
    
    logger.info(f"Created test batch file with {len(articles)} articles: {batch_file}")
    return batch_file

def create_test_curl_commands(batch_file, output_dir, api_url):
    """Create test curl commands for the API"""
    output_path = Path(output_dir)
    curl_file = output_path / "test_curl_commands.sh"
    
    with open(curl_file, 'w', encoding='utf-8') as f:
        f.write("#!/bin/bash\n\n")
        f.write("# Test commands for StoryDredge API\n\n")
        
        # Health check
        f.write("# Health check\n")
        f.write(f"curl {api_url}/health\n\n")
        
        # Submit batch
        f.write("# Submit batch\n")
        f.write(f"curl -X POST \\\n")
        f.write(f"  -H \"Content-Type: application/json\" \\\n")
        f.write(f"  -H \"X-API-Key: test_api_key\" \\\n")
        f.write(f"  -d @{batch_file} \\\n")
        f.write(f"  {api_url}/api/articles/batch\n\n")
        
        # Submit single article
        f.write("# Submit single article\n")
        f.write(f"curl -X POST \\\n")
        f.write(f"  -H \"Content-Type: application/json\" \\\n")
        f.write(f"  -H \"X-API-Key: test_api_key\" \\\n")
        f.write(f"  -d @{output_path}/test_article.json \\\n")
        f.write(f"  {api_url}/api/articles\n\n")
        
        # Check status (replace with actual IDs after running)
        f.write("# Check article status\n")
        f.write(f"curl -H \"X-API-Key: test_api_key\" {api_url}/api/articles/status/ARTICLE_ID_HERE\n\n")
        
        f.write("# Check batch status\n")
        f.write(f"curl -H \"X-API-Key: test_api_key\" {api_url}/api/batch/status/BATCH_ID_HERE\n")
    
    # Make executable
    os.chmod(curl_file, 0o755)
    
    logger.info(f"Created test curl commands file: {curl_file}")
    return curl_file

def create_test_article_file(article, output_dir):
    """Create a test article JSON file"""
    output_path = Path(output_dir)
    article_file = output_path / "test_article.json"
    
    with open(article_file, 'w', encoding='utf-8') as f:
        json.dump(article, f, indent=2)
    
    logger.info(f"Created test article file: {article_file}")
    return article_file

def main():
    """Main entry point"""
    args = parse_args()
    
    logger.info(f"Finding {args.sample_size} random articles from {args.input_dir}")
    article_files = find_random_articles(args.input_dir, args.sample_size)
    
    if not article_files:
        logger.error("No article files found. Exiting.")
        return 1
    
    logger.info(f"Found {len(article_files)} article files")
    
    # Transform articles to API format
    transformed_articles = []
    for file_path in article_files:
        transformed = transform_article(file_path)
        if transformed:
            transformed_articles.append(transformed)
    
    if not transformed_articles:
        logger.error("No articles could be transformed. Exiting.")
        return 1
    
    # Create test files
    batch_file = create_test_batch(transformed_articles, args.output_dir)
    
    # Create a sample article file
    article_file = create_test_article_file(transformed_articles[0], args.output_dir)
    
    # Create curl commands
    curl_file = create_test_curl_commands(batch_file, args.output_dir, args.api_url)
    
    logger.info(f"Test data created successfully in {args.output_dir}")
    logger.info(f"To run the test commands: bash {curl_file}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 