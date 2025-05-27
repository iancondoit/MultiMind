#!/usr/bin/env python3
"""
Direct import of Atlanta Constitution articles to PostgreSQL

This script reads JSON files from the output directory and imports them
directly into a PostgreSQL database without using the API.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extras import Json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pg_import.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("pg_import")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Import Atlanta Constitution articles to PostgreSQL")
    parser.add_argument("--input-dir", type=str, default="output/atlanta-constitution",
                       help="Directory containing processed articles")
    parser.add_argument("--db-host", type=str, default="localhost",
                       help="PostgreSQL host")
    parser.add_argument("--db-port", type=str, default="5432",
                       help="PostgreSQL port")
    parser.add_argument("--db-name", type=str, default="storymap",
                       help="PostgreSQL database name")
    parser.add_argument("--db-user", type=str, default="postgres",
                       help="PostgreSQL user")
    parser.add_argument("--db-password", type=str, default="postgres",
                       help="PostgreSQL password")
    parser.add_argument("--batch-size", type=int, default=1000,
                       help="Number of articles to process in each batch")
    parser.add_argument("--threads", type=int, default=4,
                       help="Number of worker threads")
    parser.add_argument("--max-articles", type=int, default=None,
                       help="Maximum number of articles to process (for testing)")
    parser.add_argument("--skip-existing", action="store_true",
                       help="Skip articles that already exist in the database")
    return parser.parse_args()

def get_db_connection(args):
    """Create and return a database connection"""
    conn = psycopg2.connect(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_password
    )
    conn.autocommit = False
    return conn

def init_database(conn):
    """Initialize the database schema"""
    cursor = conn.cursor()
    
    # Drop existing table if it exists
    cursor.execute("DROP TABLE IF EXISTS articles CASCADE")
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id SERIAL PRIMARY KEY,
        article_id TEXT UNIQUE,
        title TEXT,
        content TEXT,
        date TEXT,
        year INTEGER,
        month INTEGER,
        day INTEGER,
        source TEXT,
        category TEXT,
        tags JSONB,
        metadata JSONB,
        created_at TIMESTAMP DEFAULT NOW()
    )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_date ON articles (date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_source ON articles (source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_category ON articles (category)')
    
    conn.commit()
    logger.info("Database schema initialized")

def find_article_files(input_dir, max_files=None):
    """Find all JSON article files in the input directory"""
    input_path = Path(input_dir)
    article_files = []
    
    logger.info(f"Searching for JSON files in {input_dir}...")
    
    # Walk through the directory structure to find all JSON files
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith('.json'):
                article_files.append(os.path.join(root, file))
                if max_files and len(article_files) >= max_files:
                    logger.info(f"Reached maximum file limit ({max_files})")
                    return article_files
    
    logger.info(f"Found {len(article_files)} article files")
    return article_files

def transform_article(file_path):
    """Transform article data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        # Extract base filename without extension as fallback ID
        filename = os.path.basename(file_path)
        
        # Transform data
        article_id = article_data.get('source_issue', '') + '_' + filename
        title = article_data.get('headline', '')
        content = article_data.get('body', '')
        
        # Parse date components
        date_str = article_data.get('timestamp', '').split('T')[0] if article_data.get('timestamp') else ''
        year, month, day = 0, 0, 0
        if date_str:
            try:
                date_parts = date_str.split('-')
                if len(date_parts) == 3:
                    year = int(date_parts[0])
                    month = int(date_parts[1])
                    day = int(date_parts[2])
            except:
                pass
        
        source = article_data.get('publication', 'Atlanta Constitution')
        category = article_data.get('section', 'news')
        tags = article_data.get('tags', [])
        
        # Additional metadata
        metadata = {
            'source_issue': article_data.get('source_issue', ''),
            'source_url': article_data.get('source_url', ''),
            'word_count': len(content.split()) if content else 0,
            'original_file': file_path
        }
        
        return {
            'article_id': article_id,
            'title': title,
            'content': content,
            'date': date_str,
            'year': year,
            'month': month,
            'day': day,
            'source': source,
            'category': category,
            'tags': tags,
            'metadata': metadata
        }
    
    except Exception as e:
        logger.error(f"Error transforming {file_path}: {e}")
        return None

def import_article_batch(conn, articles, skip_existing=False):
    """Import a batch of articles into the database"""
    try:
        cursor = conn.cursor()
        
        success_count = 0
        skipped_count = 0
        error_count = 0
        
        # Check for existing articles if skip_existing is True
        existing_ids = set()
        if skip_existing and articles:
            article_ids = [a['article_id'] for a in articles]
            id_placeholders = ','.join(['%s'] * len(article_ids))
            cursor.execute(f"SELECT article_id FROM articles WHERE article_id IN ({id_placeholders})", 
                          article_ids)
            existing_ids = {row[0] for row in cursor.fetchall()}
            if existing_ids:
                logger.info(f"Found {len(existing_ids)} existing articles that will be skipped")
        
        # Insert articles
        for article in articles:
            try:
                # Skip if article already exists and skip_existing is True
                if skip_existing and article['article_id'] in existing_ids:
                    skipped_count += 1
                    continue
                
                cursor.execute('''
                INSERT INTO articles 
                (article_id, title, content, date, year, month, day, 
                 source, category, tags, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (article_id) DO UPDATE SET
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                date = EXCLUDED.date,
                year = EXCLUDED.year,
                month = EXCLUDED.month,
                day = EXCLUDED.day,
                source = EXCLUDED.source,
                category = EXCLUDED.category,
                tags = EXCLUDED.tags,
                metadata = EXCLUDED.metadata
                ''', (
                    article['article_id'],
                    article['title'],
                    article['content'],
                    article['date'],
                    article['year'],
                    article['month'],
                    article['day'],
                    article['source'],
                    article['category'],
                    Json(article['tags']),
                    Json(article['metadata'])
                ))
                success_count += 1
            except Exception as e:
                logger.error(f"Error inserting article {article['article_id']}: {e}")
                error_count += 1
        
        # Commit the batch
        conn.commit()
        
        return success_count, skipped_count, error_count
    
    except Exception as e:
        conn.rollback()
        logger.error(f"Batch import error: {e}")
        return 0, 0, len(articles)

def process_batch(file_batch, args):
    """Process a batch of article files"""
    # Transform articles
    articles = []
    for file_path in file_batch:
        article = transform_article(file_path)
        if article:
            articles.append(article)
    
    if not articles:
        return 0, 0, 0
    
    # Connect to database
    try:
        conn = get_db_connection(args)
        success, skipped, errors = import_article_batch(conn, articles, args.skip_existing)
        conn.close()
        return success, skipped, errors
    except Exception as e:
        logger.error(f"Error processing batch: {e}")
        return 0, 0, len(articles)

def main():
    """Main entry point"""
    args = parse_args()
    
    start_time = datetime.now()
    logger.info(f"Starting import at {start_time}")
    
    # Test database connection
    try:
        conn = get_db_connection(args)
        logger.info("Connected to PostgreSQL database")
        init_database(conn)
        conn.close()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        sys.exit(1)
    
    # Find article files
    article_files = find_article_files(args.input_dir, args.max_articles)
    
    if not article_files:
        logger.error("No article files found. Exiting.")
        sys.exit(1)
    
    # Group files into batches
    batches = [article_files[i:i + args.batch_size] for i in range(0, len(article_files), args.batch_size)]
    logger.info(f"Processing {len(article_files)} files in {len(batches)} batches")
    
    # Process batches with multithreading
    total_success = 0
    total_skipped = 0
    total_error = 0
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        # Submit batch processing tasks
        future_to_batch = {
            executor.submit(process_batch, batch, args): i 
            for i, batch in enumerate(batches)
        }
        
        # Process completed tasks
        for i, future in enumerate(as_completed(future_to_batch)):
            batch_index = future_to_batch[future]
            try:
                success, skipped, error = future.result()
                total_success += success
                total_skipped += skipped
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
    logger.info("Import Summary")
    logger.info("=" * 60)
    logger.info(f"Total files processed: {len(article_files)}")
    logger.info(f"Articles imported successfully: {total_success}")
    logger.info(f"Articles skipped (already existed): {total_skipped}")
    logger.info(f"Articles failed: {total_error}")
    logger.info(f"Total time: {duration}")
    logger.info(f"Average time per article: {duration.total_seconds() / len(article_files):.2f} seconds")
    logger.info("=" * 60)
    
    # Display database information
    try:
        conn = get_db_connection(args)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM articles")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(date), MAX(date) FROM articles")
        min_date, max_date = cursor.fetchone()
        
        cursor.execute("SELECT category, COUNT(*) FROM articles GROUP BY category ORDER BY COUNT(*) DESC LIMIT 5")
        categories = cursor.fetchall()
        
        conn.close()
        
        logger.info("Database Statistics:")
        logger.info(f"Total articles in database: {total_count}")
        logger.info(f"Date range: {min_date} to {max_date}")
        logger.info("Top categories:")
        for category, count in categories:
            logger.info(f"  {category}: {count} articles")
    except Exception as e:
        logger.error(f"Error fetching database statistics: {e}")
    
    logger.info("Import completed successfully")

if __name__ == "__main__":
    main() 