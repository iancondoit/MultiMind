#!/usr/bin/env python3
"""
Incremental Database Backup to AWS S3
=====================================

This script safely backs up the PostgreSQL database to AWS S3 in incremental chunks,
designed to run alongside the production pipeline without interference.

Features:
- Incremental backup (only new articles since last backup)
- Checkpoint system for resume capability
- Parallel processing for performance
- Safe concurrent operation with production pipeline
- Comprehensive logging and monitoring
"""

import os
import sys
import json
import time
import signal
import argparse
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

class IncrementalDBBackup:
    def __init__(self, 
                 chunk_size: int = 1000,
                 max_workers: int = 4,
                 checkpoint_file: str = "logs/db_backup_checkpoint.json"):
        """
        Initialize the incremental database backup system.
        
        Args:
            chunk_size: Number of articles to backup per chunk
            max_workers: Number of parallel upload threads
            checkpoint_file: Path to checkpoint file for resume capability
        """
        self.chunk_size = chunk_size
        self.max_workers = max_workers
        self.checkpoint_file = checkpoint_file
        self.should_stop = False
        
        # AWS S3 setup
        self.s3_client = boto3.client('s3')
        self.bucket_name = "storydredge-processed-output"
        self.backup_prefix = "database_backups"
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
        
        # Database connection
        self.db_config = {
            'host': 'localhost',
            'port': '5433',
            'database': 'storymap',
            'user': 'postgres',
            'password': 'postgres'
        }
        
        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'articles_backed_up': 0,
            'chunks_completed': 0,
            'total_size_bytes': 0,
            'last_article_id': 0
        }
        
        # Setup logging
        self._setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self):
        """Setup logging configuration."""
        log_file = f"logs/incremental_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logger.remove()
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> | <level>{message}</level>",
            level="INFO"
        )
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}",
            level="DEBUG",
            rotation="100 MB"
        )

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.should_stop = True

    def _ensure_bucket_exists(self):
        """Ensure the S3 bucket exists, create if it doesn't."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"S3 bucket {self.bucket_name} exists")
        except Exception as e:
            if "404" in str(e):
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created S3 bucket {self.bucket_name}")
                except Exception as create_error:
                    logger.error(f"Failed to create S3 bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking S3 bucket: {e}")
                raise

    def load_checkpoint(self) -> Dict:
        """Load checkpoint data from file."""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r') as f:
                    checkpoint = json.load(f)
                logger.info(f"Loaded checkpoint: last_article_id={checkpoint.get('last_article_id', 0)}")
                return checkpoint
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        
        return {'last_article_id': 0, 'last_backup_time': None}

    def save_checkpoint(self, last_article_id: int):
        """Save checkpoint data to file."""
        checkpoint = {
            'last_article_id': last_article_id,
            'last_backup_time': datetime.now().isoformat(),
            'stats': self.stats
        }
        
        try:
            os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def get_database_stats(self) -> Tuple[int, int]:
        """Get current database statistics."""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor() as cur:
                    # Get total article count
                    cur.execute("SELECT COUNT(*) FROM articles")
                    total_count = cur.fetchone()[0]
                    
                    # Get max article ID
                    cur.execute("SELECT COALESCE(MAX(id), 0) FROM articles")
                    max_id = cur.fetchone()[0]
                    
                    return total_count, max_id
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return 0, 0

    def get_articles_chunk(self, start_id: int, limit: int) -> List[Dict]:
        """Get a chunk of articles from the database."""
        try:
            with psycopg2.connect(**self.db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, title, content, publication, source_url, 
                               timestamp, quality_score, newsworthiness_score, unusualness_score
                        FROM articles 
                        WHERE id > %s 
                        ORDER BY id 
                        LIMIT %s
                    """, (start_id, limit))
                    
                    return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get articles chunk: {e}")
            return []

    def upload_chunk_to_s3(self, chunk_data: List[Dict], chunk_id: int) -> bool:
        """Upload a chunk of articles to S3."""
        try:
            # Create chunk filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.backup_prefix}/chunks/chunk_{chunk_id:06d}_{timestamp}.json"
            
            # Convert to JSON
            chunk_json = json.dumps(chunk_data, indent=2, default=str)
            chunk_bytes = chunk_json.encode('utf-8')
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=chunk_bytes,
                ContentType='application/json',
                Metadata={
                    'chunk_id': str(chunk_id),
                    'article_count': str(len(chunk_data)),
                    'backup_time': timestamp,
                    'size_bytes': str(len(chunk_bytes))
                }
            )
            
            # Update statistics
            self.stats['total_size_bytes'] += len(chunk_bytes)
            
            logger.info(f"✅ Uploaded chunk {chunk_id}: {len(chunk_data)} articles ({len(chunk_bytes):,} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upload chunk {chunk_id}: {e}")
            return False

    def create_backup_manifest(self, total_articles: int, total_chunks: int):
        """Create and upload a backup manifest file."""
        try:
            manifest = {
                'backup_info': {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'incremental',
                    'total_articles': total_articles,
                    'total_chunks': total_chunks,
                    'chunk_size': self.chunk_size
                },
                'statistics': self.stats,
                'database_info': {
                    'host': self.db_config['host'],
                    'database': self.db_config['database'],
                    'backup_range': {
                        'start_id': self.stats.get('start_id', 0),
                        'end_id': self.stats['last_article_id']
                    }
                }
            }
            
            manifest_json = json.dumps(manifest, indent=2, default=str)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.backup_prefix}/manifests/backup_manifest_{timestamp}.json"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=filename,
                Body=manifest_json.encode('utf-8'),
                ContentType='application/json'
            )
            
            logger.info(f"✅ Created backup manifest: {filename}")
            
        except Exception as e:
            logger.error(f"Failed to create backup manifest: {e}")

    def run_backup(self):
        """Run the incremental backup process."""
        logger.info("🚀 Starting incremental database backup...")
        
        # Load checkpoint
        checkpoint = self.load_checkpoint()
        start_id = checkpoint.get('last_article_id', 0)
        self.stats['start_id'] = start_id
        
        # Get current database stats
        total_articles, max_id = self.get_database_stats()
        articles_to_backup = max_id - start_id
        
        logger.info(f"📊 Database Status:")
        logger.info(f"   Total articles in DB: {total_articles:,}")
        logger.info(f"   Max article ID: {max_id:,}")
        logger.info(f"   Last backed up ID: {start_id:,}")
        logger.info(f"   Articles to backup: {articles_to_backup:,}")
        
        if articles_to_backup <= 0:
            logger.info("✅ Database is already up to date!")
            return
        
        # Calculate chunks
        total_chunks = (articles_to_backup + self.chunk_size - 1) // self.chunk_size
        logger.info(f"📦 Will create {total_chunks} chunks of {self.chunk_size} articles each")
        
        # Process chunks
        current_id = start_id
        chunk_id = 1
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            while current_id < max_id and not self.should_stop:
                # Get chunk of articles
                chunk_data = self.get_articles_chunk(current_id, self.chunk_size)
                
                if not chunk_data:
                    break
                
                # Submit upload task
                future = executor.submit(self.upload_chunk_to_s3, chunk_data, chunk_id)
                futures.append((future, chunk_data[-1]['id'], len(chunk_data)))
                
                # Update current position
                current_id = chunk_data[-1]['id']
                chunk_id += 1
                
                # Process completed uploads
                if len(futures) >= self.max_workers:
                    self._process_completed_futures(futures)
            
            # Process remaining futures
            self._process_completed_futures(futures, wait_all=True)
        
        if not self.should_stop:
            # Create backup manifest
            self.create_backup_manifest(self.stats['articles_backed_up'], self.stats['chunks_completed'])
            
            # Final statistics
            elapsed_time = datetime.now() - self.stats['start_time']
            logger.info("🎉 Backup completed successfully!")
            logger.info(f"📊 Final Statistics:")
            logger.info(f"   Articles backed up: {self.stats['articles_backed_up']:,}")
            logger.info(f"   Chunks created: {self.stats['chunks_completed']:,}")
            logger.info(f"   Total size: {self.stats['total_size_bytes'] / 1024 / 1024:.1f} MB")
            logger.info(f"   Time elapsed: {elapsed_time}")
            logger.info(f"   Average speed: {self.stats['articles_backed_up'] / elapsed_time.total_seconds():.1f} articles/second")

    def _process_completed_futures(self, futures: List, wait_all: bool = False):
        """Process completed upload futures."""
        completed = []
        
        for future, last_id, count in futures:
            if wait_all or future.done():
                try:
                    success = future.result(timeout=30 if wait_all else 0)
                    if success:
                        self.stats['articles_backed_up'] += count
                        self.stats['chunks_completed'] += 1
                        self.stats['last_article_id'] = last_id
                        
                        # Save checkpoint periodically
                        if self.stats['chunks_completed'] % 10 == 0:
                            self.save_checkpoint(last_id)
                            
                        # Progress update
                        elapsed = datetime.now() - self.stats['start_time']
                        rate = self.stats['articles_backed_up'] / elapsed.total_seconds()
                        logger.info(f"📈 Progress: {self.stats['chunks_completed']} chunks, "
                                  f"{self.stats['articles_backed_up']:,} articles "
                                  f"({rate:.1f} articles/sec)")
                    
                    completed.append((future, last_id, count))
                    
                except Exception as e:
                    logger.error(f"Upload failed: {e}")
                    completed.append((future, last_id, count))
        
        # Remove completed futures
        for item in completed:
            if item in futures:
                futures.remove(item)

def main():
    parser = argparse.ArgumentParser(description="Incremental Database Backup to AWS S3")
    parser.add_argument("--chunk-size", type=int, default=1000,
                       help="Number of articles per backup chunk (default: 1000)")
    parser.add_argument("--max-workers", type=int, default=4,
                       help="Number of parallel upload threads (default: 4)")
    parser.add_argument("--checkpoint-file", type=str, default="logs/db_backup_checkpoint.json",
                       help="Path to checkpoint file")
    
    args = parser.parse_args()
    
    # Create backup instance
    backup = IncrementalDBBackup(
        chunk_size=args.chunk_size,
        max_workers=args.max_workers,
        checkpoint_file=args.checkpoint_file
    )
    
    try:
        backup.run_backup()
    except KeyboardInterrupt:
        logger.info("Backup interrupted by user")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 