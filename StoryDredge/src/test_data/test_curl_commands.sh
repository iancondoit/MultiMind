#!/bin/bash

# Test commands for StoryDredge API

# Health check
curl http://localhost:8081/health

# Submit batch
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test_api_key" \
  -d @test_data/test_batch.json \
  http://localhost:8081/api/articles/batch

# Submit single article
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test_api_key" \
  -d @test_data/test_article.json \
  http://localhost:8081/api/articles

# Check article status
curl -H "X-API-Key: test_api_key" http://localhost:8081/api/articles/status/ARTICLE_ID_HERE

# Check batch status
curl -H "X-API-Key: test_api_key" http://localhost:8081/api/batch/status/BATCH_ID_HERE
