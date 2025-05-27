#!/bin/bash
# Batch Process Local Issues Shell Script
# This script provides a friendly wrapper around the batch_process_local_issues.py script

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
SOURCE_DIR="temp_downloads"
OUTPUT_DIR="output/hsa-ready-final"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to display usage information
function show_usage {
    echo -e "${BLUE}Batch Process Local Newspaper OCR Files${NC}"
    echo
    echo -e "This script processes multiple OCR files from a directory through the unified pipeline."
    echo
    echo -e "${CYAN}Usage:${NC}"
    echo -e "  $0 [options]"
    echo
    echo -e "${CYAN}Options:${NC}"
    echo -e "  ${GREEN}--source-dir DIR${NC}      Directory containing OCR files (default: $SOURCE_DIR)"
    echo -e "  ${GREEN}--output-dir DIR${NC}      Output directory (default: $OUTPUT_DIR)"
    echo -e "  ${GREEN}--issues-file FILE${NC}    Optional file containing issue IDs to process (one per line)"
    echo -e "  ${GREEN}--help${NC}                Show this help message"
    echo
    echo -e "${CYAN}Examples:${NC}"
    echo -e "  $0 --source-dir temp_downloads"
    echo -e "  $0 --source-dir custom_downloads --output-dir custom_output --issues-file my_issues.txt"
    echo
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --source-dir)
            SOURCE_DIR="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --issues-file)
            ISSUES_FILE="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed or not in PATH${NC}"
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Change to the project root directory
cd "$PROJECT_ROOT"

# Display batch processing start information
echo "====================================="
echo -e "${BLUE}Starting Batch Processing of Local OCR Files${NC}"
echo -e "${YELLOW}$(date)${NC}"
echo "====================================="

# Construct the command
CMD="python scripts/batch_process_local_issues.py --source-dir $SOURCE_DIR --output-dir $OUTPUT_DIR"
if [ ! -z "$ISSUES_FILE" ]; then
    CMD="$CMD --issues-file $ISSUES_FILE"
fi

# Execute the command
echo -e "${YELLOW}Executing:${NC} $CMD"
echo "-------------------------------------"
eval $CMD
RESULT=$?

# Check if the command was successful
echo "====================================="
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}Batch processing completed successfully!${NC}"
    echo -e "Source directory: ${CYAN}$SOURCE_DIR${NC}"
    echo -e "Output directory: ${CYAN}$OUTPUT_DIR${NC}"
    echo -e "You can view the processed articles in the output directory."
else
    echo -e "${RED}Batch processing failed with exit code $RESULT${NC}"
    echo -e "Please check the logs for details."
    echo -e "Logs directory: ${CYAN}logs/${NC}"
fi
echo "====================================="

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

exit $RESULT 