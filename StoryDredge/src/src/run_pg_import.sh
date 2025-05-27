#!/bin/bash
# Import Atlanta Constitution articles into PostgreSQL

# Default values - modify these for your environment
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="storymap"
DB_USER="postgres"
DB_PASSWORD="postgres"
INPUT_DIR="output/atlanta-constitution"
BATCH_SIZE=1000
THREADS=4
MAX_ARTICLES=""
SKIP_EXISTING=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --db-host)
      DB_HOST="$2"
      shift 2
      ;;
    --db-port)
      DB_PORT="$2"
      shift 2
      ;;
    --db-name)
      DB_NAME="$2"
      shift 2
      ;;
    --db-user)
      DB_USER="$2"
      shift 2
      ;;
    --db-password)
      DB_PASSWORD="$2"
      shift 2
      ;;
    --input-dir)
      INPUT_DIR="$2"
      shift 2
      ;;
    --batch-size)
      BATCH_SIZE="$2"
      shift 2
      ;;
    --threads)
      THREADS="$2"
      shift 2
      ;;
    --max-articles)
      MAX_ARTICLES="--max-articles $2"
      shift 2
      ;;
    --skip-existing)
      SKIP_EXISTING="--skip-existing"
      shift
      ;;
    --test)
      # Test mode with only 100 articles
      MAX_ARTICLES="--max-articles 100"
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --db-host HOST       PostgreSQL host (default: $DB_HOST)"
      echo "  --db-port PORT       PostgreSQL port (default: $DB_PORT)"
      echo "  --db-name NAME       PostgreSQL database name (default: $DB_NAME)"
      echo "  --db-user USER       PostgreSQL user (default: $DB_USER)"
      echo "  --db-password PASS   PostgreSQL password (default: $DB_PASSWORD)"
      echo "  --input-dir DIR      Directory containing processed articles (default: $INPUT_DIR)"
      echo "  --batch-size SIZE    Number of articles per batch (default: $BATCH_SIZE)"
      echo "  --threads NUM        Number of worker threads (default: $THREADS)"
      echo "  --max-articles NUM   Maximum number of articles to process (for testing)"
      echo "  --skip-existing      Skip articles that already exist in the database"
      echo "  --test               Test mode with only 100 articles"
      echo "  --help               Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Make sure Python is available
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
  PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
  PYTHON_CMD="python"
else
  echo "Error: Python not found. Please install Python 3."
  exit 1
fi

# Make sure the input directory exists
if [ ! -d "$INPUT_DIR" ]; then
  echo "Error: Input directory not found: $INPUT_DIR"
  exit 1
fi

# Check if psycopg2 is installed
$PYTHON_CMD -c "import psycopg2" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Installing required Python packages..."
  $PYTHON_CMD -m pip install psycopg2-binary
fi

# Print the configuration
echo "==== PostgreSQL Import Configuration ===="
echo "Database Host:     $DB_HOST"
echo "Database Port:     $DB_PORT"
echo "Database Name:     $DB_NAME"
echo "Database User:     $DB_USER"
echo "Input Directory:   $INPUT_DIR"
echo "Batch Size:        $BATCH_SIZE"
echo "Worker Threads:    $THREADS"
if [ -n "$MAX_ARTICLES" ]; then
  echo "Max Articles:     $MAX_ARTICLES"
fi
if [ -n "$SKIP_EXISTING" ]; then
  echo "Skip Existing:    Yes"
fi
echo "========================================"

# Run the import script
echo "Starting import process..."
$PYTHON_CMD direct_import_to_postgres.py \
  --db-host "$DB_HOST" \
  --db-port "$DB_PORT" \
  --db-name "$DB_NAME" \
  --db-user "$DB_USER" \
  --db-password "$DB_PASSWORD" \
  --input-dir "$INPUT_DIR" \
  --batch-size "$BATCH_SIZE" \
  --threads "$THREADS" \
  $MAX_ARTICLES $SKIP_EXISTING

# Check exit status
STATUS=$?
if [ $STATUS -eq 0 ]; then
  echo "Import completed successfully."
else
  echo "Import failed with status $STATUS."
fi

exit $STATUS 