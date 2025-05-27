#!/usr/bin/env python3
"""
Ultra-Fast Cloud Backup V2 - Optimized for StoryDredge

This script provides lightning-fast, resumable backup of newspaper files to AWS S3
with advanced optimizations for reliability and performance.

Key improvements over V1:
1. Extended timeout configurations for large files
2. Smart concurrency with connection pooling
3. Exponential backoff with jitter for retries
4. Resumable uploads (skips already uploaded files)
5. Better progress tracking and error handling
6. Optimized batch processing by year
"""

import os
import sys
import boto3
import hashlib
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from botocore.config import Config
from botocore.exceptions import ClientError, ReadTimeoutError, ConnectTimeoutError
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ultra_backup_v2.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ultra_backup_v2')

class OptimizedCloudBackup:
    def __init__(self):
        # Optimized AWS configuration with extended timeouts
        self.config = Config(
            region_name='us-east-1',
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'
            },
            # Extended timeouts for large files
            read_timeout=300,  # 5 minutes
            connect_timeout=60,  # 1 minute
            max_pool_connections=50  # Increased connection pool
        )
        
        self.s3_client = boto3.client('s3', config=self.config)
        self.bucket_name = 'storydredge-raw-cache'
        self.cache_dir = Path('cache')
        
        # Thread-safe progress tracking
        self.progress_lock = threading.Lock()
        self.uploaded_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        
        # Cache for already uploaded files
        self.uploaded_files: Set[str] = set()
        
        logger.info("Optimized backup system initialized")
    
    def get_uploaded_files(self) -> Set[str]:
        """Get set of files already uploaded to S3."""
        logger.info("Scanning S3 bucket for existing files...")
        uploaded = set()
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name, Prefix='atlanta-constitution/')
            
            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        # Extract filename from S3 key
                        key = obj['Key']
                        if key.endswith('.txt'):
                            filename = Path(key).name
                            uploaded.add(filename)
            
            logger.info(f"Found {len(uploaded)} files already uploaded to S3")
            return uploaded
            
        except Exception as e:
            logger.error(f"Error scanning S3 bucket: {e}")
            return set()
    
    def organize_files_by_year(self) -> Dict[str, List[Path]]:
        """Organize cache files by year for efficient processing."""
        logger.info("Organizing files by year...")
        files_by_year = defaultdict(list)
        
        if not self.cache_dir.exists():
            logger.error(f"Cache directory {self.cache_dir} does not exist")
            return {}
        
        # Find all .txt files in cache
        txt_files = list(self.cache_dir.glob('**/*.txt'))
        logger.info(f"Found {len(txt_files)} total files in cache")
        
        for file_path in txt_files:
            try:
                # Extract year from filename: per_atlanta-constitution_YYYY-MM-DD_...
                filename = file_path.name
                if filename.startswith('per_atlanta-constitution_'):
                    year_part = filename.split('_')[1]  # YYYY-MM-DD
                    year = year_part.split('-')[0]  # YYYY
                    files_by_year[year].append(file_path)
                else:
                    logger.warning(f"Unexpected filename format: {filename}")
            except (IndexError, ValueError) as e:
                logger.warning(f"Could not extract year from {filename}: {e}")
        
        # Sort years and log summary
        sorted_years = sorted(files_by_year.keys())
        for year in sorted_years:
            logger.info(f"Year {year}: {len(files_by_year[year])} files")
        
        return dict(files_by_year)
    
    def upload_file_with_retry(self, file_path: Path, s3_key: str, max_retries: int = 3) -> bool:
        """Upload a single file with exponential backoff retry logic."""
        filename = file_path.name
        
        # Skip if already uploaded
        if filename in self.uploaded_files:
            with self.progress_lock:
                self.skipped_count += 1
            return True
        
        for attempt in range(max_retries):
            try:
                # Calculate file size for progress tracking
                file_size = file_path.stat().st_size
                
                # Upload with metadata
                extra_args = {
                    'Metadata': {
                        'source': 'storydredge-fetcher',
                        'newspaper': 'atlanta-constitution',
                        'upload-time': datetime.now().isoformat()
                    }
                }
                
                start_time = time.time()
                self.s3_client.upload_file(
                    str(file_path),
                    self.bucket_name,
                    s3_key,
                    ExtraArgs=extra_args
                )
                
                upload_time = time.time() - start_time
                speed_mbps = (file_size / 1024 / 1024) / upload_time if upload_time > 0 else 0
                
                # Success - update progress
                with self.progress_lock:
                    self.uploaded_count += 1
                    self.uploaded_files.add(filename)
                
                logger.info(f"✅ Uploaded {filename} ({file_size:,} bytes, {speed_mbps:.1f} MB/s)")
                return True
                
            except (ClientError, ReadTimeoutError, ConnectTimeoutError) as e:
                wait_time = (2 ** attempt) + random.uniform(0, 1)  # Exponential backoff with jitter
                
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️  Upload failed for {filename} (attempt {attempt + 1}): {e}. Retrying in {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"❌ Failed to upload {filename} after {max_retries} attempts: {e}")
                    with self.progress_lock:
                        self.failed_count += 1
                    return False
            
            except Exception as e:
                logger.error(f"❌ Unexpected error uploading {filename}: {e}")
                with self.progress_lock:
                    self.failed_count += 1
                return False
        
        return False
    
    def upload_year_batch(self, year: str, files: List[Path]) -> Dict[str, int]:
        """Upload all files for a specific year using optimized concurrency."""
        logger.info(f"🚀 Starting upload for year {year} ({len(files)} files)")
        
        # Filter out already uploaded files
        files_to_upload = [f for f in files if f.name not in self.uploaded_files]
        
        if not files_to_upload:
            logger.info(f"✅ All files for year {year} already uploaded, skipping")
            return {'uploaded': 0, 'skipped': len(files), 'failed': 0}
        
        logger.info(f"📤 Uploading {len(files_to_upload)} new files for year {year}")
        
        # Use moderate concurrency to avoid overwhelming AWS
        max_workers = min(16, len(files_to_upload))  # Reduced from 32 for stability
        
        results = {'uploaded': 0, 'skipped': 0, 'failed': 0}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all upload tasks
            future_to_file = {}
            for file_path in files_to_upload:
                s3_key = f"atlanta-constitution/{year}/{file_path.name}"
                future = executor.submit(self.upload_file_with_retry, file_path, s3_key)
                future_to_file[future] = file_path
            
            # Process completed uploads
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        results['uploaded'] += 1
                    else:
                        results['failed'] += 1
                except Exception as e:
                    logger.error(f"❌ Task failed for {file_path.name}: {e}")
                    results['failed'] += 1
        
        logger.info(f"✅ Year {year} complete: {results['uploaded']} uploaded, {results['failed']} failed")
        return results
    
    def print_progress(self, total_files: int):
        """Print current progress statistics."""
        with self.progress_lock:
            completed = self.uploaded_count + self.skipped_count + self.failed_count
            percent = (completed / total_files * 100) if total_files > 0 else 0
            
            print(f"\n📊 Progress: {completed:,}/{total_files:,} files ({percent:.1f}%)")
            print(f"   ✅ Uploaded: {self.uploaded_count:,}")
            print(f"   ⏭️  Skipped: {self.skipped_count:,}")
            print(f"   ❌ Failed: {self.failed_count:,}")
    
    def run_backup(self):
        """Execute the complete backup process."""
        start_time = time.time()
        logger.info("🚀 Starting Ultra-Fast Cloud Backup V2")
        
        # Get list of already uploaded files
        self.uploaded_files = self.get_uploaded_files()
        
        # Organize files by year
        files_by_year = self.organize_files_by_year()
        
        if not files_by_year:
            logger.error("❌ No files found to backup")
            return
        
        # Calculate totals
        total_files = sum(len(files) for files in files_by_year.values())
        logger.info(f"📁 Total files to process: {total_files:,}")
        logger.info(f"📤 Files already uploaded: {len(self.uploaded_files):,}")
        logger.info(f"🆕 New files to upload: {total_files - len(self.uploaded_files):,}")
        
        # Process each year
        sorted_years = sorted(files_by_year.keys())
        
        for i, year in enumerate(sorted_years, 1):
            logger.info(f"\n📅 Processing year {year} ({i}/{len(sorted_years)})")
            
            year_results = self.upload_year_batch(year, files_by_year[year])
            
            # Print progress after each year
            self.print_progress(total_files)
            
            # Brief pause between years to avoid overwhelming AWS
            if i < len(sorted_years):
                time.sleep(2)
        
        # Final summary
        elapsed_time = time.time() - start_time
        
        with self.progress_lock:
            total_processed = self.uploaded_count + self.skipped_count + self.failed_count
            upload_rate = self.uploaded_count / (elapsed_time / 60) if elapsed_time > 0 else 0
        
        logger.info(f"\n🎉 Backup Complete!")
        logger.info(f"⏱️  Total time: {elapsed_time/60:.1f} minutes")
        logger.info(f"📤 Files uploaded: {self.uploaded_count:,}")
        logger.info(f"⏭️  Files skipped: {self.skipped_count:,}")
        logger.info(f"❌ Files failed: {self.failed_count:,}")
        logger.info(f"🚀 Upload rate: {upload_rate:.1f} files/minute")
        
        if self.failed_count > 0:
            logger.warning(f"⚠️  {self.failed_count} files failed to upload. Check logs for details.")

def main():
    """Main entry point."""
    try:
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        # Run the backup
        backup = OptimizedCloudBackup()
        backup.run_backup()
        
    except KeyboardInterrupt:
        logger.info("🛑 Backup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Backup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 