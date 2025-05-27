# StoryDredge Cloud Setup Guide

## Quick Start: AWS S3 Backup Setup

This guide will help you set up cloud backup for your StoryDredge cache directory using AWS S3.

## Prerequisites

1. **AWS Account**: Sign up at [aws.amazon.com](https://aws.amazon.com)
2. **Python Environment**: StoryDredge virtual environment activated
3. **Current Status**: ~367 files downloaded and ready for backup

## Step 1: Install AWS CLI and Boto3

```bash
# Activate StoryDredge virtual environment
source src/venv/bin/activate

# Install AWS dependencies
pip install boto3 awscli
```

## Step 2: Configure AWS Credentials

### Option A: AWS CLI Configuration (Recommended)
```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: From your AWS IAM user
- **AWS Secret Access Key**: From your AWS IAM user  
- **Default region**: `us-east-1` (recommended)
- **Default output format**: `json`

### Option B: Environment Variables
```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Option C: IAM Role (for EC2 instances)
If running on AWS EC2, attach an IAM role with S3 permissions.

## Step 3: Create AWS IAM User (if needed)

1. Go to AWS Console → IAM → Users
2. Click "Create user"
3. Username: `storydredge-backup`
4. Attach policy: `AmazonS3FullAccess` (or create custom policy below)

### Custom IAM Policy (More Secure)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:GetBucketVersioning",
                "s3:PutBucketVersioning",
                "s3:PutBucketIntelligentTieringConfiguration"
            ],
            "Resource": [
                "arn:aws:s3:::storydredge-*",
                "arn:aws:s3:::storydredge-*/*"
            ]
        }
    ]
}
```

## Step 4: Test Your Setup

```bash
# Test AWS credentials
aws sts get-caller-identity

# Should return your AWS account info
```

## Step 5: Run Initial Backup

### Dry Run First (Recommended)
```bash
python scripts/sync_to_cloud.py --dry-run
```

This will show you what would be uploaded without actually doing it.

### Full Backup
```bash
python scripts/sync_to_cloud.py
```

Expected output:
```
2025-05-26 21:00:00 - cloud_sync - INFO - AWS S3 client initialized for region us-east-1
2025-05-26 21:00:01 - cloud_sync - INFO - Created bucket storydredge-raw-cache with versioning and intelligent tiering
2025-05-26 21:00:02 - cloud_sync - INFO - Found 367 files to sync
2025-05-26 21:00:03 - cloud_sync - INFO - Uploaded atlanta-constitution/1921/per_atlanta-constitution_1921-01-01_53_201.txt (45,234 bytes)
...
✅ Sync completed successfully!
Files synced: 367/367
Total size: 15,234,567 bytes
```

## Step 6: Verify Upload

```bash
# List bucket contents
python scripts/sync_to_cloud.py --list

# Or use AWS CLI
aws s3 ls s3://storydredge-raw-cache --recursive --human-readable
```

## Step 7: Set Up Automated Sync

### Option A: Modify Download Script
Add cloud sync to the download process for real-time backup.

### Option B: Cron Job
```bash
# Edit crontab
crontab -e

# Add line for hourly sync
0 * * * * cd /path/to/StoryDredge && source src/venv/bin/activate && python scripts/sync_to_cloud.py
```

### Option C: Manual Sync
Run sync manually whenever you want to backup new downloads.

## Cost Estimation

### Current Dataset (~15-20 GB)
- **S3 Storage**: $0.30-0.40/month
- **Upload Transfer**: $1.80 one-time
- **Download Transfer**: $1.80 per full download

### Intelligent Tiering Benefits
- Files automatically move to cheaper storage after 30 days
- 40-68% cost savings for infrequently accessed data
- No retrieval fees for frequent access tier

## Troubleshooting

### Common Issues

#### 1. "NoCredentialsError"
```bash
# Solution: Configure AWS credentials
aws configure
```

#### 2. "BucketAlreadyExists"
```bash
# Solution: Use a unique bucket name
python scripts/sync_to_cloud.py --bucket storydredge-raw-cache-yourname
```

#### 3. "AccessDenied"
```bash
# Solution: Check IAM permissions
aws iam get-user-policy --user-name storydredge-backup --policy-name S3Access
```

#### 4. "RegionMismatch"
```bash
# Solution: Specify correct region
python scripts/sync_to_cloud.py --region us-west-2
```

### Verification Commands

```bash
# Check AWS credentials
aws sts get-caller-identity

# List all S3 buckets
aws s3 ls

# Check bucket policy
aws s3api get-bucket-policy --bucket storydredge-raw-cache

# Monitor costs
aws ce get-cost-and-usage --time-period Start=2025-05-01,End=2025-05-31 --granularity MONTHLY --metrics BlendedCost
```

## Security Best Practices

1. **Use IAM roles** instead of access keys when possible
2. **Enable MFA** on your AWS account
3. **Rotate access keys** regularly
4. **Use least privilege** IAM policies
5. **Enable CloudTrail** for audit logging
6. **Set up billing alerts** to monitor costs

## Next Steps

1. **Set up output database backup** (processed articles)
2. **Configure automated pipeline** in AWS Lambda
3. **Implement monitoring** with CloudWatch
4. **Plan data retention** policies
5. **Test disaster recovery** procedures

## Support

- **AWS Documentation**: [docs.aws.amazon.com](https://docs.aws.amazon.com)
- **Boto3 Documentation**: [boto3.amazonaws.com](https://boto3.amazonaws.com)
- **StoryDredge Issues**: Create issue in project repository

## Current Status

✅ **Download Process**: Running successfully (PID 30303)  
✅ **Files Downloaded**: ~367 newspaper issues  
✅ **Cloud Sync Script**: Ready for use  
⏳ **Next**: Configure AWS credentials and run first backup 