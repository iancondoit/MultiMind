# StoryDredge Database Backup System

## Overview

The StoryDredge Database Backup System provides automated, incremental backup of the PostgreSQL database to AWS S3. This system is designed to run safely alongside the production pipeline without interference, ensuring complete data redundancy and recovery capabilities.

## Table of Contents

1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Usage](#usage)
5. [Configuration](#configuration)
6. [Monitoring & Logs](#monitoring--logs)
7. [Recovery Procedures](#recovery-procedures)
8. [Troubleshooting](#troubleshooting)
9. [Performance Tuning](#performance-tuning)
10. [Security Considerations](#security-considerations)

## Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  PostgreSQL     │    │  Backup Script  │    │   AWS S3        │
│  Database       │───▶│  (Python)       │───▶│   Bucket        │
│  (Port 5433)    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Checkpoint     │
                       │  System         │
                       │  (JSON)         │
                       └─────────────────┘
```

### Key Features

- **Incremental Backups**: Only backs up new articles since the last run
- **Parallel Processing**: Configurable worker threads for concurrent uploads
- **Resume Capability**: Checkpoint system allows resuming interrupted backups
- **Safe Concurrency**: Runs alongside production pipeline without conflicts
- **Structured Storage**: JSON chunks with metadata for easy restoration
- **Comprehensive Logging**: Detailed logs for monitoring and debugging

## Prerequisites

### System Requirements

- Python 3.8+
- PostgreSQL database (running on port 5433)
- AWS account with S3 access
- Required Python packages (see Installation)

### Database Schema

The backup system expects the following table structure:

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    publication TEXT NOT NULL,
    source_url TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    quality_score FLOAT NOT NULL,
    newsworthiness_score FLOAT NOT NULL,
    unusualness_score FLOAT NOT NULL
);
```

### AWS Configuration

- AWS credentials configured (via AWS CLI, environment variables, or IAM roles)
- S3 bucket permissions for read/write operations
- Sufficient S3 storage quota

## Installation & Setup

### 1. Install Dependencies

```bash
# Install required Python packages
pip install boto3 psycopg2-binary loguru

# Optional: Install AWS CLI for bucket management
pip install awscli
```

### 2. Configure AWS Credentials

Choose one of the following methods:

**Method A: Environment Variables**
```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**Method B: AWS CLI Configuration**
```bash
aws configure
```

**Method C: IAM Roles** (recommended for EC2/ECS deployments)
- Attach appropriate IAM role to your instance

### 3. Database Connection

Ensure your database is accessible with the following default configuration:
- Host: `localhost`
- Port: `5433`
- Database: `storymap`
- User: `postgres`
- Password: `postgres`

### 4. Directory Structure

Ensure the following directories exist:
```
StoryDredge/
├── scripts/
│   └── incremental_db_backup.py
├── logs/
│   └── (backup logs will be created here)
└── docs/
    └── DATABASE_BACKUP_GUIDE.md
```

## Usage

### Basic Usage

```bash
# Run backup with default settings
python scripts/incremental_db_backup.py

# Run with custom chunk size and workers
python scripts/incremental_db_backup.py --chunk-size 1000 --max-workers 4

# Run with custom checkpoint file
python scripts/incremental_db_backup.py --checkpoint-file logs/custom_checkpoint.json
```

### Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--chunk-size` | 1000 | Number of articles per backup chunk |
| `--max-workers` | 4 | Number of parallel upload threads |
| `--checkpoint-file` | `logs/db_backup_checkpoint.json` | Path to checkpoint file |

### Running in Background

```bash
# Run in background with nohup
nohup python scripts/incremental_db_backup.py --chunk-size 1000 --max-workers 4 > backup.out 2>&1 &

# Check if running
ps aux | grep incremental_db_backup

# Stop background process
pkill -f incremental_db_backup
```

### Scheduling with Cron

Add to crontab for automated backups:

```bash
# Run backup every 6 hours
0 */6 * * * cd /path/to/StoryDredge && python scripts/incremental_db_backup.py --chunk-size 1000 --max-workers 4

# Run backup daily at 2 AM
0 2 * * * cd /path/to/StoryDredge && python scripts/incremental_db_backup.py --chunk-size 2000 --max-workers 6
```

## Configuration

### Database Configuration

Modify the database configuration in `scripts/incremental_db_backup.py`:

```python
self.db_config = {
    'host': 'localhost',
    'port': '5433',
    'database': 'storymap',
    'user': 'postgres',
    'password': 'postgres'
}
```

### S3 Configuration

Modify the S3 configuration:

```python
self.bucket_name = "storydredge-processed-output"
self.backup_prefix = "database_backups"
```

### Performance Tuning

| Parameter | Recommended Values | Impact |
|-----------|-------------------|---------|
| `chunk_size` | 500-2000 | Larger chunks = fewer files, more memory usage |
| `max_workers` | 2-8 | More workers = faster uploads, more CPU/network usage |

## Monitoring & Logs

### Log Files

Backup logs are stored in the `logs/` directory with the following naming convention:
```
logs/incremental_db_backup_YYYYMMDD_HHMMSS.log
```

### Log Levels

- **INFO**: Normal operation, progress updates
- **ERROR**: Failed operations, connection issues
- **DEBUG**: Detailed operation information

### Key Log Messages

```bash
# Successful start
🚀 Starting incremental database backup...

# Progress updates
📈 Progress: 10 chunks, 10,000 articles (193.5 articles/sec)

# Successful completion
🎉 Backup completed successfully!

# Error conditions
ERROR | Failed to get articles chunk: connection error
```

### Monitoring Commands

```bash
# Follow live backup progress
tail -f logs/incremental_db_backup_*.log

# Check recent backup status
grep "Progress\|completed\|ERROR" logs/incremental_db_backup_*.log | tail -20

# Get backup statistics
grep "Final Statistics" logs/incremental_db_backup_*.log | tail -1
```

## Recovery Procedures

### S3 Backup Structure

Backups are stored in S3 with the following structure:

```
s3://storydredge-processed-output/
├── database_backups/
│   ├── chunks/
│   │   ├── chunk_000001_20250527_000750.json
│   │   ├── chunk_000002_20250527_000750.json
│   │   └── ...
│   └── manifests/
│       └── backup_manifest_20250527_001234.json
```

### Restoring from Backup

#### 1. Download Backup Chunks

```bash
# Download all chunks for a specific backup
aws s3 sync s3://storydredge-processed-output/database_backups/chunks/ ./restore_chunks/

# Download specific manifest
aws s3 cp s3://storydredge-processed-output/database_backups/manifests/backup_manifest_20250527_001234.json ./
```

#### 2. Restore to Database

```python
import json
import psycopg2
from pathlib import Path

def restore_from_chunks(chunk_directory, db_config):
    """Restore database from backup chunks."""
    
    # Connect to database
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()
    
    # Clear existing data (if needed)
    cursor.execute("TRUNCATE TABLE articles RESTART IDENTITY")
    
    # Process each chunk
    chunk_files = sorted(Path(chunk_directory).glob("chunk_*.json"))
    
    for chunk_file in chunk_files:
        with open(chunk_file, 'r') as f:
            articles = json.load(f)
        
        # Insert articles
        for article in articles:
            cursor.execute("""
                INSERT INTO articles (title, content, publication, source_url, 
                                    timestamp, quality_score, newsworthiness_score, unusualness_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                article['title'], article['content'], article['publication'],
                article['source_url'], article['timestamp'], article['quality_score'],
                article['newsworthiness_score'], article['unusualness_score']
            ))
    
    conn.commit()
    conn.close()
    print(f"Restored {len(chunk_files)} chunks to database")

# Usage
db_config = {
    'host': 'localhost',
    'port': '5433',
    'database': 'storymap',
    'user': 'postgres',
    'password': 'postgres'
}

restore_from_chunks('./restore_chunks/', db_config)
```

#### 3. Verify Restoration

```sql
-- Check article count
SELECT COUNT(*) FROM articles;

-- Check data integrity
SELECT 
    MIN(id) as min_id,
    MAX(id) as max_id,
    COUNT(*) as total_articles,
    AVG(quality_score) as avg_quality
FROM articles;
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Error**: `connection to server at "localhost" (::1), port 5432 failed`

**Solution**: 
- Verify PostgreSQL is running on port 5433
- Check database credentials
- Ensure database accepts connections

```bash
# Test database connection
psql -h localhost -p 5433 -U postgres -d storymap
```

#### 2. S3 Permission Errors

**Error**: `An error occurred (AccessDenied) when calling the PutObject operation`

**Solution**:
- Verify AWS credentials are configured
- Check S3 bucket permissions
- Ensure bucket exists in correct region

```bash
# Test S3 access
aws s3 ls s3://storydredge-processed-output/
```

#### 3. Memory Issues

**Error**: `MemoryError` or system slowdown

**Solution**:
- Reduce `chunk_size` parameter
- Reduce `max_workers` parameter
- Monitor system memory usage

#### 4. Network Timeouts

**Error**: `ReadTimeoutError` or `ConnectionError`

**Solution**:
- Check network connectivity
- Reduce `max_workers` to decrease concurrent connections
- Implement retry logic (already included in script)

### Debugging Steps

1. **Check Process Status**
   ```bash
   ps aux | grep incremental_db_backup
   ```

2. **Monitor Resource Usage**
   ```bash
   top -p $(pgrep -f incremental_db_backup)
   ```

3. **Check Database Connectivity**
   ```bash
   python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port='5433', database='storymap', user='postgres', password='postgres'); print('Connected successfully')"
   ```

4. **Test S3 Access**
   ```bash
   python -c "import boto3; s3 = boto3.client('s3'); print(s3.list_buckets())"
   ```

## Performance Tuning

### Optimal Settings by Environment

#### Development Environment
```bash
python scripts/incremental_db_backup.py --chunk-size 500 --max-workers 2
```

#### Production Environment (High-Performance)
```bash
python scripts/incremental_db_backup.py --chunk-size 2000 --max-workers 8
```

#### Production Environment (Conservative)
```bash
python scripts/incremental_db_backup.py --chunk-size 1000 --max-workers 4
```

### Performance Metrics

Monitor these metrics for optimization:

- **Upload Speed**: Target 100-300 articles/second
- **Memory Usage**: Should not exceed 50% of available RAM
- **Network Bandwidth**: Monitor S3 upload speeds
- **Database Load**: Ensure minimal impact on production queries

### Scaling Considerations

For large databases (>1M articles):

1. **Increase Chunk Size**: Use 2000-5000 articles per chunk
2. **Parallel Processing**: Use 6-12 workers on high-performance systems
3. **Scheduled Backups**: Run during low-traffic periods
4. **Regional S3**: Use S3 bucket in same region as database

## Security Considerations

### Database Security

- Use dedicated backup user with minimal permissions
- Encrypt database connections (SSL/TLS)
- Rotate database passwords regularly

```sql
-- Create dedicated backup user
CREATE USER backup_user WITH PASSWORD 'secure_password';
GRANT SELECT ON articles TO backup_user;
```

### S3 Security

- Use IAM roles instead of access keys when possible
- Enable S3 bucket encryption
- Implement bucket policies for access control
- Enable S3 access logging

### Data Protection

- Backup data contains sensitive information
- Implement data retention policies
- Consider data anonymization for non-production backups
- Ensure compliance with data protection regulations

## Best Practices

### Operational Best Practices

1. **Regular Testing**: Test backup and restore procedures monthly
2. **Monitoring**: Set up alerts for backup failures
3. **Documentation**: Keep this guide updated with any changes
4. **Validation**: Verify backup integrity regularly

### Development Best Practices

1. **Error Handling**: All database and S3 operations include proper error handling
2. **Logging**: Comprehensive logging for debugging and monitoring
3. **Configuration**: Externalize configuration for different environments
4. **Testing**: Unit tests for critical backup functions

### Maintenance Schedule

- **Daily**: Monitor backup logs for errors
- **Weekly**: Verify backup completion and file counts
- **Monthly**: Test restore procedures
- **Quarterly**: Review and optimize performance settings

## Support and Maintenance

### Getting Help

1. Check this documentation first
2. Review log files for specific error messages
3. Test individual components (database, S3) separately
4. Consult AWS S3 and PostgreSQL documentation

### Updating the System

When updating the backup system:

1. Test changes in development environment
2. Backup current checkpoint files
3. Update during low-traffic periods
4. Monitor first backup run after updates

### Version History

- **v1.0**: Initial implementation with basic incremental backup
- **v1.1**: Added S3 bucket auto-creation and improved error handling
- **v1.2**: Enhanced logging and performance monitoring

---

**Last Updated**: May 27, 2025  
**Version**: 1.2  
**Maintainer**: StoryDredge Development Team 