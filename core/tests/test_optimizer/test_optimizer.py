import pytest
import pandas as pd
import numpy as np
import asyncio
import logging
import argparse
import sys
from datetime import datetime, timedelta
from supabase import create_async_client, AsyncClient
from core.src.optimizer.optimizer import Optimizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            # Test market data initialization
            pool_id = '1000'
            days = 30
            await self.optimizer.initialize_market_data(pool_id, days)
            
            # Verify market data was fetched
            assert pool_id in self.optimizer.market_data
            assert isinstance(self.optimizer.market_data[pool_id], pd.DataFrame)
            assert not self.optimizer.market_data[pool_id].empty
            
            logger.info("Market data initialization test passed")
            
            # Test vault initialization and optimization
            vault_info = {
                'pool_id': 'vault_1',
                'strategy': 'min_risk',
                'allowed_pools': ['1000', '1010'],
                'adaptors': ['adaptor1', 'adaptor2'],
                'weights': [0.6, 0.4]
            }
            
            self.optimizer.initialize_vault(vault_info)
            result = self.optimizer.handle_market_data({
                'pool_id': 'vault_1',
                'created_at': datetime.now().isoformat(),
                'return': 0.02
            })
            
            assert isinstance(result, dict)
            assert 'pool_id' in result
            assert 'allocation' in result
            assert 'timestamp' in result
            
            logger.info("Vault optimization test passed")
            
        except Exception as e:
            logger.error(f"Error during test sequence: {str(e)}")
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