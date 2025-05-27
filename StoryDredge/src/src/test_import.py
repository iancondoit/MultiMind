#!/usr/bin/env python3
"""
Standalone test for article import

This script tests the article import process without requiring Docker.
"""

import os
import json
import argparse
import sqlite3
from pathlib import Path
import random
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_import")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Test article import")
    parser.add_argument("--input-dir", type=str, default="output/atlanta-constitution",
                       help="Directory containing processed articles")
    parser.add_argument("--db-file", type=str, default="test_articles.db",
                       help="SQLite database file")
    parser.add_argument("--sample-size", type=int, default=100,
                       help="Number of articles to sample for testing")
    return parser.parse_args()

def init_database(db_path):
    """Initialize the database schema"""
    logger.info(f"Initializing database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY,
        article_id TEXT UNIQUE,
        title TEXT,
        date TEXT,
        year INTEGER,
        month INTEGER,
        day INTEGER,
        full_text TEXT,
        word_count INTEGER,
        page_number TEXT,
        section TEXT,
        type TEXT,
        author TEXT,
        newspaper TEXT,
        issue_id TEXT,
        created_at TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS entities (
        id INTEGER PRIMARY KEY,
        article_id TEXT,
        entity_text TEXT,
        entity_type TEXT,
        entity_count INTEGER,
        FOREIGN KEY (article_id) REFERENCES articles (article_id)
    )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_date ON articles (date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_title ON articles (title)')
    
    conn.commit()
    conn.close()
    
    return db_path

def find_random_articles(input_dir, sample_size=100):
    """Find random article files for testing"""
    input_path = Path(input_dir)
    all_json_files = []
    
    # Find all JSON files
    logger.info(f"Searching for JSON files in {input_dir}...")
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith('.json'):
                all_json_files.append(os.path.join(root, file))
                # Add early exit if we want to avoid scanning the whole directory structure
                if len(all_json_files) >= 1000 and len(all_json_files) >= sample_size * 2:
                    break
    
    logger.info(f"Found {len(all_json_files)} JSON files")
    
    # Sample random files
    if len(all_json_files) <= sample_size:
        return all_json_files
    
    sampled_files = random.sample(all_json_files, sample_size)
    logger.info(f"Sampled {len(sampled_files)} files for processing")
    return sampled_files

def import_article(article_path, db_path):
    """Import a single article file into the database"""
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Extract article data
        article_id = article_data.get('source_issue', '') + '--' + os.path.basename(article_path)
        title = article_data.get('headline', '')
        date_str = article_data.get('timestamp', '').split('T')[0] if article_data.get('timestamp') else ''
        
        # Parse date components
        try:
            date_parts = date_str.split('-')
            year = int(date_parts[0])
            month = int(date_parts[1])
            day = int(date_parts[2])
        except:
            year = 0
            month = 0
            day = 0
        
        # Get article text
        full_text = article_data.get('body', '')
        word_count = len(full_text.split()) if full_text else 0
        
        # Get metadata
        section = article_data.get('section', '')
        tags = article_data.get('tags', [])
        newspaper = article_data.get('publication', 'Atlanta Constitution')
        issue_id = article_data.get('source_issue', '')
        
        # Insert article record
        cursor.execute('''
        INSERT OR REPLACE INTO articles 
        (article_id, title, date, year, month, day, full_text, word_count, 
         section, type, newspaper, issue_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_id, title, date_str, year, month, day, full_text, word_count,
            section, section, newspaper, issue_id, 
            datetime.now().isoformat()
        ))
        
        # Import entities (tags)
        for tag in tags:
            cursor.execute('''
            INSERT INTO entities (article_id, entity_text, entity_type, entity_count)
            VALUES (?, ?, ?, ?)
            ''', (article_id, tag, 'tag', 1))
        
        # Commit and close
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error importing {article_path}: {e}")
        return False

def main():
    """Main entry point"""
    args = parse_args()
    
    start_time = datetime.now()
    logger.info(f"Starting test import at {start_time}")
    
    # Initialize database
    db_path = init_database(args.db_file)
    
    # Find article files
    article_files = find_random_articles(args.input_dir, args.sample_size)
    
    if not article_files:
        logger.error("No article files found. Exiting.")
        return
    
    # Import articles
    success_count = 0
    error_count = 0
    
    for i, file_path in enumerate(article_files):
        if import_article(file_path, db_path):
            success_count += 1
        else:
            error_count += 1
        
        # Show progress every 10 articles
        if (i + 1) % 10 == 0:
            logger.info(f"Progress: {i+1}/{len(article_files)} articles imported")
    
    # Print summary information
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("=" * 60)
    logger.info("Import Summary")
    logger.info("=" * 60)
    logger.info(f"Database: {db_path}")
    logger.info(f"Total articles found: {len(article_files)}")
    logger.info(f"Articles imported: {success_count}")
    logger.info(f"Articles failed: {error_count}")
    logger.info(f"Total time: {duration}")
    logger.info(f"Average time per article: {duration.total_seconds() / len(article_files):.2f} seconds")
    logger.info("=" * 60)
    
    # Show SQLite command to view the results
    logger.info(f"To examine the data, run: sqlite3 {db_path}")
    logger.info("Example queries:")
    logger.info("  SELECT COUNT(*) FROM articles;")
    logger.info("  SELECT title, date, section FROM articles LIMIT 10;")
    logger.info("  SELECT entity_text, COUNT(*) FROM entities GROUP BY entity_text ORDER BY COUNT(*) DESC LIMIT 20;")

if __name__ == "__main__":
    main() 