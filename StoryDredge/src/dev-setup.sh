#!/bin/bash
# dev-setup.sh - Setup development environment for StoryDredge

# Ensure script exits on error
set -e

echo "Setting up StoryDredge development environment..."

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+\.\d+')
REQUIRED_VERSION="3.9.0"

echo "Detected Python $PYTHON_VERSION"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "Error: Python $REQUIRED_VERSION or newer is required."
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directory structure if needed
echo "Ensuring directory structure..."
mkdir -p data/cache
mkdir -p output/hsa-ready
mkdir -p models

# Set up git hooks
echo "Setting up git hooks..."
if [ -d ".git" ]; then
    cat > .git/hooks/pre-commit << 'EOL'
#!/bin/bash
# Pre-commit hook for StoryDredge

# Check for basic linting issues
echo "Running black check..."
black --check src tests || { echo "Black check failed. Run 'black src tests' to fix formatting issues."; exit 1; }

echo "Running isort check..."
isort --check src tests || { echo "isort check failed. Run 'isort src tests' to fix import sorting issues."; exit 1; }

echo "Running basic pytest..."
pytest -xvs tests/test_utils/ || { echo "Basic tests failed."; exit 1; }
EOL
    chmod +x .git/hooks/pre-commit
fi

echo "Development environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  ./run_tests.py"
echo "" 