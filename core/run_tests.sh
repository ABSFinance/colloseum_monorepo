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
