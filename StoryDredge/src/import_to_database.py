#!/usr/bin/env python3
"""
Import processed Atlanta Constitution articles into a database for research
"""

import os
import sys
import json
import argparse
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("db_importer")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Import processed articles into database")
    parser.add_argument("--input-dir", type=str, default="output/atlanta-constitution",
                       help="Directory containing processed articles")
    parser.add_argument("--db-file", type=str, default="atlanta_constitution.db",
                       help="SQLite database file")
    parser.add_argument("--threads", type=int, default=4,
                       help="Number of threads to use for importing")
    parser.add_argument("--overwrite", action="store_true",
                       help="Overwrite existing database")
    return parser.parse_args()

def init_database(db_path, overwrite=False):
    """Initialize the database schema"""
    if db_path.exists() and overwrite:
        logger.info(f"Removing existing database: {db_path}")
        os.remove(db_path)
    
    logger.info(f"Initializing database: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
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
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_date ON articles (date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_year ON articles (year)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_title ON articles (title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_newspaper ON articles (newspaper)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_type ON entities (entity_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_text ON entities (entity_text)')
    
    # Store metadata
    cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', 
                  ('import_date', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return db_path

def find_article_files(input_dir):
    """Find all JSON article files in the input directory"""
    input_path = Path(input_dir)
    article_files = []
    
    # Walk through the directory structure to find all JSON files
    for root, dirs, files in os.walk(input_path):
        for file in files:
            if file.endswith('.json'):
                article_files.append(os.path.join(root, file))
    
    logger.info(f"Found {len(article_files)} article files to import")
    return article_files

def import_article(article_path, db_path):
    """Import a single article file into the database"""
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        # Connect to database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Extract article data
        article_id = article_data.get('id', os.path.basename(article_path))
        title = article_data.get('title', '')
        date_str = article_data.get('date', '')
        
        # Parse date components
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.month
            day = date_obj.day
        except:
            year = 0
            month = 0
            day = 0
        
        # Get article text
        full_text = article_data.get('text', '')
        word_count = len(full_text.split()) if full_text else 0
        
        # Get metadata
        page_number = article_data.get('page', '')
        section = article_data.get('section', '')
        article_type = article_data.get('type', '')
        author = article_data.get('author', '')
        newspaper = article_data.get('newspaper', 'atlanta-constitution')
        issue_id = article_data.get('issue_id', '')
        
        # Insert article record
        cursor.execute('''
        INSERT OR REPLACE INTO articles 
        (article_id, title, date, year, month, day, full_text, word_count, 
         page_number, section, type, author, newspaper, issue_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_id, title, date_str, year, month, day, full_text, word_count,
            page_number, section, article_type, author, newspaper, issue_id, 
            datetime.now().isoformat()
        ))
        
        # Import entities if present
        entities = article_data.get('entities', {})
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                if isinstance(entity, dict):
                    entity_text = entity.get('text', '')
                    entity_count = entity.get('count', 1)
                else:
                    entity_text = entity
                    entity_count = 1
                
                cursor.execute('''
                INSERT INTO entities (article_id, entity_text, entity_type, entity_count)
                VALUES (?, ?, ?, ?)
                ''', (article_id, entity_text, entity_type, entity_count))
        
        # Commit and close
        conn.commit()
        conn.close()
        
        return True
    
    except Exception as e:
        logger.error(f"Error importing {article_path}: {e}")
        return False

def import_batch(article_files, db_path, max_workers=4):
    """Import a batch of articles using multiple threads"""
    success_count = 0
    error_count = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all import tasks
        future_to_file = {executor.submit(import_article, file, db_path): file 
                         for file in article_files}
        
        # Process completed tasks with a progress counter
        total = len(article_files)
        for i, future in enumerate(as_completed(future_to_file)):
            file = future_to_file[future]
            try:
                result = future.result()
                if result:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                logger.error(f"Import task for {file} raised an exception: {e}")
                error_count += 1
            
            # Show progress every 100 articles
            if (i + 1) % 100 == 0:
                logger.info(f"Progress: {i+1}/{total} articles imported")
    
    logger.info(f"Successfully imported {success_count} articles")
    logger.info(f"Failed to import {error_count} articles")
    
    return success_count, error_count

def add_database_stats(db_path):
    """Add statistics to the database metadata table"""
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get article count
    cursor.execute('SELECT COUNT(*) FROM articles')
    article_count = cursor.fetchone()[0]
    
    # Get entity count
    cursor.execute('SELECT COUNT(*) FROM entities')
    entity_count = cursor.fetchone()[0]
    
    # Get date range
    cursor.execute('SELECT MIN(date), MAX(date) FROM articles')
    min_date, max_date = cursor.fetchone()
    
    # Get newspaper names
    cursor.execute('SELECT DISTINCT newspaper FROM articles')
    newspapers = [row[0] for row in cursor.fetchall()]
    
    # Store stats in metadata table
    cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', 
                  ('article_count', str(article_count)))
    cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', 
                  ('entity_count', str(entity_count)))
    cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', 
                  ('date_range', f"{min_date} to {max_date}"))
    cursor.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', 
                  ('newspapers', json.dumps(newspapers)))
    
    conn.commit()
    conn.close()
    
    return {
        'article_count': article_count,
        'entity_count': entity_count,
        'date_range': f"{min_date} to {max_date}",
        'newspapers': newspapers
    }

def main():
    """Main entry point"""
    args = parse_args()
    
    start_time = datetime.now()
    logger.info(f"Starting import at {start_time}")
    
    # Initialize database
    db_path = Path(args.db_file)
    init_database(db_path, args.overwrite)
    
    # Find article files
    article_files = find_article_files(args.input_dir)
    
    if not article_files:
        logger.error("No article files found. Exiting.")
        return
    
    # Import articles
    success_count, error_count = import_batch(
        article_files, 
        db_path, 
        max_workers=args.threads
    )
    
    # Add database statistics
    stats = add_database_stats(db_path)
    
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
    logger.info(f"Total entities: {stats['entity_count']}")
    logger.info(f"Date range: {stats['date_range']}")
    logger.info(f"Total time: {duration}")
    logger.info("=" * 60)

 