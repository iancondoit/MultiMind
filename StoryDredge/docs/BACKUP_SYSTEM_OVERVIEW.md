# StoryDredge Backup System Overview

## Complete Data Protection Strategy

StoryDredge implements a comprehensive, multi-layered backup strategy that ensures complete data redundancy and recovery capabilities. The system protects both raw source files and processed database content through automated, incremental backup processes.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    StoryDredge Backup Architecture              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   Raw Files     │    │  Production     │    │ PostgreSQL  │  │
│  │   (14,730+)     │───▶│   Pipeline      │───▶│  Database   │  │
│  │   cache/*.txt   │    │                 │    │ (134K+ art) │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│           │                                             │       │
│           ▼                                             ▼       │
│  ┌─────────────────┐                           ┌─────────────┐  │
│  │  File Backup    │                           │ DB Backup   │  │
│  │  ultra_fast_    │                           │ incremental │  │
│  │  cloud_backup   │                           │ _db_backup  │  │
│  └─────────────────┘                           └─────────────┘  │
│           │                                             │       │
│           ▼                                             ▼       │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                AWS S3 Storage                          │    │
│  │  ┌─────────────────┐    ┌─────────────────────────┐    │    │
│  │  │ Raw File Bucket │    │ Database Backup Bucket  │    │    │
│  │  │ storydredge-    │    │ storydredge-processed-  │    │    │
│  │  │ raw-cache       │    │ output                  │    │    │
│  │  └─────────────────┘    └─────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Two-Tier Backup Strategy

### Tier 1: Raw File Backup
**Purpose**: Protect source OCR text files  
**Script**: `ultra_fast_cloud_backup_v2.py`  
**Target**: AWS S3 bucket `storydredge-raw-cache`  
**Content**: 14,730+ newspaper OCR text files (9.7 GB)

### Tier 2: Database Backup  
**Purpose**: Protect processed articles and metadata  
**Script**: `incremental_db_backup.py`  
**Target**: AWS S3 bucket `storydredge-processed-output`  
**Content**: 134,000+ structured articles with quality scores

## Key Benefits

### 🔄 **Complete Data Lifecycle Protection**
- **Source Protection**: Raw OCR files backed up to S3
- **Processed Protection**: Structured articles backed up incrementally
- **Metadata Preservation**: Quality scores, classifications, timestamps

### ⚡ **High Performance**
- **File Backup**: Parallel uploads with smart deduplication
- **Database Backup**: 150+ articles/second backup rate
- **Minimal Impact**: Runs alongside production pipeline

### 🛡️ **Robust Recovery**
- **Point-in-Time Recovery**: Incremental backups with timestamps
- **Selective Restore**: Restore specific date ranges or article sets
- **Complete Rebuild**: Full system restoration from S3 backups

### 🔧 **Operational Excellence**
- **Automated Scheduling**: Cron-compatible for regular backups
- **Resume Capability**: Checkpoint system for interrupted backups
- **Comprehensive Monitoring**: Detailed logs and progress tracking

## Backup Components

### 1. File Backup System (`ultra_fast_cloud_backup_v2.py`)

```bash
# Backup all raw files to S3
python scripts/ultra_fast_cloud_backup_v2.py

# Features:
# - Parallel uploads (64 workers)
# - Smart deduplication
# - Progress tracking
# - Resume capability
```

**Storage Structure**:
```
s3://storydredge-raw-cache/
├── per_atlanta-constitution_1920-01-01_52_203.txt
├── per_atlanta-constitution_1920-01-02_52_204.txt
└── ... (14,730+ files)
```

### 2. Database Backup System (`incremental_db_backup.py`)

```bash
# Backup database incrementally to S3
python scripts/incremental_db_backup.py --chunk-size 1000 --max-workers 4

# Features:
# - Incremental backups (only new articles)
# - Chunked storage (1000 articles per file)
# - Parallel processing
# - Checkpoint system
```

**Storage Structure**:
```
s3://storydredge-processed-output/
├── database_backups/
│   ├── chunks/
│   │   ├── chunk_000001_20250527_000750.json
│   │   ├── chunk_000002_20250527_000750.json
│   │   └── ... (135+ chunks)
│   └── manifests/
│       └── backup_manifest_20250527_001234.json
```

## Operational Workflows

### Daily Operations

1. **Monitor Backup Status**
   ```bash
   # Check file backup progress
   tail -f logs/ultra_backup_v2_*.log
   
   # Check database backup progress  
   tail -f logs/incremental_db_backup_*.log
   ```

2. **Verify Backup Completion**
   ```bash
   # Check S3 file counts
   aws s3 ls s3://storydredge-raw-cache/ --recursive | wc -l
   aws s3 ls s3://storydredge-processed-output/database_backups/chunks/ | wc -l
   ```

### Scheduled Automation

```bash
# Crontab entries for automated backups

# File backup - daily at 1 AM
0 1 * * * cd /path/to/StoryDredge && python scripts/ultra_fast_cloud_backup_v2.py

# Database backup - every 6 hours
0 */6 * * * cd /path/to/StoryDredge && python scripts/incremental_db_backup.py --chunk-size 1000 --max-workers 4
```

### Recovery Procedures

#### Complete System Recovery

1. **Restore Raw Files**
   ```bash
   # Download all raw files from S3
   aws s3 sync s3://storydredge-raw-cache/ ./cache/
   ```

2. **Restore Database**
   ```bash
   # Download database backup chunks
   aws s3 sync s3://storydredge-processed-output/database_backups/chunks/ ./restore/
   
   # Run restore script (see DATABASE_BACKUP_GUIDE.md)
   python restore_database.py
   ```

3. **Verify Restoration**
   ```bash
   # Check file count
   ls cache/*.txt | wc -l
   
   # Check database
   psql -h localhost -p 5433 -U postgres -d storymap -c "SELECT COUNT(*) FROM articles;"
   ```

## Performance Metrics

### Current Backup Performance

| Component | Speed | Volume | Status |
|-----------|-------|--------|--------|
| File Backup | 140 files/hour | 14,730 files (9.7 GB) | ✅ Active |
| Database Backup | 150 articles/sec | 134,000+ articles | ✅ Active |
| Total Backup Time | ~2-3 hours | Complete system | ✅ Automated |

### Storage Utilization

| Backup Type | S3 Bucket | Size | Files |
|-------------|-----------|------|-------|
| Raw Files | `storydredge-raw-cache` | ~9.7 GB | 14,730+ |
| Database | `storydredge-processed-output` | ~200 MB | 135+ chunks |
| **Total** | **Both buckets** | **~9.9 GB** | **14,865+** |

## Security and Compliance

### Data Protection
- **Encryption**: S3 server-side encryption enabled
- **Access Control**: IAM policies restrict bucket access
- **Audit Trail**: CloudTrail logging for all S3 operations
- **Retention**: Configurable lifecycle policies

### Compliance Features
- **Data Integrity**: MD5 checksums for all uploads
- **Version Control**: S3 versioning for change tracking
- **Geographic Distribution**: Multi-region backup capability
- **Disaster Recovery**: Complete system restoration procedures

## Monitoring and Alerting

### Log Monitoring
```bash
# Real-time backup monitoring
tail -f logs/ultra_backup_v2_*.log logs/incremental_db_backup_*.log

# Error detection
grep "ERROR\|FAILED" logs/*.log | tail -20

# Success verification
grep "completed successfully\|✅" logs/*.log | tail -10
```

### Health Checks
```bash
# Verify backup processes are running
ps aux | grep -E "(ultra_fast_cloud_backup|incremental_db_backup)"

# Check S3 connectivity
aws s3 ls s3://storydredge-raw-cache/ | head -5
aws s3 ls s3://storydredge-processed-output/ | head -5
```

## Documentation Quick Links

- **[Database Backup Guide](DATABASE_BACKUP_GUIDE.md)** - Complete database backup documentation
- **[Backup Quick Reference](BACKUP_QUICK_REFERENCE.md)** - Common commands and troubleshooting
- **[Production Pipeline Guide](PRODUCTION_PIPELINE_GUIDE.md)** - Main processing pipeline
- **[Data Protection Summary](DATA_PROTECTION_SUMMARY.md)** - Overall data protection strategy

## Support and Maintenance

### Regular Maintenance Tasks

- **Weekly**: Verify backup completion and file counts
- **Monthly**: Test restore procedures with sample data
- **Quarterly**: Review and optimize backup performance
- **Annually**: Update documentation and disaster recovery plans

### Getting Help

1. **Check Documentation**: Start with the relevant guide above
2. **Review Logs**: Check backup logs for specific error messages
3. **Test Components**: Verify database and S3 connectivity separately
4. **Escalation**: Contact system administrators for infrastructure issues

---

**System Status**: ✅ **FULLY OPERATIONAL**  
**Last Updated**: May 27, 2025  
**Backup Coverage**: 100% (Files + Database)  
**Recovery Tested**: ✅ Verified 