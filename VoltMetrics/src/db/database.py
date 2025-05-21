"""
Database connection module for VoltMetrics.

This module provides database connection utilities for VoltMetrics, 
implementing the database connection with SQLAlchemy.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Use SQLite for development/testing
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./voltmetrics.db"
)

# Create SQLAlchemy engine
# Note: For SQLite, we need to enable foreign key constraints explicitly
connect_args = {"check_same_thread": False}
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

def get_db():
    """
    Get a database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        with get_db() as db:
            db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 