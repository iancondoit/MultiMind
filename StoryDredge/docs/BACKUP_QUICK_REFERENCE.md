# Database Backup Quick Reference

## 🚀 Quick Start

```bash
# Install dependencies
pip install boto3 psycopg2-binary loguru

# Configure AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# Run backup
python scripts/incremental_db_backup.py --chunk-size 1000 --max-workers 4
```

## 📋 Common Commands

### Start Backup
```bash
# Basic backup
python scripts/incremental_db_backup.py

# High-performance backup
python scripts/incremental_db_backup.py --chunk-size 2000 --max-workers 8

# Background backup
nohup python scripts/incremental_db_backup.py --chunk-size 1000 --max-workers 4 > backup.out 2>&1 &
```

### Monitor Progress
```bash
# Follow live progress
tail -f logs/incremental_db_backup_*.log

# Check if running
ps aux | grep incremental_db_backup

# Get latest status
grep "Progress\|completed\|ERROR" logs/incremental_db_backup_*.log | tail -10
```

### Stop Backup
```bash
# Stop gracefully (Ctrl+C if in foreground)
pkill -f incremental_db_backup
```

## 🔧 Configuration

### Database Settings
```python
# In scripts/incremental_db_backup.py
self.db_config = {
    'host': 'localhost',
    'port': '5433',        # StoryDredge uses 5433, not default 5432
    'database': 'storymap',
    'user': 'postgres',
    'password': 'postgres'
}
```

### S3 Settings
```python
self.bucket_name = "storydredge-processed-output"
self.backup_prefix = "database_backups"
```

## 📊 Performance Guidelines

| Environment | Chunk Size | Workers | Expected Speed |
|-------------|------------|---------|----------------|
| Development | 500 | 2 | 50-100 articles/sec |
| Production | 1000-2000 | 4-8 | 150-300 articles/sec |
| High-Load | 2000+ | 8+ | 300+ articles/sec |

## 🚨 Troubleshooting

### Database Connection Issues
```bash
# Test connection
psql -h localhost -p 5433 -U postgres -d storymap

# Check if PostgreSQL is running
ps aux | grep postgres
```

### S3 Access Issues
```bash
# Test S3 access
aws s3 ls s3://storydredge-processed-output/

# Check credentials
aws sts get-caller-identity
```

### Memory Issues
- Reduce `--chunk-size` to 500 or lower
- Reduce `--max-workers` to 2
- Monitor with `top` or `htop`

## 📁 File Locations

```
StoryDredge/
├── scripts/incremental_db_backup.py    # Main backup script
├── logs/incremental_db_backup_*.log    # Backup logs
├── logs/db_backup_checkpoint.json      # Resume checkpoint
└── docs/DATABASE_BACKUP_GUIDE.md       # Full documentation
```

## 🔄 Restore Process

### 1. Download from S3
```bash
aws s3 sync s3://storydredge-processed-output/database_backups/chunks/ ./restore/
```

### 2. Restore to Database
```python
# See full restore script in DATABASE_BACKUP_GUIDE.md
python restore_script.py
```

## 📅 Automation

### Cron Schedule
```bash
# Every 6 hours
0 */6 * * * cd /path/to/StoryDredge && python scripts/incremental_db_backup.py

# Daily at 2 AM
0 2 * * * cd /path/to/StoryDredge && python scripts/incremental_db_backup.py --chunk-size 2000
```

## 🔍 Log Messages

| Message | Meaning |
|---------|---------|
| `🚀 Starting incremental database backup...` | Backup started |
| `📊 Database Status: Total articles in DB: X` | Found X articles to backup |
| `📦 Will create X chunks` | Backup plan created |
| `✅ Uploaded chunk X: Y articles` | Chunk successfully uploaded |
| `📈 Progress: X chunks, Y articles (Z articles/sec)` | Progress update |
| `🎉 Backup completed successfully!` | Backup finished |
| `ERROR` | Something went wrong - check logs |

## ⚡ Emergency Procedures

### Stop All Backups
```bash
pkill -f incremental_db_backup
```

### Check System Resources
```bash
# Memory usage
free -h

# Disk space
df -h

# Network connections
netstat -an | grep 5433
```

### Reset Checkpoint (Start Fresh)
```bash
rm logs/db_backup_checkpoint.json
```

---

**For detailed information, see [DATABASE_BACKUP_GUIDE.md](DATABASE_BACKUP_GUIDE.md)** 