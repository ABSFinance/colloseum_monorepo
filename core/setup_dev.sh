#!/bin/bash
# Setup development environment for ABS_eval using a virtual environment

set -e  # Exit on error

echo "=== Setting up development environment for ABS_eval ==="

# Check if running on macOS
IS_MACOS=false
if [[ "$(uname)" == "Darwin" ]]; then
    IS_MACOS=true
    echo "Detected macOS environment"
fi

# Find Python executable
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Error: Could not find Python executable. Please make sure Python is installed."
    if $IS_MACOS; then
        echo "On macOS, you can install Python with: brew install python"
    fi
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Setup virtual environment
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    $PYTHON_CMD -m venv $VENV_DIR || {
        echo "Failed to create virtual environment."
        exit 1
    }
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip inside virtual environment
echo "Upgrading pip..."
pip install --upgrade pip

# Install all requirements in the virtual environment
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating example .env file..."
    cp .env.example .env 2>/dev/null || echo "# Environment variables for ABS_eval
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_KEY=your_service_key_here
USE_MOCK_DATA=true" > .env
    echo "Please edit .env file with your actual configuration values."
fi

# Setup PYTHONPATH in the virtual environment
CURRENT_DIR=$(pwd)
echo "Setting PYTHONPATH to include current directory..."

# Create or append to the activate script to include PYTHONPATH
if grep -q "PYTHONPATH=" "$VENV_DIR/bin/activate"; then
    # Already exists, update it
    if $IS_MACOS; then
        # macOS requires empty string for in-place sed
        sed -i '' "s|export PYTHONPATH=.*|export PYTHONPATH=\"$CURRENT_DIR:\$PYTHONPATH\"|g" "$VENV_DIR/bin/activate"
    else
        # Linux version
        sed -i "s|export PYTHONPATH=.*|export PYTHONPATH=\"$CURRENT_DIR:\$PYTHONPATH\"|g" "$VENV_DIR/bin/activate"
    fi
else
    # Add it to the activate script
    echo "export PYTHONPATH=\"$CURRENT_DIR:\$PYTHONPATH\"" >> "$VENV_DIR/bin/activate"
fi

# Generate a convenience script to run the tests
cat > run_tests.sh << 'EOF'
#!/bin/bash
# Script to run the market data tests within the virtual environment

# Activate virtual environment
source venv/bin/activate

# Run the tests
cd "$(dirname "$0")"
python -m pytest tests/test_models/test_market_data.py -v
echo "Unit tests completed."

# Check if integration tests should be run
if [ "$1" == "--integration" ] || [ "$1" == "-i" ]; then
    python -m pytest tests/test_models/test_market_data_integration.py -v
    echo "Integration tests completed."
fi
EOF

chmod +x run_tests.sh

echo "================================================================"
echo "Development environment setup complete!"
echo ""
echo "To use this environment:"
echo "  1. Activate the virtual environment with:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Run the tests with:"
echo "     ./run_tests.sh         # For unit tests only"
echo "     ./run_tests.sh -i      # For unit and integration tests"
echo "================================================================"

# Leave the virtual environment activated
echo "Virtual environment is now active!" 