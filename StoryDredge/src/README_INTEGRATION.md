# StoryDredge to StoryMap Integration

This document explains how to use the StoryDredge API integration to send processed newspaper articles to the StoryMap system.

## Overview

The integration consists of:
1. **API Client**: A Python script for sending articles to the StoryMap API
2. **Docker Service**: A Docker setup for running the API service
3. **PostgreSQL Database**: Storage for processed articles

## Getting Started

### Prerequisites
- Docker and Docker Compose
- Python 3.10 or higher
- Access to processed StoryDredge articles

### Setup

1. **Configure Environment**

Create a `.env` file in the project root:
```
API_KEY=your_api_key_here
DB_HOST=db
DB_PORT=5432
DB_NAME=storymap
DB_USER=postgres
DB_PASSWORD=postgres
```

2. **Start Docker Services**

```bash
docker-compose up -d
```

This will start:
- The StoryDredge API service on port 8081
- PostgreSQL database on port 5432

3. **Check Health Status**

```bash
curl http://localhost:8081/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Sending Articles to StoryMap

### Using the API Client Script

The `storydredge_api_client.py` script can be used to send processed articles to the StoryMap API:

```bash
python3 storydredge_api_client.py \
  --input-dir output/atlanta-constitution \
  --api-url http://localhost:8081 \
  --api-key your_api_key_here \
  --batch-size 100 \
  --threads 4
```

Optional parameters:
- `--max-articles`: Limit the number of articles to process (for testing)

### Manual API Usage

You can also send articles manually:

```bash
# Send a single article
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "id": "article123",
    "title": "Article Title",
    "content": "Article content...",
    "source": "Atlanta Constitution",
    "date": "1920-05-15",
    "category": "news",
    "tags": ["tag1", "tag2"],
    "metadata": {
      "ocr_confidence": 0.95,
      "word_count": 500
    }
  }' \
  http://localhost:8081/api/articles
```

## Monitoring Progress

### Check Article Status

```bash
curl -H "X-API-Key: your_api_key_here" \
  http://localhost:8081/api/articles/status/article123
```

### Check Batch Status

```bash
curl -H "X-API-Key: your_api_key_here" \
  http://localhost:8081/api/batch/status/batch123
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure Docker services are running
   - Check if ports are correctly mapped

2. **Authentication Errors**
   - Verify API key in environment variables
   - Check API key in request headers

3. **Database Connection Issues**
   - Check PostgreSQL container logs
   - Verify database credentials

### Logs

To check logs:

```bash
# API service logs
docker-compose logs storydredge-api

# Database logs
docker-compose logs db
```

## Development

### Local Development Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run API service locally:
```bash
python storydredge_api.py
```

3. Run API client locally:
```bash
python storydredge_api_client.py --api-url http://localhost:8080 --api-key test_api_key --input-dir output/test
```

## API Reference

See the [Technical Handoff Document](TECHNICAL_HANDOFF.md) for detailed API specifications.

## Version History

- 1.0.0 (2024-05-12): Initial integration 