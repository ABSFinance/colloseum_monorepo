"""
Observer System Test with Real Database

This script tests the Observer system using a real database connection.
It inserts mock data into the relevant tables and monitors how the
events flow through the system.
"""

import sys
import os
import time
import argparse
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import uuid
import asyncio

# Add the parent directory to the Python path to allow importing from the core module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import observatory components
from src.observer import EventTypes, ObserverManager
from src.observer.market_data_observable import MarketDataObservable
from src.observer.portfolio_state_observable import PortfolioStateObservable
from src.observer.vault_observable import VaultObservable
# Import TestObserver from test_observer.py in the same directory
from test_observer import TestObserver

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ObserverDBTest:
    """Test harness for observer system with real database connection."""

    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize the test harness.
        
        Args:
            supabase_url: Supabase URL for connection
            supabase_key: Supabase API key for authentication
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_client = None
        
        # Initialize observables and observers
        self.observer_manager = ObserverManager()
        self.test_observer = TestObserver(log_level="INFO")
        
        # Test data
        self.test_pools = []
        self.test_records = {
            'performance_history': [],
            'abs_vault_allocation_history': [],
            'abs_vault_info': []
        }
        
        # Initialize the observer object 
        self.observer = None
        
        # Initialize a flag to indicate whether we're listening for events
        self.is_listening = False
        
        logger.info("ObserverDBTest initialized")
    
    def connect_to_supabase(self):
        """Connect to Supabase and initialize the client."""
        try:
            # Import the Supabase client module
            from supabase import create_async_client
            
            # Create a client with realtime enabled
            self.supabase_client = create_async_client(
                self.supabase_url, 
                self.supabase_key,
                options={
                    "realtime": {
                        "enabled": True
                    },
                }
            )

            logger.info(f"Supabase client type: {type(self.supabase_client)}")
            logger.info(f"Supabase client attributes and methods: {dir(self.supabase_client)}")

            
            # Check if the client has the necessary channel method for realtime
            if not hasattr(self.supabase_client, 'channel'):
                logger.error("Supabase client does not have 'channel' method for realtime functionality")
                logger.error("Make sure you're using supabase-py>=2.0.0 and have properly configured the client")
                return False
                
            logger.info("Connected to Supabase successfully with realtime-capable client")
            return True
        except ImportError as e:
            # The supabase module is not installed
            logger.error(f"Supabase package not installed. Run 'pip install supabase>=2.0.0' to install it: {str(e)}")
            return False
        except Exception as e:
            # Handle other exceptions (connection issues, invalid credentials, etc.)
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            return False
    
    def setup_observer_system(self):
        """Set up the observer system with the test observer."""
        # Create observables
        market_data_observable = MarketDataObservable()
        portfolio_state_observable = PortfolioStateObservable()
        vault_observable = VaultObservable()
        
        # Register observables with the manager
        self.observer_manager.register_observable('market_data', market_data_observable)
        self.observer_manager.register_observable('portfolio_state', portfolio_state_observable)
        self.observer_manager.register_observable('vault', vault_observable)
        
        # Register test observer for all event types
        # Market data events
        self.observer_manager.register_observer(
            'market_data', EventTypes.NEW_PERFORMANCE_HISTORY_RECORD, 
            self.test_observer.handle_new_performance_history_record
        )
        
        # Portfolio state events
        self.observer_manager.register_observer(
            'portfolio_state', EventTypes.DEPOSIT_EVENT, 
            self.test_observer.handle_deposit_event
        )
        self.observer_manager.register_observer(
            'portfolio_state', EventTypes.WITHDRAWAL_EVENT, 
            self.test_observer.handle_withdrawal_event
        )
        
        # Vault info events
        self.observer_manager.register_observer(
            'vault', EventTypes.VAULT_INFO_RECORD, 
            self.test_observer.handle_vault_info_record
        )
        
        logger.info("Observer system set up successfully")
    
    def generate_test_pools(self, num_pools: int = 2):
        """Generate test pool data.
        
        Args:
            num_pools: Number of test pools to create
        """
        self.test_pools = []
        for i in range(num_pools):
            pool_id = f"test_pool_{i}_{str(uuid.uuid4())[:8]}"
            self.test_pools.append(pool_id)
        
        logger.info(f"Generated {num_pools} test pools: {self.test_pools}")
    
    def generate_test_data(self):
        """Generate test data for all tables."""
        if not self.test_pools:
            logger.warning("No test pools defined, generating default pools")
            self.generate_test_pools()
        
        now = datetime.now()
        
        # Generate performance history test data
        for pool_id in self.test_pools:
            # Create 3 performance records for each pool with different timestamps
            for i in range(3):
                timestamp = now - timedelta(hours=i)
                record = {
                    'pool_id': pool_id,
                    'timestamp': timestamp.isoformat(),
                    'apy': 0.05 + (i * 0.01),  # Slightly different APY values
                    'tvl': 1000000.0 - (i * 50000.0),  # Slightly different TVL values
                }
                self.test_records['performance_history'].append(record)
        
        # Generate allocation history test data
        for pool_id in self.test_pools:
            # Create a deposit record (pool_id equals allocated_pool_id and amount > 0)
            deposit_record = {
                'pool_id': pool_id,
                'allocated_pool_id': pool_id,  # Same pool ID for deposit
                'amount': 5000.0,
                'status': 'completed',
                'timestamp': (now - timedelta(minutes=30)).isoformat(),
            }
            self.test_records['abs_vault_allocation_history'].append(deposit_record)
            
            # Create a withdrawal record (pool_id equals allocated_pool_id, amount < 0, status = 'pending')
            withdrawal_record = {
                'pool_id': pool_id,
                'allocated_pool_id': pool_id,  # Same pool ID for withdrawal
                'amount': -2000.0,
                'status': 'pending',
                'timestamp': now.isoformat(),
            }
            self.test_records['abs_vault_allocation_history'].append(withdrawal_record)
            
        # Generate vault info test data
        for pool_id in self.test_pools:
            vault_record = {
                'pool_id': pool_id,
                'strategy': 'BALANCED',
                'allowed_pools': self.test_pools,  # All pools allowed
                'updated_at': now.isoformat(),
                'created_at': (now - timedelta(days=1)).isoformat(),
            }
            self.test_records['abs_vault_info'].append(vault_record)
        
        logger.info(f"Generated test data: {json.dumps(self.test_records, indent=2, default=str)}")
    
    def insert_test_data(self, table_name: str, record: Dict[str, Any]) -> bool:
        """Insert a test record into the specified table.
        
        Args:
            table_name: Name of the table to insert into
            record: Record data to insert
            
        Returns:
            bool: Whether the insertion was successful
        """
        if not self.supabase_client:
            logger.error(f"Cannot insert data: Supabase client not initialized")
            return False
        
        try:
            # Create an event loop for async operations
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new event loop if the current one is already running
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                future = asyncio.run_coroutine_threadsafe(self._async_insert_test_data(table_name, record), new_loop)
                return future.result()  # Wait for the result
            else:
                # Use the current event loop
                return loop.run_until_complete(self._async_insert_test_data(table_name, record))
        except Exception as e:
            logger.error(f"Error inserting into {table_name}: {str(e)}")
            return False
    
    async def _async_insert_test_data(self, table_name: str, record: Dict[str, Any]) -> bool:
        """Async version of insert_test_data for async Supabase client."""
        try:
            response = await self.supabase_client.table(table_name).insert(record).execute()
            data = response.data
            if data:
                record_id = data[0].get('id')
                if record_id:
                    # Store the ID in the original record for later cleanup
                    record['id'] = record_id
                logger.info(f"Successfully inserted record into {table_name}: {record_id}")
                return True
            else:
                logger.warning(f"Insertion into {table_name} did not return data")
                return False
        except Exception as e:
            logger.error(f"Error inserting into {table_name}: {str(e)}")
            return False
    
    def manually_trigger_event(self, observable_name: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """Manually trigger an event for testing.
        
        Args:
            observable_name: Name of the observable to trigger the event on
            event_type: Type of event to trigger
            event_data: Data for the event
        """
        try:
            # Get the observable
            observable = self.observer_manager.get_observable(observable_name)
            
            # Notify with the event
            observable.notify(event_type, event_data)
            
            logger.info(f"Manually triggered {event_type} event on {observable_name}")
        except Exception as e:
            logger.error(f"Error triggering event {event_type}: {str(e)}")

    def run_test_sequence(self, delay_between_inserts: float = 2.0, cleanup_after_test: bool = True):
        """Run a test sequence by inserting test data and monitoring events.
        
        Args:
            delay_between_inserts: Delay in seconds between insert operations
            cleanup_after_test: Whether to clean up test data after the test
        """
        if not self.is_listening:
            logger.error("Cannot run test: Supabase listener not started")
            return
        
        logger.info("Starting test sequence")
        
        # Clear any previous test events
        self.test_observer.clear()
        
        try:
            # Insert performance history records
            for i, record in enumerate(self.test_records['performance_history']):
                logger.info(f"Inserting performance history record {i+1}/{len(self.test_records['performance_history'])}")
                self.insert_test_data('performance_history', record)
                time.sleep(delay_between_inserts)  # Wait for events to propagate
            
            # Insert allocation history records
            for i, record in enumerate(self.test_records['abs_vault_allocation_history']):
                logger.info(f"Inserting allocation history record {i+1}/{len(self.test_records['abs_vault_allocation_history'])}")
                self.insert_test_data('abs_vault_allocation_history', record)
                time.sleep(delay_between_inserts)  # Wait for events to propagate
            
            # Insert vault info records
            for i, record in enumerate(self.test_records['abs_vault_info']):
                logger.info(f"Inserting vault info record {i+1}/{len(self.test_records['abs_vault_info'])}")
                self.insert_test_data('abs_vault_info', record)
                time.sleep(delay_between_inserts)  # Wait for events to propagate
            
            # Wait a bit longer for all events to propagate
            logger.info(f"Waiting for final events to propagate...")
            time.sleep(delay_between_inserts * 2)
            
            # Print event summary
            self.test_observer.print_event_summary()
            
            # Print events for each pool
            for pool_id in self.test_pools:
                print(f"\nEvents for pool {pool_id}:")
                self.test_observer.print_event_details(pool_id=pool_id)
            
            logger.info("Test sequence completed")
            
        finally:
            # Clean up test data if requested
            if cleanup_after_test:
                logger.info("Cleaning up test data...")
                self.clean_up_test_data()

    def cleanup(self):
        """Clean up resources and connections."""
        # Stop the Observer
        if self.observer and self.is_listening:
            try:
                self.observer.stop()
                self.is_listening = False
                logger.info("Observer stopped")
            except Exception as e:
                logger.error(f"Error stopping Observer: {str(e)}")
                
        # Make sure any remaining test data is cleaned up
        # This is a safety measure in case the test was interrupted before cleanup
        try:
            self.clean_up_test_data()
        except Exception as e:
            logger.error(f"Error during final cleanup of test data: {str(e)}")

    def clean_up_test_data(self):
        """Clean up test data from the database after test completion."""
        logger.info("Cleaning up test data from database...")
        
        if not self.supabase_client:
            logger.warning("Cannot clean up test data: Supabase client not initialized")
            return False
            
        try:
            # Clean up performance history records
            for record in self.test_records['performance_history']:
                if 'id' in record:  # We can only delete records with IDs
                    self.delete_test_record('performance_history', record['id'])
            
            # Clean up allocation history records
            for record in self.test_records['abs_vault_allocation_history']:
                if 'id' in record:
                    self.delete_test_record('abs_vault_allocation_history', record['id'])
            
            # Clean up vault info records
            for record in self.test_records['abs_vault_info']:
                if 'id' in record:
                    self.delete_test_record('abs_vault_info', record['id'])
            
            logger.info("Test data cleanup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up test data: {str(e)}")
            return False
            
    def delete_test_record(self, table_name: str, record_id: str) -> bool:
        """Delete a test record from the specified table.
        
        Args:
            table_name: Name of the table to delete from
            record_id: ID of the record to delete
            
        Returns:
            bool: Whether the deletion was successful
        """
        if not self.supabase_client:
            logger.error(f"Cannot delete data: Supabase client not initialized")
            return False
        
        try:
            # Create an event loop for async operations
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new event loop if the current one is already running
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                future = asyncio.run_coroutine_threadsafe(self._async_delete_test_record(table_name, record_id), new_loop)
                return future.result()  # Wait for the result
            else:
                # Use the current event loop
                return loop.run_until_complete(self._async_delete_test_record(table_name, record_id))
        except Exception as e:
            logger.error(f"Error deleting from {table_name}: {str(e)}")
            return False
    
    async def _async_delete_test_record(self, table_name: str, record_id: str) -> bool:
        """Async version of delete_test_record for async Supabase client."""
        try:
            response = await self.supabase_client.table(table_name).delete().eq('id', record_id).execute()
            data = response.data
            if data:
                logger.info(f"Successfully deleted record from {table_name}: {record_id}")
                return True
            else:
                logger.warning(f"Deletion from {table_name} did not return data for record {record_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting from {table_name}: {str(e)}")
            return False

    def setup_supabase_listener(self):
        """Set up the Supabase listener to monitor database changes."""
        if not self.supabase_client:
            logger.error("Cannot set up listener: Supabase client not initialized")
            return False
        
        try:
            # Import the Observer class from observer.py
            from src.observer.observer import Observer
            
            # Check if supabase_client is properly configured for realtime
            if not hasattr(self.supabase_client, 'channel'):
                logger.error("Cannot set up listener: Supabase client does not have channel method")
                return False
                
            # Create and start the Observer with our Supabase client
            self.observer = Observer(
                supabase_client=self.supabase_client,
                observer_manager=self.observer_manager,
                market_data_table='performance_history',
                portfolio_state_table='abs_vault_allocation_history',
                vault_info_table='abs_vault_info'
            )
            
            # Start the Observer (this will set up the listeners)
            self.observer.start()
            self.is_listening = True
            logger.info("Observer started successfully with realtime capabilities")
            return True
        except Exception as e:
            logger.error(f"Failed to set up Observer: {str(e)}")
            return False

def main():
    """Main function to run the test."""
    parser = argparse.ArgumentParser(description='Test Observer system with real database for standard events: performance history, allocation history, and vault info')
    
    parser.add_argument('--url', required=True,
                        help='Supabase URL')
    
    parser.add_argument('--key', required=True,
                        help='Supabase API key')
    
    parser.add_argument('--pools', type=int, default=2,
                        help='Number of test pools to create')
    
    parser.add_argument('--delay', type=float, default=2.0,
                        help='Delay in seconds between insert operations')
    
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
                        
    parser.add_argument('--no-cleanup', action='store_true',
                        help='Disable automatic cleanup of test data (for debugging)')
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run the test
    test = ObserverDBTest(args.url, args.key)
    
    try:
        # Connect to Supabase
        if not test.connect_to_supabase():
            logger.error("Failed to connect to Supabase, exiting")
            return
        
        # Set up observer system
        test.setup_observer_system()
        
        # Set up Supabase listener
        if not test.setup_supabase_listener():
            logger.error("Failed to set up Supabase listener, exiting")
            return
        
        # Generate test data
        test.generate_test_pools(args.pools)
        test.generate_test_data()
        
        # Run test sequence
        test.run_test_sequence(args.delay, not args.no_cleanup)
    finally:
        # Clean up
        test.cleanup()

if __name__ == '__main__':
    main() 