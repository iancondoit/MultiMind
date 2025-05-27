#!/usr/bin/env python3
"""
Simple test for importing articles to SQLite
"""
import os
import sys
import json
import sqlite3
import random
from pathlib import Path
from datetime import datetime

# Configure output with timestamps
def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

log(f"Starting import test at {datetime.now()}")

# Create database
db_path = "test_articles.db"
log(f"Creating database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY,
        article_id TEXT UNIQUE,
        title TEXT,
        date TEXT,
        section TEXT,
        content TEXT,
        newspaper TEXT,
        issue_id TEXT,
        created_at TEXT
    )
    ''')
    conn.commit()
    log("Database schema created successfully")
except Exception as e:
    log(f"Error creating database: {e}")
    sys.exit(1)

# Find JSON files
input_dir = "output/atlanta-constitution"
log(f"Searching for JSON files in {input_dir}...")

if not os.path.exists(input_dir):
    log(f"Error: Directory not found: {input_dir}")
    sys.exit(1)

all_json_files = []
try:
    for root, dirs, files in os.walk(Path(input_dir)):
        for file in files:
            if file.endswith('.json'):
                all_json_files.append(os.path.join(root, file))
                if len(all_json_files) >= 1000:  # Limit for faster iteration
                    break
        if len(all_json_files) >= 1000:
            break
except Exception as e:
    log(f"Error searching for files: {e}")
    sys.exit(1)

log(f"Found {len(all_json_files)} JSON files")

if not all_json_files:
    log("No JSON files found. Exiting.")
    sys.exit(1)

# Sample files for testing
sample_size = 50
if len(all_json_files) > sample_size:
    article_files = random.sample(all_json_files, sample_size)
else:
    article_files = all_json_files

log(f"Processing {len(article_files)} sample files")

# Show first few files to debug
log("First 5 files to process:")
for i, file_path in enumerate(article_files[:5]):
    log(f"  {i+1}: {file_path}")

# Import articles
success_count = 0
error_count = 0

for i, file_path in enumerate(article_files):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        # Extract data
        article_id = os.path.basename(file_path)
        title = article_data.get('headline', '')
        date_str = article_data.get('timestamp', '').split('T')[0] if article_data.get('timestamp') else ''
        section = article_data.get('section', '')
        content = article_data.get('body', '')
        newspaper = article_data.get('publication', 'Atlanta Constitution')
        issue_id = article_data.get('source_issue', '')
        
        # Insert article
        cursor.execute('''
        INSERT OR REPLACE INTO articles 
        (article_id, title, date, section, content, newspaper, issue_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_id, title, date_str, section, content, newspaper, issue_id, 
            datetime.now().isoformat()
        ))
        
        conn.commit()  # Commit each article individually for safety
        success_count += 1
        
        # Show progress every 10 articles
        if (i + 1) % 10 == 0:
            log(f"Progress: {i+1}/{len(article_files)} articles imported")
        
    except Exception as e:
        error_count += 1
        log(f"Error importing {file_path}: {e}")

# Show sample of data
try:
    log("Sample data from imported articles:")
    cursor.execute("SELECT id, title, date, section FROM articles LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        log(f"  ID: {row[0]}, Title: {row[1]}, Date: {row[2]}, Section: {row[3]}")
except Exception as e:
    log(f"Error querying data: {e}")

# Show summary
try:
    cursor.execute("SELECT COUNT(*) FROM articles")
    count = cursor.fetchone()[0]
    log(f"Successfully imported {success_count} articles to {db_path}")
    log(f"Errors: {error_count}")
    log(f"Total in database: {count}")
    log(f"To examine the data, run: sqlite3 {db_path}")
except Exception as e:
    log(f"Error getting summary: {e}")

# Close database
try:
    cursor.close()
    conn.close()
    log("Database connection closed")
except Exception as e:
    log(f"Error closing database: {e}")

log(f"Import test completed at {datetime.now()}") 