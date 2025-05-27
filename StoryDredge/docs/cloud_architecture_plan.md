# StoryDredge Cloud Architecture Plan

## Overview
This document outlines the cloud architecture for StoryDredge, including backup strategies and the eventual full cloud deployment.

## Architecture Components

### 1. Raw Data Storage (Input Side)
**S3 Bucket: `storydredge-raw-cache`**
- **Purpose**: Mirror of local `cache/` directory
- **Structure**: 
  ```
  storydredge-raw-cache/
  ├── atlanta-constitution/
  │   ├── 1920/
  │   │   ├── per_atlanta-constitution_1920-01-01_52_201.txt
  │   │   └── ...
  │   ├── 1921/
  │   └── ...
  ├── other-newspapers/
  └── metadata/
      └── download_logs/
  ```
- **Storage Class**: S3 Intelligent Tiering
- **Versioning**: Enabled
- **Lifecycle**: Transition to IA after 30 days, Glacier after 90 days

### 2. Processed Data Storage (Output Side)
**S3 Bucket: `storydredge-processed-data`**
- **Purpose**: Structured output from StoryDredge pipeline
- **Structure**:
  ```
  storydredge-processed-data/
  ├── articles/
  │   ├── year=1920/
  │   │   ├── month=01/
  │   │   │   └── classified_articles.parquet
  │   │   └── ...
  │   └── ...
  ├── classifications/
  ├── extractions/
  └── reports/
  ```

**DynamoDB Table: `storydredge-articles`**
- **Purpose**: Searchable metadata and article index
- **Schema**:
  ```
  Primary Key: article_id (String)
  Sort Key: publication_date (String)
  Attributes:
  - newspaper_name
  - classification
  - extracted_entities
  - s3_location
  - processing_status
  - created_at
  - updated_at
  ```

### 3. Backup Strategy

#### Immediate Setup (Phase 1)
1. **AWS CLI Configuration**
2. **S3 Bucket Creation** with proper policies
3. **Automated Sync Script** for cache directory
4. **Download Process Integration** (real-time upload)

#### Future Migration (Phase 2)
1. **Lambda Functions** for pipeline processing
2. **Step Functions** for workflow orchestration
3. **EventBridge** for event-driven processing
4. **CloudWatch** for monitoring and logging

## Implementation Steps

### Phase 1: Backup Setup (Immediate)

#### Step 1: AWS Setup
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
```

#### Step 2: Create S3 Buckets
```bash
# Raw data bucket
aws s3 mb s3://storydredge-raw-cache --region us-east-1

# Processed data bucket  
aws s3 mb s3://storydredge-processed-data --region us-east-1
```

#### Step 3: Sync Script
Create `scripts/sync_to_cloud.py` for automated backup

#### Step 4: Integration
Modify download script to upload to S3 in real-time

### Phase 2: Full Cloud Migration (Future)

#### Infrastructure as Code
- **Terraform** or **CloudFormation** templates
- **VPC** setup for security
- **IAM roles** and policies
- **Lambda deployment** packages

#### Data Pipeline
- **AWS Glue** for ETL processing
- **Amazon Textract** for enhanced OCR
- **Amazon Comprehend** for NLP classification
- **Amazon OpenSearch** for full-text search

## Cost Estimation

### Current Dataset (15-20GB projected)
- **S3 Storage**: ~$0.30-0.40/month
- **Data Transfer**: ~$1.80 for initial upload
- **DynamoDB**: ~$2.50/month (1M items, light usage)

### Full Scale (1M+ articles)
- **S3 Storage**: ~$15-25/month
- **DynamoDB**: ~$25-50/month
- **Lambda**: ~$10-20/month
- **Total**: ~$50-95/month

## Security Considerations

### Access Control
- **IAM roles** with least privilege
- **S3 bucket policies** restricting access
- **VPC endpoints** for private communication
- **Encryption at rest** and in transit

### Data Privacy
- **No PII** in article content (historical newspapers)
- **Audit logging** for all access
- **Backup retention** policies
- **GDPR compliance** considerations

## Monitoring & Alerting

### CloudWatch Metrics
- **Storage usage** and costs
- **Pipeline processing** times
- **Error rates** and failures
- **Data quality** metrics

### Alerts
- **Failed uploads** to S3
- **Pipeline failures**
- **Cost thresholds** exceeded
- **Storage quota** warnings

## Next Steps

1. **AWS Account Setup** and billing alerts
2. **Create S3 buckets** with proper configuration
3. **Implement sync script** for immediate backup
4. **Test upload/download** workflows
5. **Monitor costs** and optimize storage classes
6. **Plan Phase 2** migration timeline

## Alternative Architectures Considered

### Google Cloud Platform
- **Pros**: BigQuery for analytics, strong ML tools
- **Cons**: Higher egress costs, less mature for this use case

### Microsoft Azure
- **Pros**: Good integration with existing tools
- **Cons**: More complex pricing, less cost-effective for storage

### Conclusion
AWS provides the best balance of cost, features, and scalability for StoryDredge's requirements. 