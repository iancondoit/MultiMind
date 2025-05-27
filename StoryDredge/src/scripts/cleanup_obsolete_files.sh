#!/bin/bash
# Cleanup Obsolete Files Script
# This script moves obsolete files to the archive directory

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ARCHIVE_DIR="$PROJECT_ROOT/archive/scripts"

# Ensure archive directory exists
mkdir -p "$ARCHIVE_DIR"

# List of obsolete files to archive
OBSOLETE_FILES=(
    # Scripts replaced by universal_newspaper_pipeline.py
    "test_atlanta_constitution_direct.py"
    "run_classification.py"
    "run_classification.sh"
    "migrate_hsa_data.py"
    
    # Scripts replaced by process_local_issue.py
    "process_atlanta_constitution.py"
    "process_constitution_pipeline.py"
    
    # Other obsolete scripts
    "prepare_atlanta_constitution_dataset.py"
    "run_atlanta_constitution_test.py"
    "verify_atlanta_constitution_testing.py"
)

# Function to archive a file
archive_file() {
    local file="$1"
    local full_path="$SCRIPT_DIR/$file"
    
    if [ -f "$full_path" ]; then
        echo -e "${YELLOW}Archiving:${NC} $file"
        cp "$full_path" "$ARCHIVE_DIR/"
        git rm -f "$full_path" --quiet
        echo -e "${GREEN}✓${NC} Moved to archive: $file"
    else
        echo -e "${RED}×${NC} File not found: $file"
    fi
}

# Display header
echo "====================================="
echo -e "${BLUE}Cleaning up obsolete files${NC}"
echo "====================================="

# Archive each obsolete file
for file in "${OBSOLETE_FILES[@]}"; do
    archive_file "$file"
done

# Confirm completion
echo "====================================="
echo -e "${GREEN}Cleanup complete!${NC}"
echo -e "Archived files can be found in: ${CYAN}archive/scripts/${NC}"
echo "=====================================" 