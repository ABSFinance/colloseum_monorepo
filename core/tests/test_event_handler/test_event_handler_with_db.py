"""
Event Handler System Test with Real Database

This script tests the EventHandler system using a real database connection.
It inserts mock data into the relevant tables and monitors how the
events flow through the entire system.
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
import zmq
from supabase import create_async_client, AsyncClient

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import event handler components
from src.event.event_handler import EventHandler
from src.observer import EventTypes, ObserverManager
from src.observer.market_data_observable import MarketDataObservable
from src.observer.portfolio_state_observable import PortfolioStateObservable
from src.observer.vault_observable import VaultObservable
from src.observer.logging_observer import LoggingObserver

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EventHandlerDBTest:
    """Test harness for event handler system with real database connection."""

    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize the test harness.
        
        Args:
            supabase_url: Supabase URL for connection
            supabase_key: Supabase API key for authentication
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_client = None
        
        # Initialize services and config
        self.services = {}
        self.config = {
            'logging': {
                'log_level': 'INFO',
                'include_data': True
            },
            'observer': {
                'market_data_table': 'performance_history',
                'portfolio_state_table': 'abs_vault_allocation_history',
                'vault_info_table': 'abs_vault_info'
            },
            'zmq': {
                'enabled': True,
                'pub_address': 'tcp://*:5555'
            }
        }
        
        # Test data
        self.test_pools = []
        self.test_records = {
            'pool_info': [],
            'performance_history': [],
            'abs_vault_allocation_history': [],
            'abs_vault_info': []
        }
        
        # Initialize the event handler
        self.event_handler = None
        
        logger.info("EventHandlerDBTest initialized")
    
    async def connect_to_supabase(self):
        """Connect to Supabase and initialize the client."""
        try:
            # Create a client with realtime enabled
            self.supabase_client: AsyncClient = await create_async_client(
                self.supabase_url, 
                self.supabase_key,
            )
            
            # Store in services
            self.services['supabase_service'] = self.supabase_client
                
            logger.info("Connected to Supabase successfully with realtime-capable client")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            return False
    
    def setup_zmq(self):
        """Set up ZeroMQ publisher."""
        try:
            context = zmq.Context()
            publisher = context.socket(zmq.PUB)
            publisher.bind(self.config['zmq']['pub_address'])
            self.services['zmq_publisher'] = publisher
            logger.info("ZeroMQ publisher set up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set up ZeroMQ: {str(e)}")
            return False
    
    async def setup_event_handler(self):
        """Set up the event handler system."""
        try:
            # Create and initialize the event handler
            self.event_handler = EventHandler(self.services, self.config)
            await self.event_handler.setup()
            logger.info("Event handler set up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set up event handler: {str(e)}")
            return False
    
    def generate_test_pools(self, num_pools: int = 2):
        """Generate test pool data."""
        self.test_pools = []
        for i in range(num_pools):
            pool_id = random.randint(1000000, 10000000)
            self.test_pools.append(pool_id)
        
        logger.info(f"Generated {num_pools} test pools: {self.test_pools}")
    
    def generate_test_data(self):
        """Generate test data for all tables."""
        if not self.test_pools:
            logger.warning("No test pools defined, generating default pools")
            self.generate_test_pools()
        
        now = datetime.now(UTC)

        # Generate pool info test data
        for pool_id in self.test_pools:
            pool_info_record = {
                'id': pool_id,
                'type': 'abs_vault',
                'created_at': now.isoformat(),
                'updated_at': now.isoformat(),
            }
            self.test_records['pool_info'].append(pool_info_record)
            
        # Generate vault info test data
        for pool_id in self.test_pools:
            vault_record = {
                'name': f'test_vault_{pool_id}',
                'address': f'92choftJrxdnv4FXoau1JsvsCbRcWX8TsUrBcGjo38e{pool_id}',
                'pool_id': pool_id,
                'org_id': 377,
                'underlying_token': 'Sol11111111111111111111111111111111111111112',
                'capacity': 1000000.0,
                'adaptors': ['kamino-lend', 'drift-vault'],
                'allowed_pools': [1105, 1088],
                'description': 'test_description',
                'created_at': now.isoformat(),
                'updated_at': now.isoformat(),
            }
            self.test_records['abs_vault_info'].append(vault_record)

        pool_ids = [1105, 1088, 1074]
        
        # Generate performance history test data
        for pool_id in pool_ids:
            for i in range(3):
                timestamp = now - timedelta(hours=i)
                record = {
                    'pool_id': pool_id,
                    'created_at': timestamp.isoformat(),
                    'apy': 0.05 + (i * 0.01),
                    'tvl': 1000000.0 - (i * 50000.0),
                }
                self.test_records['performance_history'].append(record)
        
        # Generate allocation history test data
        for pool_id in self.test_pools:
            # Deposit record
            deposit_record = {
                'pool_id': pool_id,
                'allocated_pool_id': pool_id,
                'amount': 5000.0,
                'status': 'COMPLETED',
                'created_at': (now - timedelta(minutes=30)).isoformat(),
            }
            self.test_records['abs_vault_allocation_history'].append(deposit_record)
            
            # Withdrawal record
            withdrawal_record = {
                'pool_id': pool_id,
                'allocated_pool_id': pool_id,
                'amount': -2000.0,
                'status': 'PENDING',
                'created_at': now.isoformat(),
            }
            self.test_records['abs_vault_allocation_history'].append(withdrawal_record)

    async def insert_test_data(self, table_name: str, record: Dict[str, Any]) -> bool:
        """Insert a test record into the specified table."""
        if not self.supabase_client:
            logger.error(f"Cannot insert data: Supabase client not initialized")
            return False

        try:
            response = await self.supabase_client.table(table_name).insert(record).execute()
            data = response.data
            if data:
                record_id = data[0].get('id')
                if record_id:
                    record['id'] = record_id
                logger.info(f"Successfully inserted record into {table_name}: {record_id}")
                return True
            else:
                logger.warning(f"Insertion into {table_name} did not return data")
                return False
        except Exception as e:
            logger.error(f"Error inserting into {table_name}: {str(e)}")
            return False

    async def run_test_sequence(self, delay_between_inserts: float = 2.0, cleanup_after_test: bool = True):
        """Run a test sequence by inserting test data and monitoring events."""
        if not self.event_handler:
            logger.error("Cannot run test: Event handler not initialized")
            return

        try:
            # Insert performance history records
            for i, record in enumerate(self.test_records['performance_history']):
                logger.info(f"Inserting performance history record {i+1}/{len(self.test_records['performance_history'])}")
                await self.insert_test_data('performance_history', record)
                await asyncio.sleep(delay_between_inserts)
                
            # Insert pool info records
            for i, record in enumerate(self.test_records['pool_info']):
                logger.info(f"Inserting pool info record {i+1}/{len(self.test_records['pool_info'])}")
                await self.insert_test_data('pool_info', record)
                await asyncio.sleep(delay_between_inserts)
                
            # Insert vault info records
            for i, record in enumerate(self.test_records['abs_vault_info']):
                logger.info(f"Inserting vault info record {i+1}/{len(self.test_records['abs_vault_info'])}")
                await self.insert_test_data('abs_vault_info', record)
                await asyncio.sleep(delay_between_inserts)
            
            # Insert allocation history records
            for i, record in enumerate(self.test_records['abs_vault_allocation_history']):
                logger.info(f"Inserting allocation history record {i+1}/{len(self.test_records['abs_vault_allocation_history'])}")
                await self.insert_test_data('abs_vault_allocation_history', record)
                await asyncio.sleep(delay_between_inserts)
            
            # Wait for final events to propagate
            logger.info("Waiting for final events to propagate...")
            await asyncio.sleep(delay_between_inserts * 2)
            
            logger.info("Test sequence completed")
            
        finally:
            # Clean up test data if requested
            if cleanup_after_test:
                logger.info("Cleaning up test data...")
                await self.clean_up_test_data()

    async def cleanup(self):
        """Clean up resources and connections."""
        try:
            # Stop the event handler
            if self.event_handler:
                try:
                    self.event_handler.shutdown()
                    logger.info("Event handler stopped")
                except Exception as e:
                    logger.error(f"Error stopping event handler: {str(e)}")
                    
            # Clean up ZeroMQ
            if 'zmq_publisher' in self.services:
                try:
                    self.services['zmq_publisher'].close()
                    self.services['zmq_publisher'].context.term()
                    logger.info("ZeroMQ publisher closed")
                except Exception as e:
                    logger.error(f"Error closing ZeroMQ: {str(e)}")
                    
            # Clean up test data
            try:
                await self.clean_up_test_data()
            except Exception as e:
                logger.error(f"Error during final cleanup of test data: {str(e)}")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

    async def clean_up_test_data(self):
        """Clean up test data from the database."""
        logger.info("Cleaning up test data from database...")
        
        if not self.supabase_client:
            logger.warning("Cannot clean up test data: Supabase client not initialized")
            return False
            
        try:
            # Clean up all test records
            for table_name, records in self.test_records.items():
                for record in records:
                    if 'id' in record:
                        await self.delete_test_record(table_name, record['id'])
            
            logger.info("Test data cleanup completed successfully")
            return True
        except Exception as e:
            logger.error(f"Error cleaning up test data: {str(e)}")
            return False
            
    async def delete_test_record(self, table_name: str, record_id: str) -> bool:
        """Delete a test record from the specified table."""
        if not self.supabase_client:
            logger.error(f"Cannot delete data: Supabase client not initialized")
            return False
        
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

async def async_main():
    """Async main function to run the test."""
    parser = argparse.ArgumentParser(description='Test EventHandler system with real database')
    
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
                        help='Disable automatic cleanup of test data')
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create and run the test
    test = EventHandlerDBTest(args.url, args.key)
    
    try:
        # Connect to Supabase
        if not await test.connect_to_supabase():
            logger.error("Failed to connect to Supabase, exiting")
            return
        
        # Set up ZeroMQ
        if not test.setup_zmq():
            logger.error("Failed to set up ZeroMQ, exiting")
            return
        
        # Set up event handler
        if not await test.setup_event_handler():
            logger.error("Failed to set up event handler, exiting")
            return
        
        # Generate test data
        test.generate_test_pools(args.pools)
        test.generate_test_data()
        
        # Run test sequence
        await test.run_test_sequence(args.delay, not args.no_cleanup)
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