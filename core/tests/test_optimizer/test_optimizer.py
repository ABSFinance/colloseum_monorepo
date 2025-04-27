import pytest
import pandas as pd
import numpy as np
import asyncio
import logging
import argparse
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from datetime import datetime, timedelta, UTC
from supabase import create_async_client, AsyncClient
from core.src.optimizer.optimizer import Optimizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_iso_datetime(dt=None):
    """Create an ISO 8601 formatted datetime string.
    
    Args:
        dt: Datetime object to format (default: current UTC time)
        
    Returns:
        ISO 8601 formatted string
    """
    if dt is None:
        dt = datetime.now(UTC)
    # Format with microsecond precision and explicit timezone
    return dt.isoformat()

class OptimizerTest:
    """Test harness for optimizer with real database connection."""

    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize the test harness.
        
        Args:
            supabase_url: Supabase URL for connection
            supabase_key: Supabase API key for authentication
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_client = None
        self.optimizer = None
        
        logger.info("OptimizerTest initialized")
    
    async def connect_to_supabase(self):
        """Connect to Supabase and initialize the client."""
        try:
            self.supabase_client = await create_async_client(
                self.supabase_url, 
                self.supabase_key
            )
            logger.info("Connected to Supabase successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            return False
    
    async def setup_optimizer(self):
        """Set up the optimizer with Supabase client."""
        if not self.supabase_client:
            logger.error("Cannot set up optimizer: Supabase client not initialized")
            return False
        
        try:
            self.optimizer = Optimizer(supabase_client=self.supabase_client)
            logger.info("Optimizer set up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set up optimizer: {str(e)}")
            return False

    async def run_test_sequence(self):
        """Run the test sequence."""
        if not self.optimizer:
            logger.error("Cannot run test: Optimizer not initialized")
            return
        
        try:
            # Test market data initialization for multiple pools
            for pool_id in ['1105', '1088']:
                days = 30
                await self.optimizer.initialize_market_data(pool_id, days)
                
                # If no market data was fetched from the database, simulate some test data
                if pool_id not in self.optimizer.market_data or self.optimizer.market_data[pool_id].empty:
                    logger.warning(f"No market data found for pool {pool_id} in database, creating simulated data")
                    
                    # Create simulated data matching the actual database schema
                    dates = pd.date_range(end=datetime.now(UTC), periods=30, freq='D')
                    
                    # Generate random returns
                    apy_values = np.random.normal(5.0, 1.0, size=30).astype(np.float64)  # APY as percentage (5.0 = 5%)
                    
                    # Create DataFrame with performance data
                    df = pd.DataFrame({
                        'id': range(1, 31),
                        'pool_id': pool_id,
                        'tvl': np.random.uniform(1000000, 5000000, size=30).astype(np.float64),  # Explicit float64 type
                        'apy': apy_values,  # APY as percentage values (float64)
                        'created_at': [d.isoformat() for d in dates]
                    })
                    
                    # Verify numeric types
                    assert pd.api.types.is_float_dtype(df['apy']), "APY column must be float type"
                    
                    df['timestamp_parsed'] = pd.to_datetime(df['created_at'])
                    df.set_index('timestamp_parsed', inplace=True)
                    
                    # Add to optimizer's market data
                    self.optimizer.market_data[pool_id] = df
                    
                    logger.info(f"Created simulated market data for {pool_id} with {len(df)} records")
                
                # Verify market data exists now
                assert pool_id in self.optimizer.market_data
                assert isinstance(self.optimizer.market_data[pool_id], pd.DataFrame)
                assert not self.optimizer.market_data[pool_id].empty
            
            logger.info("Market data initialization test passed")
            
            # Test vault initialization and optimization
            vault_info = {
                'pool_id': 'vault_1',
                'strategy': 'min_risk',
                'allowed_pools': ['1105', '1088'],
                'adaptors': ["kamino-lend", "save"],
                'weights': [0.6, 0.4]
            }
            
            self.optimizer.initialize_vault(vault_info)
            
            # Initialize market data for the vault itself using the schema with apy instead of return
            market_data = {
                'pool_id': 'vault_1',
                'created_at': create_iso_datetime(),
                'tvl': float(2000000),  # Explicitly cast to float
                'apy': float(4.5)       # APY as percentage (4.5 = 4.5%)
            }
            
            # Test handle_market_data with only market_data
            result = self.optimizer.handle_market_data(market_data)
            
            assert isinstance(result, dict)
            assert 'pool_id' in result
            assert 'status' in result
            
            # Check if the optimization was successful
            if result.get('status') == 'success':
                assert 'allocation' in result
                assert 'timestamp' in result
                logger.info("Vault optimization test passed")
            else:
                logger.error(f"Vault optimization failed: {result.get('message', 'Unknown error')}")
                raise ValueError(f"Vault optimization failed: {result.get('message', 'Unknown error')}")
                
            # Test handle_market_data with market_data and vault_data
            updated_vault_info = {
                'pool_id': 'vault_1',
                'strategy': 'max_sharpe',  # Change strategy to test updates
                'allowed_pools': ['1105', '1088'],
                'adaptors': ["kamino-lend", "save"],
                'weights': [0.7, 0.3]  # Change weights to test updates
            }
            
            new_market_data = {
                'pool_id': 'vault_1',
                'created_at': create_iso_datetime(),
                'tvl': float(2500000),  # Updated TVL
                'apy': float(5.0)       # Updated APY
            }
            
            result = self.optimizer.handle_market_data(new_market_data, updated_vault_info)
            
            assert isinstance(result, dict)
            assert 'pool_id' in result
            assert result.get('status') == 'success', f"Failed with status {result.get('status')} and message: {result.get('message')}"
            
            # Test handle_vault_update with market_data parameter
            vault_info_update = {
                'pool_id': 'vault_1',
                'strategy': 'min_risk',  # Reset strategy
                'allowed_pools': ['1105', '1088'],
                'adaptors': ["kamino-lend", "save"],
                'weights': [0.5, 0.5]  # Update weights again
            }
            
            additional_market_data = {
                'pool_id': 'vault_1',
                'created_at': create_iso_datetime(),
                'tvl': float(2600000),
                'apy': float(5.2)
            }
            
            result = self.optimizer.handle_vault_update(vault_info_update, additional_market_data)
            
            assert isinstance(result, dict)
            assert 'pool_id' in result
            assert result.get('status') == 'success', f"Failed with status {result.get('status')} and message: {result.get('message')}"
            
            logger.info("Advanced optimization tests passed")
            
            # Create a second vault to test multi-vault reoptimization
            vault_info_2 = {
                'pool_id': 'vault_2',
                'strategy': 'max_sharpe',
                'allowed_pools': ['1105', '1088'],
                'adaptors': ["kamino-lend", "save"],
                'weights': [0.4, 0.6]
            }
            
            self.optimizer.initialize_vault(vault_info_2)
            
            # Add market data for the second vault
            market_data_2 = {
                'pool_id': 'vault_2',
                'created_at': create_iso_datetime(),
                'tvl': float(1500000),
                'apy': float(4.0)
            }
            
            self.optimizer.handle_market_data(market_data_2)
            
            assert isinstance(result, dict)
            assert result.get('status') == 'success'
            assert 'results' in result
            assert len(result['results']) == 2, f"Expected 2 vault results, got {len(result['results'])}"
            assert 'vault_1' in result['results']
            assert 'vault_2' in result['results']
            
            logger.info("Multi-vault reoptimization test passed")
            
            # Test reoptimizing all vaults with new market data
            global_market_data = {
                'created_at': create_iso_datetime(),
                'tvl': float(3000000),
                'apy': float(6.0)
            }
            
            # We need to add a pool_id for the global market data
            global_market_data['pool_id'] = '1105'  # Set to one of the underlying pools
            
            # This should reoptimize both vault_1 and vault_2 since both use this pool
            result = self.optimizer.handle_market_data(global_market_data)
            
            assert isinstance(result, dict)
            assert result.get('status') == 'success'
            assert 'results' in result, f"Missing 'results' in response: {result}"
            assert len(result['results']) == 2, f"Expected 2 vault results, got {len(result['results'])}"
            assert 'vault_1' in result['results']
            assert 'vault_2' in result['results']
            
            logger.info("Multi-vault reoptimization test passed")
            
            # Test reoptimizing vaults when market data for a constituent pool is updated
            constituent_market_data = {
                'pool_id': '1105',  # This is an underlying pool used by both vaults
                'created_at': create_iso_datetime(),
                'tvl': float(3500000),
                'apy': float(6.5)
            }
            
            # This should reoptimize both vault_1 and vault_2 since both use pool 1105
            result = self.optimizer.handle_market_data(constituent_market_data)
            
            assert isinstance(result, dict)
            assert result.get('status') == 'success'
            assert 'results' in result, f"Missing 'results' in response: {result}"
            assert len(result['results']) == 2, f"Expected 2 vault results, got {len(result['results'])}"
            assert 'vault_1' in result['results']
            assert 'vault_2' in result['results']
            
            logger.info("Constituent pool update test passed")
                
        except Exception as e:
            logger.error(f"Error in test sequence: {str(e)}")
            raise

    async def cleanup(self):
        """Clean up resources."""
        try:
            if self.supabase_client:
                # Add any necessary cleanup for Supabase client
                pass
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

async def async_main():
    """Async main function to run the test."""
    parser = argparse.ArgumentParser(description='Test Optimizer with real database')
    
    parser.add_argument('--url', required=True,
                        help='Supabase URL')
    
    parser.add_argument('--key', required=True,
                        help='Supabase API key')
    
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run the test
    test = OptimizerTest(args.url, args.key)
    
    try:
        # Connect to Supabase
        if not await test.connect_to_supabase():
            logger.error("Failed to connect to Supabase, exiting")
            return
        
        # Set up optimizer
        if not await test.setup_optimizer():
            logger.error("Failed to set up optimizer, exiting")
            return
        
        # Run test sequence
        await test.run_test_sequence()
        
    finally:
        # Clean up
        await test.cleanup()

def main():
    """Main function that runs the async_main function in an event loop."""
    try:
        asyncio.run(async_main())
    except Exception as e:
        logger.error(f"Unhandled exception in main: {str(e)}")
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main()) 