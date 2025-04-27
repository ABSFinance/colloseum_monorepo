"""
Evaluator System Test with Real Database

This script tests the Evaluator system using a real database connection.
It inserts mock vault and allocation data, then tests the portfolio reallocation flow
based on optimization results.
"""

import sys
import os
import time
import argparse
import logging
import json
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List, Optional
import uuid
import asyncio
import random
# Import the Supabase client module
from supabase import create_async_client, AsyncClient

# Add the parent directory to the Python path to allow importing from the core module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import evaluator components
from src.evaluator.evaluator import Evaluator
from src.optimizer.optimizer import Optimizer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EvaluatorDBTest:
    """Test harness for evaluator system with real database connection."""

    def __init__(self, supabase_url: str, supabase_key: str, use_zmq: bool = True, zmq_address: str = "tcp://*:5556"):
        """Initialize the test harness.
        
        Args:
            supabase_url: Supabase URL for connection
            supabase_key: Supabase API key for authentication
            use_zmq: Whether to use ZMQ for message publishing
            zmq_address: ZMQ binding address (default: tcp://*:5556 to avoid conflicts)
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_client = None
        
        # ZMQ configuration
        self.use_zmq = use_zmq
        self.zmq_address = zmq_address
        
        # Initialize evaluator, optimizer, and vault data
        self.evaluator = None
        self.optimizer = None
        
        # Test data
        # Use a high ID to avoid conflicts with existing vaults
        self.test_vault_id = 100099  
        
        # Common lending pool IDs that likely exist in the database
        # These should be real pools that already exist in the database
        self.test_allocation_pools = [28, 29, 1071, 1088, 1105]  
        
        self.test_records = {
            'pool_info': [],
            'abs_vault_info': [],
            'abs_vault_allocation_history': [],
        }
        
        logger.info("EvaluatorDBTest initialized")
    
    async def connect_to_supabase(self):
        """Connect to Supabase and initialize the client."""
        try:
            # Create a client
            self.supabase_client = await create_async_client(
                self.supabase_url, 
                self.supabase_key
            )
            
            logger.info("Connected to Supabase successfully")
            return True
        except ImportError as e:
            # The supabase module is not installed
            logger.error(f"Supabase package not installed. Run 'pip install supabase>=2.0.0' to install it: {str(e)}")
            return False
        except Exception as e:
            # Handle other exceptions (connection issues, invalid credentials, etc.)
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            return False
    
    def setup_evaluator_system(self):
        """Set up the evaluator system with the database connection."""
        # Create evaluator and optimizer instances
        self.evaluator = Evaluator(supabase_client=self.supabase_client, reallocation_threshold=0.05)
        self.optimizer = Optimizer(supabase_client=self.supabase_client)
        
        # Initialize ZMQ publisher if enabled
        if self.use_zmq:
            self.evaluator.initialize_zmq_publisher(self.zmq_address)
            logger.info(f"Initialized ZMQ publisher at {self.zmq_address}")
        
        # Patch the evaluator's update_vault method to ensure consistent key handling
        original_update_vault = self.evaluator.update_vault
        
        def patched_update_vault(vault_info):
            """Patched version of update_vault that ensures consistent key types."""
            result = original_update_vault(vault_info)
            
            # Convert all vault keys to strings for consistent access
            # This helps avoid issues with int/string conversion
            vaults_copy = dict(self.evaluator.vaults)
            self.evaluator.vaults = {}
            
            for key, value in vaults_copy.items():
                self.evaluator.vaults[str(key)] = value
                
            return result
            
        # Apply the update_vault patch
        self.evaluator.update_vault = patched_update_vault
        
        # Patch run_reallocation_flow to handle key conversion safely
        original_run_reallocation = self.evaluator.run_reallocation_flow
        
        async def patched_run_reallocation(pool_id, optimization_result):
            """Patched version of run_reallocation_flow that handles key conversion safely."""
            try:
                # Convert pool_id to string to ensure consistency
                pool_id_str = str(pool_id)
                
                # Check if the pool exists in vaults
                if pool_id_str not in self.evaluator.vaults:
                    # Try to find the key with a different type
                    for key in self.evaluator.vaults.keys():
                        if str(key) == pool_id_str:
                            pool_id = key
                            break
                    else:
                        logger.error(f"Pool ID {pool_id_str} not found in vaults")
                        return {
                            'pool_id': pool_id,
                            'status': 'error',
                            'message': f"Unknown vault {pool_id_str}",
                            'timestamp': pd.Timestamp.now(UTC).isoformat()
                        }
                
                return await original_run_reallocation(pool_id, optimization_result)
            except Exception as e:
                logger.error(f"Error in run_reallocation_flow: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': str(e),
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
        # Apply the run_reallocation_flow patch
        self.evaluator.run_reallocation_flow = patched_run_reallocation
        
        logger.info("Evaluator system set up successfully with patched vault access")
    
    def generate_test_data(self):
        """Generate test data for all required tables."""
        try:
            now = datetime.now(UTC)
            
            # Generate pool_info record for the test vault
            # We don't create pool_info records for allocation pools as they should already exist
            pool_info_record = {
                'id': self.test_vault_id,
                'type': 'abs_vault',
                'created_at': now.isoformat(),
                'updated_at': now.isoformat(),
            }
            self.test_records['pool_info'].append(pool_info_record)
            
            # Generate vault info test data
            vault_record = {
                'name': f'test_vault_{self.test_vault_id}',
                'address': f'92choftJrxdnv4FXoau1JsvsCbRcWX8TsUrBcGjo38e{self.test_vault_id}',
                'pool_id': self.test_vault_id,
                'org_id': 377,
                'underlying_token': 'Sol11111111111111111111111111111111111111112',
                'capacity': 1000000.0,
                'adaptors': ['kamino-lend', 'drift-vault'],
                'allowed_pools': self.test_allocation_pools,
                'strategy': 'min_risk',  # or 'max_sharpe'
                'description': 'test_description',
                'created_at': now.isoformat(),
                'updated_at': now.isoformat(),
                'weight': [50, 50]  # Weight for each adaptor
            }
            self.test_records['abs_vault_info'].append(vault_record)
            
            # Generate current allocation data (current portfolio state)
            # Use realistic values that match the example
            current_allocation = {
                28: 100000.0,  # Using explicit float values for consistency
                29: 5858502.988240444,
                1071: 861284.8835517357,
                1088: 874894.7721451924,
                1105: 455947.6186058908
            }
            
            # Create allocation history records
            for allocated_pool_id, amount in current_allocation.items():
                allocation_record = {
                    'pool_id': self.test_vault_id,
                    'allocated_pool_id': allocated_pool_id,
                    'amount': float(amount),  # Ensure amount is a float
                    'created_at': now.isoformat()
                }
                self.test_records['abs_vault_allocation_history'].append(allocation_record)
            
            logger.info(f"Generated test data for vault {self.test_vault_id} with {len(self.test_allocation_pools)} allocation pools")
        except Exception as e:
            logger.error(f"Error generating test data: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    async def insert_test_data(self):
        """Insert all test data into the database."""
        if not self.supabase_client:
            logger.error("Supabase client not initialized")
            return False
        
        try:
            success = True
            
            # First check if test data already exists to avoid duplicates
            logger.info("Checking if test data already exists...")
            
            # Check for vault info
            try:
                vault_check = await self.supabase_client.table('abs_vault_info') \
                    .select('pool_id') \
                    .eq('pool_id', self.test_vault_id) \
                    .execute()
                    
                if vault_check.data and len(vault_check.data) > 0:
                    logger.info(f"Test vault {self.test_vault_id} already exists, cleaning up first")
                    # Clean up existing test data
                    await self.clean_up_test_data()
            except Exception as e:
                logger.warning(f"Error checking for existing vault: {str(e)}")
            
            # Insert test data in proper order (pool_info first, then vault, then allocations)
            logger.info("Inserting pool_info records...")
            
            # Insert pool_info records
            for record in self.test_records['pool_info']:
                try:
                    response = await self.supabase_client.table('pool_info').insert(record).execute()
                    if not response.data:
                        logger.warning(f"Failed to insert pool_info record: {record}")
                        success = False
                except Exception as e:
                    logger.error(f"Error inserting pool_info record: {str(e)}")
                    success = False
            
            # Add delay to ensure pool_info is fully inserted
            await asyncio.sleep(1)
            
            logger.info("Inserting abs_vault_info records...")
            # Insert abs_vault_info records
            for record in self.test_records['abs_vault_info']:
                try:
                    response = await self.supabase_client.table('abs_vault_info').insert(record).execute()
                    if not response.data:
                        logger.warning(f"Failed to insert abs_vault_info record: {record}")
                        success = False
                except Exception as e:
                    logger.error(f"Error inserting abs_vault_info record: {str(e)}")
                    success = False
            
            # Add delay to ensure vault_info is fully inserted
            await asyncio.sleep(1)
            
            logger.info("Inserting abs_vault_allocation_history records...")
            # Insert abs_vault_allocation_history records
            for record in self.test_records['abs_vault_allocation_history']:
                try:
                    response = await self.supabase_client.table('abs_vault_allocation_history').insert(record).execute()
                    if not response.data:
                        logger.warning(f"Failed to insert abs_vault_allocation_history record: {record}")
                        success = False
                except Exception as e:
                    logger.error(f"Error inserting abs_vault_allocation_history record: {str(e)}")
                    success = False
            
            # Add delay after insertion to ensure data is fully processed
            await asyncio.sleep(2)
            
            logger.info(f"Test data insertion completed {'successfully' if success else 'with errors'}")
            return success
        except Exception as e:
            logger.error(f"Unexpected error during data insertion: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def clean_up_test_data(self):
        """Clean up all test data from the database."""
        if not self.supabase_client:
            logger.error("Supabase client not initialized")
            return False
        
        try:
            success = True
            
            # Delete in reverse order of creation (allocation history first, then vault info, then pool info)
            # This respects foreign key constraints
            
            # 1. Delete allocation history records
            logger.info(f"Deleting allocation history for vault {self.test_vault_id}")
            try:
                await self.supabase_client.table('abs_vault_allocation_history') \
                    .delete() \
                    .eq('pool_id', self.test_vault_id) \
                    .execute()
            except Exception as e:
                logger.error(f"Error deleting allocation history: {str(e)}")
                success = False
                
            # Add a small delay
            await asyncio.sleep(1)
            
            # 2. Delete vault info records
            logger.info(f"Deleting vault info for vault {self.test_vault_id}")
            try:
                await self.supabase_client.table('abs_vault_info') \
                    .delete() \
                    .eq('pool_id', self.test_vault_id) \
                    .execute()
            except Exception as e:
                logger.error(f"Error deleting vault info: {str(e)}")
                success = False
                
            # Add a small delay
            await asyncio.sleep(1)
            
            # 3. Delete pool info records
            logger.info(f"Deleting pool info for ID {self.test_vault_id}")
            try:
                await self.supabase_client.table('pool_info') \
                    .delete() \
                    .eq('id', self.test_vault_id) \
                    .execute()
            except Exception as e:
                logger.error(f"Error deleting pool info: {str(e)}")
                success = False
            
            logger.info(f"Test data cleanup completed {'successfully' if success else 'with errors'}")
            return success
            
        except Exception as e:
            logger.error(f"Unexpected error during cleanup: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    async def run_evaluator_test(self):
        """Run the main evaluator test by initializing and testing reallocation flow."""
        # 1. Initialize the vault info in the evaluator
        logger.info("Initializing vault information in evaluator...")
        await self.evaluator.initialize_vault_info()
        
        # 2. Check if vault info was loaded correctly
        # Convert both the test_vault_id and keys to strings for consistent comparison
        vault_id_str = str(self.test_vault_id)
        
        # Detailed debug information about vaults dictionary
        logger.info(f"Evaluator has {len(self.evaluator.vaults)} vaults")
        logger.info(f"Vault types: {[type(k) for k in self.evaluator.vaults.keys()]}")
        logger.info(f"First few vault keys: {list(self.evaluator.vaults.keys())[:5]}")
        
        # Check if the vault is in the keys
        vault_keys = [str(key) for key in self.evaluator.vaults.keys()]
        int_keys = [int(key) if str(key).isdigit() else key for key in self.evaluator.vaults.keys()]
        
        logger.info(f"Available vaults (str): {vault_keys}")
        logger.info(f"Available vaults (int): {int_keys}")
        
        # Try multiple ways to access the vault data
        vault_data = None
        
        # Try as string
        if vault_id_str in self.evaluator.vaults:
            logger.info(f"Found vault with string key: {vault_id_str}")
            vault_data = self.evaluator.vaults[vault_id_str]
        # Try as int
        elif self.test_vault_id in self.evaluator.vaults:
            logger.info(f"Found vault with int key: {self.test_vault_id}")
            vault_data = self.evaluator.vaults[self.test_vault_id]
        # Try all keys
        else:
            for key in self.evaluator.vaults.keys():
                try:
                    if str(key) == vault_id_str:
                        logger.info(f"Found matching vault with key: {key} (type: {type(key)})")
                        vault_data = self.evaluator.vaults[key]
                        break
                except Exception as e:
                    logger.error(f"Error when comparing key {key}: {str(e)}")
        
        # Check if we found the vault data
        if vault_data is None:
            logger.error(f"Failed to find vault info for test vault {self.test_vault_id}")
            logger.error(f"Available vault IDs: {vault_keys}")
            return False
        
        logger.info(f"Successfully loaded vault info for test vault {self.test_vault_id}")
        logger.info(f"Vault data: {vault_data}")
        
        # 3. Check current allocation - safely get with appropriate key
        current_allocation = vault_data.get('current_allocation', {})
        if not current_allocation:
            logger.error("Failed to load current allocation for test vault")
            logger.error(f"Vault data keys: {vault_data.keys()}")
            return False
        
        logger.info(f"Current allocation: {current_allocation}")
        
        # 4. Create test optimization result (simulating optimizer output)
        # Use mixed allocation changes to test median-based utilization calculation
        optimization_result = {
            'pool_id': str(self.test_vault_id),  # Use string for pool_id to match evaluator expectation
            'allocation': {
                # Create a mix of over-allocations and under-allocations to test median calculation
                int(28): float(200000.0),        # 2x of original (~100K) - over-allocated
                int(29): float(2900000.0),       # Half of original (~5.8M) - under-allocated
                int(1071): float(861284.0),      # Same as original (~861K) - perfectly allocated
                int(1088): float(1800000.0),     # 2x of original (~874K) - over-allocated
                int(1105): float(227000.0)       # Half of original (~455K) - under-allocated
            },
            'status': 'success',
            'timestamp': datetime.now(UTC).isoformat()
        }
        
        logger.info(f"Test optimization result: {optimization_result}")
        
        # 5. Run the reallocation flow
        logger.info("Running reallocation flow...")
        try:
            reallocation_result = await self.evaluator.run_reallocation_flow(
                vault_id_str, optimization_result  # Use the consistent string vault ID
            )
            
            logger.info(f"Reallocation result: {json.dumps(reallocation_result, indent=2)}")
            
            # 6. Validate the result
            if reallocation_result.get('status') != 'success':
                logger.error(f"Reallocation failed with status: {reallocation_result.get('status')}")
                logger.error(f"Error message: {reallocation_result.get('message', 'No error message provided')}")
                return False
            
            # Check if reallocation was needed and performed
            if not reallocation_result.get('reallocation_needed', False):
                logger.error("Reallocation was expected to be needed but was not performed")
                return False
            
            # Log utilization metrics to verify the median calculation
            evaluation_result = reallocation_result.get('evaluation_result', {})
            utilization_metrics = evaluation_result.get('utilization_metrics', {})
            
            if utilization_metrics:
                overall_util = utilization_metrics.get('overall', 0.0)
                logger.info(f"Overall utilization (median): {overall_util:.4f}")
                
                # Log individual asset utilizations
                asset_utils = utilization_metrics.get('by_asset', [])
                if asset_utils:
                    utils_formatted = "\n".join([f"  Asset {asset['asset']}: {asset['utilization']:.4f}" for asset in asset_utils])
                    logger.info(f"Individual asset utilizations:\n{utils_formatted}")
                    
                    # Calculate what the median should be for verification
                    util_values = [asset['utilization'] for asset in asset_utils if asset['utilization'] != float('inf')]
                    if util_values:
                        expected_median = sorted(util_values)[len(util_values)//2] if len(util_values) % 2 == 1 else \
                                        (sorted(util_values)[len(util_values)//2-1] + sorted(util_values)[len(util_values)//2])/2
                        logger.info(f"Expected median utilization: {expected_median:.4f}")
                        
                        # Verify that the overall utilization is close to the expected median
                        if abs(overall_util - expected_median) > 0.0001:
                            logger.error(f"Overall utilization {overall_util:.4f} does not match expected median {expected_median:.4f}")
            
            logger.info("Reallocation flow test completed successfully")
            
            # 7. Verify the reallocation actions
            reallocation_actions = evaluation_result.get('reallocation_actions', [])
            
            if not reallocation_actions:
                logger.error("No reallocation actions were generated")
                return False
            
            # Format the actions for logging
            actions_formatted = "\n".join([f"  Pool {action['pool_id']}: {action['amount']:,.2f}" for action in reallocation_actions])
            logger.info(f"Reallocation actions generated:\n{actions_formatted}")
            
            # 8. Check if allocation was updated in the evaluator - use the same key that worked before
            try:
                # Access vaults with the same key that worked earlier
                updated_vault_data = None
                for key in self.evaluator.vaults.keys():
                    try:
                        if str(key) == vault_id_str:
                            updated_vault_data = self.evaluator.vaults[key]
                            break
                    except Exception:
                        pass
                
                if updated_vault_data is None:
                    logger.error(f"Could not find the vault in evaluator.vaults after reallocation")
                    return False
                
                new_allocation = updated_vault_data.get('current_allocation', {})
                logger.info(f"Updated allocation: {new_allocation}")
                
                # Verify at least the pool 28 allocation changed significantly (should be much lower)
                if 28 in new_allocation and 28 in current_allocation:
                    old_value = current_allocation[28]
                    new_value = new_allocation[28]
                    logger.info(f"Pool 28 allocation changed from {old_value} to {new_value}")
                    
                    # It should be significantly lower
                    if new_value > old_value * 0.5:  # Expecting at least 50% reduction
                        logger.error(f"Pool 28 allocation didn't decrease significantly: {old_value} -> {new_value}")
                else:
                    logger.warning(f"Pool 28 not found in either current or new allocation, can't verify change")
            
            except Exception as e:
                logger.error(f"Error verifying allocation update: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error during reallocation flow: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False

async def async_main():
    """Main async function to run the test."""
    parser = argparse.ArgumentParser(description='Test the Evaluator with a real database connection')
    parser.add_argument('--url', required=True, help='Supabase URL')
    parser.add_argument('--key', required=True, help='Supabase service role key')
    parser.add_argument('--no-zmq', action='store_true', help='Disable ZMQ publishing')
    parser.add_argument('--zmq-address', default="tcp://*:5556", help='ZMQ binding address')
    parser.add_argument('--cleanup', action='store_true', help='Clean up test data after testing')
    parser.add_argument('--insert-only', action='store_true', help='Only insert test data without running tests')
    parser.add_argument('--skip-insert', action='store_true', help='Skip test data insertion (use existing data)')
    parser.add_argument('--vault-id', type=int, help='Custom vault ID to use for testing')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    logger.info(f"Starting evaluator test with ZMQ {'disabled' if args.no_zmq else 'enabled'}")
    
    # Create and run the test
    test = EvaluatorDBTest(
        supabase_url=args.url,
        supabase_key=args.key,
        use_zmq=not args.no_zmq,
        zmq_address=args.zmq_address
    )
    
    # Set custom vault ID if provided
    if args.vault_id:
        test.test_vault_id = args.vault_id
        logger.info(f"Using custom vault ID: {test.test_vault_id}")
    
    try:
        # Connect to Supabase
        if not await test.connect_to_supabase():
            logger.error("Failed to connect to Supabase. Exiting.")
            return False
        
        logger.info("Connected to Supabase successfully")
        
        # Setup the evaluator system
        test.setup_evaluator_system()
        logger.info("Evaluator system set up successfully")
        
        # Generate test data
        logger.info("Generating test data...")
        test.generate_test_data()
        logger.info("Test data generated successfully")
        
        # Insert test data if not skipped
        if not args.skip_insert:
            logger.info("Inserting test data into database...")
            if not await test.insert_test_data():
                logger.error("Failed to insert test data. Exiting.")
                return False
            
            logger.info("Test data inserted successfully")
            
            if args.insert_only:
                logger.info("Insert only mode. Exiting without running tests.")
                return True
        else:
            logger.info("Skipping test data insertion as requested")
        
        # Run the evaluator test
        logger.info("Running evaluator reallocation flow test...")
        test_success = await test.run_evaluator_test()
        
        if test_success:
            logger.info("Evaluator reallocation flow test PASSED")
        else:
            logger.error("Evaluator reallocation flow test FAILED")
        
        # Clean up test data if requested
        if args.cleanup:
            logger.info("Cleaning up test data...")
            cleanup_success = await test.clean_up_test_data()
            logger.info(f"Test data cleanup {'succeeded' if cleanup_success else 'failed'}")
        
        return test_success
    
    except Exception as e:
        logger.error(f"Unexpected error during test execution: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Try to clean up test data on error if requested
        if args.cleanup:
            try:
                logger.info("Attempting to clean up test data after error...")
                await test.clean_up_test_data()
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup after failure: {str(cleanup_error)}")
        
        return False

def main():
    """Main function to run the test."""
    try:
        success = asyncio.run(async_main())
        if success:
            logger.info("Test completed successfully")
            sys.exit(0)
        else:
            logger.error("Test failed")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Test interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 