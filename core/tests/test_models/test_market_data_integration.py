#!/usr/bin/env python3
"""
Integration tests for the market_data module.

This module contains integration tests for the MarketData class using
real Supabase credentials for actual data retrieval.
"""

import os
import pytest
import asyncio
from dotenv import load_dotenv
import json
from datetime import datetime
from pathlib import Path

# Try to locate and load the .env file 
load_dotenv()  # Load from current directory
# Also try to load from parent directories
for parent in ["..", "../..", "../../.."]:
    env_path = Path(parent) / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        break

# If we find a fund_manager/.env file, load that too
fund_manager_env = Path("../../../fund_manager/.env")
if fund_manager_env.exists():
    load_dotenv(fund_manager_env)

from supabase import create_client
from src.models.market_data import MarketData, MarketMetrics


# Skip all tests if environment variables are not set
pytestmark = pytest.mark.skipif(
    not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_KEY"),
    reason="Supabase credentials not available in environment variables"
)


@pytest.fixture
def supabase_client():
    """Create a real Supabase client using credentials from .env."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        pytest.skip("Supabase credentials not available")
    
    client = create_client(url, key)
    return client


@pytest.fixture
def market_data(supabase_client):
    """Create a MarketData instance with a real Supabase client."""
    return MarketData(supabase_client=supabase_client)


@pytest.mark.asyncio
async def test_get_market_metrics_real_data(market_data):
    """Test retrieving market metrics using actual Supabase connection."""
    try:
        # Retrieve all metrics without filters
        result = await market_data.get_market_metrics()
        
        # Verify we got a proper MarketMetrics object back
        assert isinstance(result, MarketMetrics)
        
        # Print some summary information
        print(f"\nRetrieved real market metrics:")
        print(f" - Total count: {result.total_count}")
        print(f" - Drift vaults: {len(result.drift_vaults)}")
        print(f" - Yield pools: {len(result.yield_pools)}")
        print(f" - Lending pools: {len(result.lending_pools)}")
        print(f" - ABS vaults: {len(result.abs_vaults)}")
        
        # Save the first item of each type for inspection (if available)
        samples = {}
        if result.drift_vaults:
            samples['drift_vault'] = result.drift_vaults[0].to_dict()
        if result.yield_pools:
            samples['yield_pool'] = result.yield_pools[0].to_dict()
        if result.lending_pools:
            samples['lending_pool'] = result.lending_pools[0].to_dict()
        if result.abs_vaults:
            samples['abs_vault'] = result.abs_vaults[0].to_dict()
        
        # Save samples to a file for review
        with open("market_data_samples.json", "w") as f:
            json.dump(samples, f, indent=2)
        
        # Assert we got some data back (at least one category should have items)
        assert result.total_count > 0, "No market data was retrieved"
        
    except Exception as e:
        pytest.fail(f"Integration test failed with error: {str(e)}")


@pytest.mark.asyncio
async def test_get_market_metrics_with_filters(market_data):
    """Test retrieving filtered market metrics."""
    try:
        # First get all metrics to see what's available
        all_metrics = await market_data.get_market_metrics()
        
        # If we have some drift vaults, test filtering by that asset type
        if all_metrics.drift_vaults:
            # Filter by asset type
            result = await market_data.get_market_metrics(asset_types=['drift_vault'])
            
            # Verify filtering worked correctly
            assert len(result.drift_vaults) > 0
            assert len(result.yield_pools) == 0
            assert len(result.lending_pools) == 0
            assert len(result.abs_vaults) == 0
            
            # If we have at least one drift vault, test filtering by asset ID
            if all_metrics.drift_vaults:
                sample_id = all_metrics.drift_vaults[0].id
                result = await market_data.get_market_metrics(asset_ids=[sample_id])
                
                # Verify at least one result is returned
                assert result.total_count > 0
                
    except Exception as e:
        pytest.fail(f"Filtered integration test failed with error: {str(e)}")


@pytest.mark.asyncio
async def test_get_single_asset_metrics(market_data):
    """Test retrieving metrics for a single asset."""
    try:
        # First get all metrics to see what's available
        all_metrics = await market_data.get_market_metrics()
        
        # If we have some drift vaults, test getting a single vault
        if all_metrics.drift_vaults:
            sample_vault = all_metrics.drift_vaults[0]
            
            # Get metrics for a single asset
            single_result = await market_data.get_single_asset_metrics(
                asset_id=sample_vault.id,
                asset_type='drift_vault'
            )
            
            # Verify the result matches what we expect
            assert single_result.id == sample_vault.id
            assert single_result.name == sample_vault.name
            assert single_result.tvl == sample_vault.tvl
            
    except Exception as e:
        pytest.fail(f"Single asset test failed with error: {str(e)}")


@pytest.mark.asyncio
async def test_get_market_data_historical(market_data):
    """Test retrieving historical market data."""
    try:
        # First get all metrics to see what's available
        all_metrics = await market_data.get_market_metrics()
        
        # If we have some assets, test getting historical data
        if all_metrics.total_count > 0:
            # Pick the first available asset of any type
            sample_asset = None
            if all_metrics.drift_vaults:
                sample_asset = all_metrics.drift_vaults[0].id
            elif all_metrics.yield_pools:
                sample_asset = all_metrics.yield_pools[0].id
            elif all_metrics.lending_pools:
                sample_asset = all_metrics.lending_pools[0].id
            elif all_metrics.abs_vaults:
                sample_asset = all_metrics.abs_vaults[0].id
            
            if sample_asset:
                # Get historical data for the past 30 days
                start_date = datetime.now().replace(day=1)  # First day of current month
                end_date = datetime.now()
                
                historical_data = await market_data.get_market_data(
                    asset_ids=[sample_asset],
                    start_date=start_date,
                    end_date=end_date
                )
                
                # Print information about the data we got back
                if historical_data and sample_asset in historical_data:
                    df = historical_data[sample_asset]
                    print(f"\nRetrieved historical data for asset {sample_asset}:")
                    print(f" - Time range: {start_date} to {end_date}")
                    print(f" - Data points: {len(df)}")
                    print(f" - Columns: {list(df.columns)}")
                    
                    # Basic validation that we either got data or an empty result
                    assert isinstance(historical_data, dict)
                    
    except Exception as e:
        pytest.fail(f"Historical data test failed with error: {str(e)}")


if __name__ == '__main__':
    # This allows running the tests directly with python
    # (will use the default event loop instead of pytest's)
    async def run_tests():
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            print("Supabase credentials not found in environment")
            return
            
        client = create_client(url, key)
        market_data_client = MarketData(supabase_client=client)
        
        # Run the tests manually
        print("Running integration tests directly...")
        await test_get_market_metrics_real_data(market_data_client)
        await test_get_market_metrics_with_filters(market_data_client)
        await test_get_single_asset_metrics(market_data_client)
        await test_get_market_data_historical(market_data_client)
        print("Tests completed successfully!")
    
    asyncio.run(run_tests()) 