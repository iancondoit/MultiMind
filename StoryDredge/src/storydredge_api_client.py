#!/usr/bin/env python3
"""
StoryDredge API Client for sending processed articles to StoryMap

This script reads processed newspaper articles from the output directory
and sends them to the StoryMap API for storage in PostgreSQL.
"""

import os
import sys
import json
import time
import argparse
import logging
import requests
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("api_client.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("storydredge_api_client")

class StoryDredgeClient:
    def __init__(self, api_url, api_key, batch_size=100, max_retries=3, retry_delay=5):
        self.api_url = api_url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def submit_article(self, article_data):
        """Submit a single article to the API"""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.api_url}/api/articles",
                    headers=self.headers,
                    json=article_data,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to submit article {article_data.get('id', 'unknown')}: {str(e)}")
                    raise
    
    def submit_batch(self, articles):
        """Submit a batch of articles to the API"""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.api_url}/api/articles/batch",
                    headers=self.headers,
                    json={"articles": articles},
                    timeout=120
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Batch attempt {attempt+1} failed: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to submit batch ({len(articles)} articles): {str(e)}")
                    raise
    
    def check_status(self, article_id):
        """Check the processing status of an article"""
        try:
            response = requests.get(
                f"{self.api_url}/api/articles/status/{article_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to check status for article {article_id}: {str(e)}")
            raise

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Send processed articles to StoryMap API")
    parser.add_argument("--input-dir", type=str, default="../output/atlanta-constitution",
                       help="Directory containing processed articles")
    parser.add_argument("--api-url", type=str, default="http://localhost:8081",
                       help="StoryMap API base URL")
    parser.add_argument("--api-key", type=str, required=True,
                       help="API key for authentication")
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Number of articles to send in each batch")
    parser.add_argument("--threads", type=int, default=4,
                       help="Number of threads to use for processing")
    parser.add_argument("--max-articles", type=int, default=None,
                       help="Maximum number of articles to process (for testing)")
    return parser.parse_args()

def find_article_files(input_dir, max_files=None):
    """Find all JSON article files in the input directory"""
    input_path = Path(input_dir)
    article_files = []
    
    # Walk through the directory structure to find all JSON files
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith('.json'):
                article_files.append(os.path.join(root, file))
                if max_files and len(article_files) >= max_files:
                    return article_files
    
    logger.info(f"Found {len(article_files)} article files to process")
    return article_files

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

def process_batch(client, article_files, batch_size):
    """Process a batch of article files and send to API"""
    transformed_articles = []
    
    for file_path in article_files:
        transformed = transform_article(file_path)
        if transformed:
            transformed_articles.append(transformed)
    
    # Skip empty batches
    if not transformed_articles:
        return 0, 0
    
    try:
        result = client.submit_batch(transformed_articles)
        success_count = len(transformed_articles)
        error_count = 0
        batch_id = result.get('batch_id', 'unknown')
        logger.info(f"Batch {batch_id}: Successfully submitted {success_count} articles")
        return success_count, error_count
    except Exception as e:
        logger.error(f"Error submitting batch: {e}")
        return 0, len(transformed_articles)

def main():
    """Main entry point"""
    args = parse_args()
    
    start_time = datetime.now()
    logger.info(f"Starting StoryDredge API client at {start_time}")
    
    # Initialize API client
    client = StoryDredgeClient(
        api_url=args.api_url,
        api_key=args.api_key,
        batch_size=args.batch_size
    )
    
    # Test connection to API
    try:
        health_check = requests.get(f"{args.api_url}/health", timeout=10)
        health_check.raise_for_status()
        logger.info(f"Successfully connected to API: {health_check.json().get('status', 'unknown')}")
    except Exception as e:
        logger.error(f"Failed to connect to API at {args.api_url}: {e}")
        sys.exit(1)
    
    # Find article files
    article_files = find_article_files(args.input_dir, args.max_articles)
    
    if not article_files:
        logger.error("No article files found. Exiting.")
        return
    
    # Process articles in batches with multithreading
    total_success = 0
    total_error = 0
    
    # Group files into batches
    batches = [article_files[i:i + args.batch_size] for i in range(0, len(article_files), args.batch_size)]
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        # Submit batch processing tasks
        future_to_batch = {
            executor.submit(process_batch, client, batch, args.batch_size): i 
            for i, batch in enumerate(batches)
        }
        
        # Process completed tasks
        for i, future in enumerate(as_completed(future_to_batch)):
            batch_index = future_to_batch[future]
            try:
                success, error = future.result()
                total_success += success
                total_error += error
            except Exception as e:
                logger.error(f"Batch {batch_index} raised an exception: {e}")
                total_error += len(batches[batch_index])
            
            # Show progress
            if (i + 1) % 10 == 0 or (i + 1) == len(batches):
                progress = (i + 1) / len(batches) * 100
                logger.info(f"Progress: {progress:.1f}% ({i+1}/{len(batches)} batches)")
    
    # Print summary information
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 60)
    logger.info("Processing Summary")
    logger.info("=" * 60)
    logger.info(f"Total articles found: {len(article_files)}")
    logger.info(f"Articles submitted successfully: {total_success}")
    logger.info(f"Articles failed: {total_error}")
    logger.info(f"Total time: {duration}")
    logger.info(f"Average processing time per article: {duration.total_seconds() / len(article_files):.2f} seconds")
    logger.info("=" * 60)

if __name__ == "__main__":
    main() 