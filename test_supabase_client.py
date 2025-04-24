#!/usr/bin/env python
"""
Supabase Client Test

This script tests that the Supabase client is properly initialized and 
that the Observer class works correctly with the async methods.
"""

import sys
import os
import asyncio
import logging
from supabase import create_client, create_async_client

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'core')))

# Import the Observer class
from core.src.observer.observer import Observer
from core.src.observer import ObserverManager

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DummyObservable:
    """Simple dummy observable for testing"""
    def __init__(self):
        self.callbacks = {}
    
    def notify(self, event_type, data):
        logger.info(f"Notifying for event: {event_type}")
        if event_type in self.callbacks:
            for callback in self.callbacks[event_type]:
                callback(data)
    
    def register_observer(self, event_type, callback):
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
        logger.info(f"Observer registered for {event_type}")

class TestObserver:
    """Simple test observer"""
    def __init__(self):
        self.events = []
    
    def handle_event(self, data):
        logger.info(f"Event received: {data}")
        self.events.append(data)

async def test_supabase_async_client():
    """Test the asynchronous Supabase client."""
    # Replace with your actual Supabase URL and key
    supabase_url = input("Enter your Supabase URL: ")
    supabase_key = input("Enter your Supabase API key: ")
    
    logger.info("Creating async Supabase client...")
    supabase = create_async_client(supabase_url, supabase_key)
    
    logger.info(f"Supabase client type: {type(supabase)}")
    logger.info(f"Supabase client attributes: {dir(supabase)}")
    
    # Check if the client has the channel method
    if hasattr(supabase, 'channel'):
        logger.info("✅ channel method found in supabase client")
    else:
        logger.error("❌ channel method NOT found in supabase client")
    
    # Create a simple observer system
    observer_manager = ObserverManager()
    dummy_observable = DummyObservable()
    observer_manager.register_observable('dummy', dummy_observable)
    
    test_observer = TestObserver()
    observer_manager.register_observer('dummy', 'TEST_EVENT', test_observer.handle_event)
    
    # Create the Observer
    logger.info("Creating Observer...")
    observer = Observer(
        supabase_client=supabase,
        observer_manager=observer_manager,
        market_data_table='performance_history',
        portfolio_state_table='abs_vault_allocation_history',
        vault_info_table='abs_vault_info'
    )
    
    # Start the Observer asynchronously
    logger.info("Starting Observer asynchronously...")
    try:
        await observer.start_async()
        logger.info("✅ Observer started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start Observer: {str(e)}")
    
    # Give some time for the channel to connect
    logger.info("Waiting for channel to connect...")
    await asyncio.sleep(5)
    
    # Manually trigger an event
    logger.info("Triggering test event...")
    dummy_observable.notify('TEST_EVENT', {'message': 'Hello from test event!'})
    
    # Stop the Observer
    logger.info("Stopping Observer...")
    try:
        await observer.stop_async()
        logger.info("✅ Observer stopped successfully")
    except Exception as e:
        logger.error(f"❌ Failed to stop Observer: {str(e)}")

def main():
    """Main function"""
    try:
        asyncio.run(test_supabase_async_client())
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 