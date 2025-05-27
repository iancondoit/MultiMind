#!/bin/bash
# Cleanup JSON files after PostgreSQL import
# This script backs up a small sample and then removes all JSON files

# Configuration
OUTPUT_DIR="../output/atlanta-constitution"
BACKUP_DIR="../output/sample_backup"
SAMPLE_SIZE=100  # Number of files to keep as a sample

echo "==============================================="
echo "JSON Cleanup and Sample Backup"
echo "==============================================="

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"
echo "Created backup directory: $BACKUP_DIR"

# Create a random sample of files
echo "Creating backup of $SAMPLE_SIZE random sample files..."
find "$OUTPUT_DIR" -type f -name "*.json" | sort -R | head -n "$SAMPLE_SIZE" | while read file; do
    # Preserve the directory structure in the backup
    rel_path="${file#$OUTPUT_DIR/}"
    backup_path="$BACKUP_DIR/$rel_path"
    mkdir -p "$(dirname "$backup_path")"
    cp "$file" "$backup_path"
done

echo "Backup complete. Sample files saved to $BACKUP_DIR"

# Get pre-deletion stats
TOTAL_FILES=$(find "$OUTPUT_DIR" -type f -name "*.json" | wc -l)
TOTAL_SIZE=$(du -sh "$OUTPUT_DIR" | awk '{print $1}')

echo "==============================================="
echo "About to delete $TOTAL_FILES JSON files ($TOTAL_SIZE)"
echo "A sample of $SAMPLE_SIZE files has been backed up to $BACKUP_DIR"
echo "==============================================="

# Confirm deletion
read -p "Are you sure you want to delete all JSON files? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Deletion cancelled."
    exit 1
fi

# Delete JSON files
echo "Deleting JSON files..."
find "$OUTPUT_DIR" -type f -name "*.json" -delete

# Delete empty directories
echo "Cleaning up empty directories..."
find "$OUTPUT_DIR" -type d -empty -delete

# Check result
REMAINING_FILES=$(find "$OUTPUT_DIR" -type f -name "*.json" | wc -l)
if [ "$REMAINING_FILES" -eq 0 ]; then
    echo "SUCCESS: All JSON files have been deleted."
    echo "A backup sample of $SAMPLE_SIZE files is available at $BACKUP_DIR"
else
    echo "WARNING: $REMAINING_FILES JSON files remain."
fi

echo "Cleanup complete!" 