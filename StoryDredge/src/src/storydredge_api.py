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
        port=os.environ.get("DB_PORT", "5433"),  # Updated to 5433
        dbname=os.environ.get("DB_NAME", "storymap"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", "postgres")
    )
    conn.autocommit = True
    return conn

# The rest of the file remains unchanged 