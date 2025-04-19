#!/bin/bash
# Script to run market data tests using real Supabase credentials within a virtual environment

# Stop on any error
set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./setup_dev.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check for .env file and explicitly export variables
if [ -f ".env" ]; then
    echo "Found .env file in current directory"
    # Manually export the credentials
    export SUPABASE_URL=$(grep -o 'SUPABASE_URL=.*' .env | cut -d '=' -f2)
    export SUPABASE_SERVICE_KEY=$(grep -o 'SUPABASE_SERVICE_KEY=.*' .env | cut -d '=' -f2)
    echo "Manually exported SUPABASE_URL and SUPABASE_SERVICE_KEY from .env file"
elif [ -f "../fund_manager/.env" ]; then
    echo "Found .env file in fund_manager directory"
    # Manually export the credentials from fund_manager/.env
    export SUPABASE_URL=$(grep -o 'SUPABASE_URL=.*' ../fund_manager/.env | cut -d '=' -f2)
    export SUPABASE_SERVICE_KEY=$(grep -o 'SUPABASE_SERVICE_KEY=.*' ../fund_manager/.env | cut -d '=' -f2)
    echo "Manually exported SUPABASE_URL and SUPABASE_SERVICE_KEY from fund_manager/.env file"
fi

# Check required environment variables
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo "Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables are not set."
    echo "Please make sure these are set in your .env file."
    exit 1
fi

echo "SUPABASE_URL is set to: $SUPABASE_URL"
echo "SUPABASE_SERVICE_KEY is set (value hidden for security)"

# Add current directory to PYTHONPATH
export PYTHONPATH="$(pwd):$PYTHONPATH"
echo "PYTHONPATH set to: $PYTHONPATH"

# Fix the syntax error in market_data.py before running the tests
echo "Checking market_data.py for syntax errors..."
LINE_733_FILE="src/models/market_data.py"
if [ -f "$LINE_733_FILE" ]; then
    # Create a backup first
    cp "$LINE_733_FILE" "${LINE_733_FILE}.bak"
    
    # Fix the syntax error on line 733
    sed -i.bak -e '733s/.or(f/            .or(f/' "$LINE_733_FILE" || {
        echo "Warning: Could not automatically fix $LINE_733_FILE"
        echo "Please manually check line 733 for a syntax error before running tests."
    }
    
    echo "Fixes applied to $LINE_733_FILE"
fi

# Run the tests
echo "Running market data integration tests..."
python -m tests.test_models.test_market_data_integration

echo "Tests completed!" 