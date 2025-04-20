#!/usr/bin/env python
"""
Run Observer Test

This script sets up a TestObserver connected to an Observer to monitor database changes.
It provides a simple way to test the Observer system with real events.
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
from src.observer.observer import Observer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ObserverTest:
    """Test class for running the Observer with TestObserver"""

    def __init__(self, supabase_url: str, supabase_key: str, log_level: str = "INFO"):
        """Initialize the test environment.
        
        Args:
            supabase_url: Supabase URL
            supabase_key: Supabase API key
            log_level: Logging level for the TestObserver
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.log_level = log_level
        
        # Initialize components
        self.supabase_client = None
        self.observer_manager = ObserverManager()
        self.test_observer = TestObserver(log_level=log_level)
        self.observer = None
        self.is_running = False
        
        logger.info("ObserverTest initialized")
    
    def connect_to_supabase(self) -> bool:
        """Connect to Supabase."""
        try:
            # Import here to allow running even if supabase package is not installed
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
    
    def setup(self) -> bool:
        """Set up the Observer system with TestObserver."""
        try:
            # Initialize observables
            market_data_observable = MarketDataObservable()
            portfolio_state_observable = PortfolioStateObservable()
            vault_observable = VaultObservable()
            
            # Register observables with the manager
            self.observer_manager.register_observable('market_data', market_data_observable)
            self.observer_manager.register_observable('portfolio_state', portfolio_state_observable)
            self.observer_manager.register_observable('vault', vault_observable)
            
            # Register test observer for events
            self.observer_manager.register_observer(
                'market_data', EventTypes.NEW_PERFORMANCE_HISTORY_RECORD,
                self.test_observer.handle_new_performance_history_record
            )
            
            self.observer_manager.register_observer(
                'portfolio_state', EventTypes.DEPOSIT_EVENT,
                self.test_observer.handle_deposit_event
            )
            
            self.observer_manager.register_observer(
                'portfolio_state', EventTypes.WITHDRAWAL_EVENT,
                self.test_observer.handle_withdrawal_event
            )
            
            self.observer_manager.register_observer(
                'vault', EventTypes.VAULT_INFO_RECORD,
                self.test_observer.handle_vault_info_record
            )
            
            # Create and start Observer
            if not self.supabase_client:
                logger.error("Cannot set up Observer: Supabase client not initialized")
                return False
                
            self.observer = Observer(
                supabase_client=self.supabase_client,
                observer_manager=self.observer_manager,
                market_data_table='performance_history',
                portfolio_state_table='abs_vault_allocation_history',
                vault_info_table='abs_vault_info'
            )
            
            self.observer.start()
            self.is_running = True
            
            logger.info("Observer system setup complete")
            return True
        except Exception as e:
            logger.error(f"Error setting up Observer system: {str(e)}")
            return False
    
    def trigger_test_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Manually trigger a test event.
        
        Args:
            event_type: Type of event to trigger
            event_data: Event data
        """
        try:
            # Determine which observable should handle this event type
            observable_name = None
            if event_type == EventTypes.NEW_PERFORMANCE_HISTORY_RECORD:
                observable_name = 'market_data'
            elif event_type in [EventTypes.DEPOSIT_EVENT, EventTypes.WITHDRAWAL_EVENT]:
                observable_name = 'portfolio_state'
            elif event_type == EventTypes.VAULT_INFO_RECORD:
                observable_name = 'vault'
            else:
                logger.error(f"Unknown event type: {event_type}")
                return
                
            # Get the observable and trigger the event
            observable = self.observer_manager.get_observable(observable_name)
            observable.notify(event_type, event_data)
            
            logger.info(f"Manually triggered {event_type} event")
        except Exception as e:
            logger.error(f"Error triggering test event: {str(e)}")
    
    def monitor(self, duration: int = 0, summary_interval: int = 10) -> None:
        """Monitor database events for a specified duration.
        
        Args:
            duration: Duration in seconds to monitor (0 for indefinite)
            summary_interval: Interval in seconds to print summary
        """
        if not self.is_running:
            logger.error("Cannot monitor: Observer not running")
            return
            
        try:
            logger.info(f"Monitoring events for {duration if duration > 0 else 'indefinite'} seconds. Press Ctrl+C to stop.")
            
            # Clear any previous events
            self.test_observer.clear()
            
            # Main monitoring loop
            start_time = datetime.now()
            last_summary_time = start_time
            
            while True:
                try:
                    # Check if we've reached the specified duration
                    if duration > 0 and (datetime.now() - start_time).total_seconds() >= duration:
                        logger.info(f"Monitoring completed after {duration} seconds")
                        break
                        
                    # Sleep for a bit to avoid high CPU usage
                    time.sleep(1)
                    
                    # Check if it's time to print a summary
                    now = datetime.now()
                    if (now - last_summary_time).total_seconds() >= summary_interval:
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
            # Print a final summary
            if self.test_observer.get_event_count() > 0:
                print("\n=== Final Event Summary ===")
                self.test_observer.print_event_summary()
                
                # Print details for each event type
                for event_type, count in self.test_observer.event_counts.items():
                    if count > 0:
                        print(f"\nDetails for {event_type} events:")
                        self.test_observer.print_event_details(event_type=event_type)
    
    def cleanup(self) -> None:
        """Clean up resources."""
        if self.observer and self.is_running:
            try:
                self.observer.stop()
                self.is_running = False
                logger.info("Observer stopped")
            except Exception as e:
                logger.error(f"Error stopping Observer: {str(e)}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Run Observer Test with TestObserver')
    
    parser.add_argument('--url', required=True,
                        help='Supabase URL')
                        
    parser.add_argument('--key', required=True,
                        help='Supabase API key')
                        
    parser.add_argument('--duration', type=int, default=0,
                        help='Duration in seconds to monitor (0 for indefinite)')
                        
    parser.add_argument('--interval', type=int, default=10,
                        help='Interval in seconds to print summary')
                        
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='INFO', help='Logging level')
                        
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create and initialize test
    test = ObserverTest(args.url, args.key, args.log_level)
    
    try:
        # Connect to Supabase
        if not test.connect_to_supabase():
            logger.error("Failed to connect to Supabase, exiting")
            return 1
            
        # Set up Observer system
        if not test.setup():
            logger.error("Failed to set up Observer system, exiting")
            return 1
            
        # Start monitoring
        test.monitor(args.duration, args.interval)
        
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1
    finally:
        # Clean up resources
        test.cleanup()

if __name__ == '__main__':
    sys.exit(main()) 