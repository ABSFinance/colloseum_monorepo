# Market Data Tests

This directory contains tests for the market data models in the `src/models/market_data.py` module.

## Prerequisites

The tests require a Python virtual environment with all necessary dependencies installed. You can set this up easily using the provided script:

```bash
# From the project root (ABS_eval directory)
./setup_dev.sh
```

This script will:

1. Create a virtual environment in the `venv` directory
2. Install all required dependencies
3. Set up the PYTHONPATH correctly
4. Create a convenient script for running tests

If you prefer to set up manually, install the required packages:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install pytest pytest-asyncio python-dotenv supabase pandas numpy
```

## Test Files

- `test_market_data.py`: Unit tests with mocks for the `MarketData` class
- `test_market_data_integration.py`: Integration tests using real Supabase credentials

## Running the Tests

### Using the Convenience Script (Recommended)

After running `setup_dev.sh`, you can use the generated script to run tests:

```bash
# Run unit tests only
./run_tests.sh

# Run both unit and integration tests
./run_tests.sh -i
```

### Running Tests Manually

If you prefer to run tests manually, first activate the virtual environment:

```bash
source venv/bin/activate
```

Then run the tests:

#### Unit Tests

```bash
# Ensure you're in the project root directory (ABS_eval)
python -m pytest tests/test_models/test_market_data.py -v
```

#### Integration Tests

```bash
# Ensure you're in the project root directory (ABS_eval)
python -m pytest tests/test_models/test_market_data_integration.py -v
```

### Environment Variables for Integration Tests

The integration tests require the following environment variables:

- `SUPABASE_URL`: The URL of your Supabase project
- `SUPABASE_SERVICE_KEY` or `SUPABASE_KEY`: The API key for your Supabase project

These can be set in a `.env` file in the project root or in the parent `fund_manager/.env` file.

## Sample Data

When running the integration tests, a file called `market_data_samples.json` will be created with samples of each type of market data retrieved. This can be helpful for debugging and understanding the data structure.

## Troubleshooting

If you encounter errors:

1. **Virtual environment issues**: Make sure you've activated the virtual environment

   ```bash
   source venv/bin/activate
   ```

2. **Module not found errors**: The PYTHONPATH should be automatically set when you activate the virtual environment. If you still have issues, manually set it:

   ```bash
   export PYTHONPATH=.
   ```

3. **Supabase connection errors**: Verify your `.env` file has the correct credentials
