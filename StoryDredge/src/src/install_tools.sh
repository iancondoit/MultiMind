#!/bin/bash
# Tool installation and database setup for StoryDredge importing

echo "Setting up environment for StoryDredge import"

# Make sure we're in a Python environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
  echo "Creating Python virtual environment..."
  python3 -m venv .venv
  source .venv/bin/activate
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install psycopg2-binary psycopg2 flask

# Check for PostgreSQL
if ! command -v psql &> /dev/null; then
  echo "PostgreSQL not found. Please install PostgreSQL first."
  echo "On macOS: brew install postgresql@14"
  echo "On Linux: sudo apt-get install postgresql"
  exit 1
fi

# Check if PostgreSQL server is running
if ! pg_isready &> /dev/null; then
  echo "PostgreSQL server is not running. Please start it first:"
  echo "On macOS: brew services start postgresql"
  echo "On Linux: sudo service postgresql start"
  exit 1
fi

# Create database if it doesn't exist
echo "Creating PostgreSQL database 'storymap' if it doesn't exist..."
PGPASSWORD=postgres psql -U postgres -h localhost -c "SELECT 1 FROM pg_database WHERE datname='storymap'" | grep -q 1
if [ $? -ne 0 ]; then
  echo "Creating database 'storymap'..."
  PGPASSWORD=postgres psql -U postgres -h localhost -c "CREATE DATABASE storymap" 
fi

echo "Setup completed! You can now run:"
echo "./run_pg_import.sh --test"
echo "to test the import process with a small sample." 