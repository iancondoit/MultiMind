#!/bin/bash
# Automatic processing of new articles into PostgreSQL
# This script should be called after new articles are generated

# Script locations
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="../output/atlanta-constitution"
DB_USER="$(whoami)"
DB_PASSWORD=""
DB_NAME="storymap"
DB_HOST="localhost"
DB_PORT="5432"

# Log file
LOG_FILE="postgres_pipeline.log"
echo "$(date) - Starting automatic PostgreSQL import" | tee -a "$LOG_FILE"

# Check if there are new files to process
TOTAL_FILES=$(find "$OUTPUT_DIR" -type f -name "*.json" | wc -l)
echo "Found $TOTAL_FILES total JSON files" | tee -a "$LOG_FILE"

# Get current count in database
DB_COUNT=$(psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM articles")
DB_COUNT=$(echo "$DB_COUNT" | tr -d ' ')
echo "Current database has $DB_COUNT articles" | tee -a "$LOG_FILE"

if [ "$TOTAL_FILES" -gt "$DB_COUNT" ]; then
    NEW_FILES=$((TOTAL_FILES - DB_COUNT))
    echo "Found $NEW_FILES new files to process" | tee -a "$LOG_FILE"
    
    # Run the import with skip_existing flag to only process new files
    "$SCRIPT_DIR/run_pg_import.sh" \
        --db-user "$DB_USER" \
        --db-password "$DB_PASSWORD" \
        --db-name "$DB_NAME" \
        --db-host "$DB_HOST" \
        --db-port "$DB_PORT" \
        --input-dir "$OUTPUT_DIR" \
        --skip-existing
    
    # Check result
    if [ $? -eq 0 ]; then
        echo "$(date) - Successfully processed new articles into PostgreSQL" | tee -a "$LOG_FILE"
    else
        echo "$(date) - ERROR: Failed to process new articles" | tee -a "$LOG_FILE"
        exit 1
    fi
else
    echo "No new files to process" | tee -a "$LOG_FILE"
fi

echo "$(date) - Finished automatic PostgreSQL import" | tee -a "$LOG_FILE"
exit 0 