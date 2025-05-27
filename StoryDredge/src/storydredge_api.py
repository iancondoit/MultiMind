#!/usr/bin/env python3
"""
StoryDredge API Server

This Flask application provides an API for receiving and processing article data
from StoryDredge and storing it in a PostgreSQL database.
"""

import os
import json
import uuid
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import Json, DictCursor
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("storydredge_api")

# Initialize Flask app
app = Flask(__name__)

# API version
API_VERSION = "1.0.0"

# Database connection
def get_db_connection():
    """Create and return a database connection"""
    conn = psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "storymap"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres")
    )
    conn.autocommit = True
    return conn

def init_db():
    """Initialize database schema if not exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        source TEXT NOT NULL,
        date DATE NOT NULL,
        category TEXT NOT NULL,
        tags JSONB,
        metadata JSONB,
        processing_status TEXT NOT NULL DEFAULT 'pending',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS processing_batches (
        batch_id TEXT PRIMARY KEY,
        articles_count INTEGER NOT NULL,
        processing_status TEXT NOT NULL DEFAULT 'queued',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    )
    ''')
    
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_articles_date ON articles (date)
    ''')
    
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_articles_source ON articles (source)
    ''')
    
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_articles_processing_status ON articles (processing_status)
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()
    
    logger.info("Database initialized")

# API key authentication
def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_api_key = os.environ.get('API_KEY', 'test_api_key')
        
        if api_key != expected_api_key:
            return jsonify({
                "error": "Invalid API key",
                "code": "AUTHENTICATION_ERROR"
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

# API endpoints
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "version": API_VERSION
    })

@app.route('/api/articles', methods=['POST'])
@api_key_required
def submit_article():
    """Submit a single article"""
    if not request.json:
        return jsonify({
            "error": "Invalid request format",
            "details": "Request must be JSON",
            "code": "VALIDATION_ERROR"
        }), 400
    
    article_data = request.json
    
    # Validate required fields
    required_fields = ['id', 'title', 'content', 'source', 'date', 'category']
    for field in required_fields:
        if field not in article_data:
            return jsonify({
                "error": "Invalid article data",
                "details": f"Missing required field: {field}",
                "code": "VALIDATION_ERROR"
            }), 400
    
    try:
        # Store article in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO articles 
        (id, title, content, source, date, category, tags, metadata, processing_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        content = EXCLUDED.content,
        source = EXCLUDED.source,
        date = EXCLUDED.date,
        category = EXCLUDED.category,
        tags = EXCLUDED.tags,
        metadata = EXCLUDED.metadata,
        processing_status = 'pending',
        updated_at = NOW()
        ''', (
            article_data['id'],
            article_data['title'],
            article_data['content'],
            article_data['source'],
            article_data['date'],
            article_data['category'],
            Json(article_data.get('tags', [])),
            Json(article_data.get('metadata', {})),
            'queued'
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Return success response
        return jsonify({
            "status": "success",
            "article_id": article_data['id'],
            "processing_status": "queued"
        })
    
    except Exception as e:
        logger.error(f"Error processing article {article_data.get('id', 'unknown')}: {str(e)}")
        return jsonify({
            "error": "Error processing article",
            "details": str(e),
            "code": "PROCESSING_ERROR"
        }), 500

@app.route('/api/articles/batch', methods=['POST'])
@api_key_required
def submit_batch():
    """Submit a batch of articles"""
    if not request.json or 'articles' not in request.json:
        return jsonify({
            "error": "Invalid batch format",
            "details": "Request must contain 'articles' array",
            "code": "VALIDATION_ERROR"
        }), 400
    
    articles = request.json['articles']
    
    if not articles or not isinstance(articles, list):
        return jsonify({
            "error": "Invalid batch format",
            "details": "'articles' must be a non-empty array",
            "code": "VALIDATION_ERROR"
        }), 400
    
    # Generate a batch ID
    batch_id = str(uuid.uuid4())
    
    try:
        # Store batch information
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create batch record
        cursor.execute('''
        INSERT INTO processing_batches 
        (batch_id, articles_count, processing_status, created_at)
        VALUES (%s, %s, %s, %s)
        ''', (
            batch_id,
            len(articles),
            'queued',
            datetime.now()
        ))
        
        # Store articles
        for article in articles:
            # Validate required fields
            required_fields = ['id', 'title', 'content', 'source', 'date', 'category']
            missing_fields = [field for field in required_fields if field not in article]
            
            if missing_fields:
                logger.warning(f"Skipping article with missing fields: {missing_fields}")
                continue
            
            cursor.execute('''
            INSERT INTO articles 
            (id, title, content, source, date, category, tags, metadata, processing_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            source = EXCLUDED.source,
            date = EXCLUDED.date,
            category = EXCLUDED.category,
            tags = EXCLUDED.tags,
            metadata = EXCLUDED.metadata,
            processing_status = 'queued',
            updated_at = NOW()
            ''', (
                article['id'],
                article['title'],
                article['content'],
                article['source'],
                article['date'],
                article['category'],
                Json(article.get('tags', [])),
                Json(article.get('metadata', {})),
                'queued'
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Return success response
        return jsonify({
            "status": "success",
            "batch_id": batch_id,
            "articles_processed": len(articles),
            "processing_status": "queued"
        })
    
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        return jsonify({
            "error": "Error processing batch",
            "details": str(e),
            "code": "PROCESSING_ERROR"
        }), 500

@app.route('/api/articles/status/<article_id>', methods=['GET'])
@api_key_required
def check_status(article_id):
    """Check the processing status of an article"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        cursor.execute('''
        SELECT id, processing_status, updated_at 
        FROM articles 
        WHERE id = %s
        ''', (article_id,))
        
        article = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not article:
            return jsonify({
                "error": "Article not found",
                "article_id": article_id,
                "code": "NOT_FOUND_ERROR"
            }), 404
        
        return jsonify({
            "status": "success",
            "article_id": article['id'],
            "processing_status": article['processing_status'],
            "processing_time": article['updated_at'].isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error checking status for article {article_id}: {str(e)}")
        return jsonify({
            "error": "Error checking article status",
            "details": str(e),
            "code": "DATABASE_ERROR"
        }), 500

@app.route('/api/batch/status/<batch_id>', methods=['GET'])
@api_key_required
def check_batch_status(batch_id):
    """Check the processing status of a batch"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=DictCursor)
        
        cursor.execute('''
        SELECT batch_id, articles_count, processing_status, updated_at 
        FROM processing_batches 
        WHERE batch_id = %s
        ''', (batch_id,))
        
        batch = cursor.fetchone()
        
        if not batch:
            cursor.close()
            conn.close()
            return jsonify({
                "error": "Batch not found",
                "batch_id": batch_id,
                "code": "NOT_FOUND_ERROR"
            }), 404
        
        # Get article statuses
        cursor.execute('''
        SELECT processing_status, COUNT(*) as count
        FROM articles
        WHERE id IN (
            SELECT id FROM articles
            WHERE metadata->>'batch_id' = %s
        )
        GROUP BY processing_status
        ''', (batch_id,))
        
        status_counts = {row['processing_status']: row['count'] for row in cursor.fetchall()}
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "batch_id": batch['batch_id'],
            "articles_count": batch['articles_count'],
            "processing_status": batch['processing_status'],
            "processing_time": batch['updated_at'].isoformat(),
            "status_breakdown": status_counts
        })
    
    except Exception as e:
        logger.error(f"Error checking status for batch {batch_id}: {str(e)}")
        return jsonify({
            "error": "Error checking batch status",
            "details": str(e),
            "code": "DATABASE_ERROR"
        }), 500

if __name__ == "__main__":
    # Initialize database tables
    init_db()
    
    # Start Flask server
    port = int(os.environ.get("API_PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", "false").lower() == "true") 