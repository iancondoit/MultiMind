#!/bin/bash
# Universal Newspaper Pipeline Shell Script
# This script provides a friendly wrapper around the universal newspaper pipeline

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
OUTPUT_DIR="output/hsa-ready-final"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to display usage information
function show_usage {
    echo -e "${BLUE}Universal Newspaper Pipeline${NC}"
    echo
    echo -e "This script processes newspaper issues from archive.org through the unified pipeline."
    echo
    echo -e "${CYAN}Usage:${NC}"
    echo -e "  $0 [options]"
    echo
    echo -e "${CYAN}Options:${NC}"
    echo -e "  ${GREEN}--issue ISSUE_ID${NC}       Process a single issue"
    echo -e "  ${GREEN}--issues-file FILE${NC}     Process multiple issues from a file (one ID per line)"
    echo -e "  ${GREEN}--output-dir DIR${NC}       Output directory (default: $OUTPUT_DIR)"
    echo -e "  ${GREEN}--help${NC}                 Show this help message"
    echo
    echo -e "${CYAN}Examples:${NC}"
    echo -e "  $0 --issue per_atlanta-constitution_1922-01-01_54_203"
    echo -e "  $0 --issues-file data/issue_list.txt --output-dir custom_output"
    echo
}

# Check if no arguments provided
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --issue)
            ISSUE="$2"
            shift 2
            ;;
        --issues-file)
            ISSUES_FILE="$2"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
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

# Check if we have required arguments
if [ -z "$ISSUE" ] && [ -z "$ISSUES_FILE" ]; then
    echo -e "${RED}Error: Either --issue or --issues-file must be specified${NC}"
    show_usage
    exit 1
fi

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

# Display pipeline start information
echo "====================================="
echo -e "${BLUE}Starting Universal Newspaper Pipeline${NC}"
echo -e "${YELLOW}$(date)${NC}"
echo "====================================="

# Construct the command
if [ ! -z "$ISSUE" ]; then
    echo -e "${GREEN}Processing single issue:${NC} $ISSUE"
    CMD="python scripts/universal_newspaper_pipeline.py --issue $ISSUE --output $OUTPUT_DIR"
else
    echo -e "${GREEN}Processing issues from file:${NC} $ISSUES_FILE"
    CMD="python scripts/universal_newspaper_pipeline.py --issues-file $ISSUES_FILE --output $OUTPUT_DIR"
fi

# Execute the command
echo -e "${YELLOW}Executing:${NC} $CMD"
echo "-------------------------------------"
eval $CMD
RESULT=$?

# Check if the command was successful
echo "====================================="
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}Pipeline completed successfully!${NC}"
    if [ ! -z "$ISSUE" ]; then
        echo -e "Processed issue: ${CYAN}$ISSUE${NC}"
    else
        echo -e "Processed issues from: ${CYAN}$ISSUES_FILE${NC}"
    fi
    echo -e "Output directory: ${CYAN}$OUTPUT_DIR${NC}"
    echo -e "You can view the processed articles in the output directory."
else
    echo -e "${RED}Pipeline failed with exit code $RESULT${NC}"
    echo -e "Please check the logs for details."
    echo -e "Logs directory: ${CYAN}logs/${NC}"
fi
echo "====================================="

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

exit $RESULT 