#!/usr/bin/env python3
"""
Very simple test to import one article to SQLite
"""
import os
import json
import sqlite3
from datetime import datetime

print(f"Starting simple test at {datetime.now()}")

# Set file path
file_path = "output/atlanta-constitution/atlanta-constitution/1944/03/03/1944-03-03--georgia.json"
if not os.path.exists(file_path):
    print(f"Error: File not found: {file_path}")
    exit(1)

print(f"Reading file: {file_path}")

# Read the file
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        article_data = json.load(f)
    print("Successfully read the file")
except Exception as e:
    print(f"Error reading file: {e}")
    exit(1)

# Create database
db_path = "one_article.db"
print(f"Creating database: {db_path}")

try:
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
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
    print("Created database table")
    
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
    
    conn.commit()
    print("Inserted article into database")
    
    # Show the data
    cursor.execute("SELECT * FROM articles")
    row = cursor.fetchone()
    if row:
        print(f"Article in database: {row[0]}, Title: {row[2]}, Date: {row[3]}")
    else:
        print("No article found in database")
        
    conn.close()
    print("Database connection closed")
    
except Exception as e:
    print(f"Database error: {e}")
    exit(1)

print(f"Test completed at {datetime.now()}")
print(f"Database created at: {os.path.abspath(db_path)}") 