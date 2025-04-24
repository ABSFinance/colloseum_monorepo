#!/usr/bin/env python
"""
Run Observer Test

This script sets up a TestObserver connected to an Observer to monitor database changes.
It's designed to be a simpler alternative to test_observer.py, focusing on listening to
events rather than generating test data.
"""

import sys
import os
import argparse
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add the parent directory to the Python path to allow importing from the core module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import observatory components
from src.observer import EventTypes, ObserverManager
from src.observer.market_data_observable import MarketDataObservable
from src.observer.portfolio_state_observable import PortfolioStateObservable
from src.observer.vault_observable import VaultObservable
from src.observer.test_observer import TestObserver
from src.observer.observer import Observer  # Import Observer instead of SupabaseListener

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ObserverTest:
    """Test harness for the Observer system using the Observer class"""

    def __init__(self, supabase_url: str, supabase_key: str, log_level: str = "INFO"):
        """Initialize the test harness.
        
        Args:
            supabase_url: Supabase URL
            supabase_key: Supabase API key
            log_level: Logging level for the test observer
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.log_level = log_level
        
        # Initialize components
        self.supabase_client = None
        self.observer_manager = ObserverManager()
        self.test_observer = TestObserver(log_level=log_level)
        self.observer = None  # Using Observer instead of supabase_listener
        self.is_listening = False
        
        logger.info("ObserverTest initialized")
    
    def connect_to_supabase(self) -> bool:
        """Connect to Supabase."""
        try:
            # Import inside function to allow running even if supabase package is not installed
            from supabase import create_client
            
            # Create a client with realtime enabled
            self.supabase_client = create_client(
                self.supabase_url, 
                self.supabase_key,
                options={
                    "realtime": {
                        "enabled": True
                    },
                    "autoRefreshToken": True,
                    "persistSession": True,
                    "detectSessionInUrl": False
                }
            )
            
            # Check if the client has the necessary channel method for realtime
            if not hasattr(self.supabase_client, 'channel'):
                logger.error("Supabase client does not have 'channel' method for realtime functionality")
                logger.error("Make sure you're using supabase-py>=2.0.0 and have properly configured the client")
                return False
                
            logger.info("Connected to Supabase successfully with realtime-capable client")
            return True
        except ImportError as e:
            # Create a mock client with __mock__ attribute when supabase is not installed
            logger.warning(f"Supabase package not installed, using mock client: {str(e)}")
            
            class MockSupabaseClient:
                """Mock Supabase client for testing when the supabase package is not available."""
                
                def __init__(self, url, key):
                    self.url = url
                    self.key = key
                    self.__mock__ = True  # Flag to indicate this is a mock
                
                def channel(self, name):
                    """Return a mock channel."""
                    from src.observer.observer import MockChannel
                    return MockChannel(name)
            
            self.supabase_client = MockSupabaseClient(self.supabase_url, self.supabase_key)
            logger.info("Created mock Supabase client as fallback")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {str(e)}")
            return False
    
    def setup_observer_system(self) -> bool:
        """Set up the Observer system components."""
        try:
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
            
            logger.info("Observer system setup complete")
            return True
        except Exception as e:
            logger.error(f"Error setting up observer system: {str(e)}")
            return False
    
    async def setup_observer_async(self) -> bool:
        """Set up the Observer asynchronously."""
        if not self.supabase_client:
            logger.error("Cannot set up observer: Supabase client not initialized")
            return False
        
        try:
            # Log supabase client type for debugging
            logger.info(f"Supabase client type: {type(self.supabase_client)}")
            
            # Create the Observer
            self.observer = Observer(
                supabase_client=self.supabase_client,
                observer_manager=self.observer_manager,
                market_data_table='performance_history',
                portfolio_state_table='abs_vault_allocation_history',
                vault_info_table='abs_vault_info'
            )
            
            # Use the async start method directly
            await self.observer.start_async()
            self.is_listening = True
            logger.info("Observer started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set up Observer: {str(e)}")
            return False
    
    def setup_observer(self) -> bool:
        """Set up the Observer (synchronous wrapper)."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                future = asyncio.run_coroutine_threadsafe(self.setup_observer_async(), new_loop)
                return future.result()
            else:
                return loop.run_until_complete(self.setup_observer_async())
        except Exception as e:
            logger.error(f"Error in setup_observer: {str(e)}")
            return False
    
    def manually_trigger_event(self, observable_name: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """Manually trigger an event (for testing when we don't want to insert into the database).
        
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
    
    def start_monitoring(self) -> None:
        """Start monitoring database events."""
        if not self.is_listening:
            logger.error("Cannot start monitoring: Observer not started")
            return
        
        try:
            logger.info("Starting to monitor events. Press Ctrl+C to stop.")
            
            # Main monitor loop
            interval = 10  # Print summary every 10 seconds
            last_summary_time = datetime.now()
            
            while True:
                try:
                    time.sleep(1)  # Sleep briefly to avoid CPU usage
                    
                    # If it's time to print a summary
                    now = datetime.now()
                    if (now - last_summary_time).total_seconds() >= interval:
                        # Print event summary if we have events
                        if self.test_observer.get_event_count() > 0:
                            print("\n=== Event Summary Update ===")
                            self.test_observer.print_event_summary()
                            last_summary_time = now
                    
                except KeyboardInterrupt:
                    logger.info("Monitoring stopped by user")
                    break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {str(e)}")
        finally:
            self.cleanup()
    
    async def cleanup_async(self) -> None:
        """Clean up resources asynchronously."""
        if self.observer and self.is_listening:
            try:
                await self.observer.stop_async()
                self.is_listening = False
                logger.info("Observer stopped")
            except Exception as e:
                logger.error(f"Error stopping Observer: {str(e)}")
        
        # Print final event summary
        if self.test_observer.get_event_count() > 0:
            print("\n=== Final Event Summary ===")
            self.test_observer.print_event_summary()
            
            # If we have events, print details for each event type
            for event_type in self.test_observer.event_counts.keys():
                if self.test_observer.get_event_count(event_type) > 0:
                    self.test_observer.print_event_details(event_type=event_type)
    
    def cleanup(self) -> None:
        """Clean up resources (synchronous wrapper)."""
        try:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                future = asyncio.run_coroutine_threadsafe(self.cleanup_async(), new_loop)
                future.result()
            else:
                loop.run_until_complete(self.cleanup_async())
        except Exception as e:
            logger.error(f"Error in cleanup: {str(e)}")
            
            # Print final event summary in case of error
            if self.test_observer.get_event_count() > 0:
                print("\n=== Final Event Summary (after error) ===")
                self.test_observer.print_event_summary()

async def async_main():
    """Async main function."""
    parser = argparse.ArgumentParser(description='Test the Observer with TestObserver')
    
    parser.add_argument('--url', required=True,
                        help='Supabase URL')
    
    parser.add_argument('--key', required=True,
                        help='Supabase API key')
    
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                        default='INFO', help='Logging level')
    
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')

    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create and initialize the test
    test = ObserverTest(args.url, args.key, args.log_level)
    
    try:
        # Connect to Supabase
        if not test.connect_to_supabase():
            logger.error("Failed to connect to Supabase, exiting")
            return 1
        
        # Set up observer system
        if not test.setup_observer_system():
            logger.error("Failed to set up observer system, exiting")
            return 1
        
        # Set up Observer asynchronously
        if not await test.setup_observer_async():
            logger.error("Failed to set up Observer, exiting")
            return 1
        
        # Start monitoring
        test.start_monitoring()
        
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1
    finally:
        # Ensure resources are cleaned up
        test.cleanup()

def main():
    """Main function that runs the async_main function."""
    try:
        import asyncio
        return asyncio.run(async_main())
    except Exception as e:
        logger.error(f"Unhandled exception in main: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 