#!/usr/bin/env python
"""
Test Event Handler

This script tests the EventHandler class to verify it correctly sets up
Observer pattern components and handles events properly.
"""

import sys
import os
import argparse
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Add the parent directory to the Python path to allow importing from the core module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Import observatory components
from src.observer import EventTypes, ObserverManager
from src.event.event_handler import EventHandler
from src.observer.logging_observer import LoggingObserver
# Import TestObserver from test_observer.py
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../test_observer')))
from test_observer import TestObserver

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockSupabaseService:
    """Supabase service for testing that uses the real client."""
    
    def __init__(self, url: str, key: str):
        """Initialize the Supabase service.
        
        Args:
            url: Supabase URL
            key: Supabase API key
        """
        self.url = url
        self.key = key
        self.client = None
        
        # Use the real supabase client
        try:
            from supabase import create_client
            self.client = create_client(self.url, self.key)
            logger.info("Created real Supabase client successfully")
        except ImportError as e:
            logger.error(f"Supabase package not installed. Run 'pip install supabase' to install it: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {str(e)}")
            raise

class MockPortfolioOptimizationObserver(TestObserver):
    """Mock observer for portfolio optimization tests that extends TestObserver."""
    
    def __init__(self, portfolio_service=None, reoptimization_cooldown_seconds=3600, log_level="INFO"):
        """Initialize the mock portfolio optimization observer.
        
        Args:
            portfolio_service: Portfolio service for optimization
            reoptimization_cooldown_seconds: Cooldown between reoptimizations
            log_level: Logging level
        """
        super().__init__(log_level)
        self.portfolio_service = portfolio_service
        self.reoptimization_cooldown_seconds = reoptimization_cooldown_seconds
        self.last_optimization_time = {}  # Track last optimization time by pool_id
        logger.info("Initialized MockPortfolioOptimizationObserver")
    
    def handle_new_performance_history_record(self, event_data: Dict[str, Any]) -> None:
        """Handle performance history record events with optimization logic.
        
        Args:
            event_data: Event data
        """
        super().handle_new_performance_history_record(event_data)
        
        pool_id = event_data.get('pool_id', 'unknown')
        logger.info(f"Mock handling performance history for pool {pool_id}")
        
        # Add any portfolio-specific optimization logic here
        
    def handle_deposit_event(self, event_data: Dict[str, Any]) -> None:
        """Handle deposit events with optimization logic.
        
        Args:
            event_data: Event data
        """
        super().handle_deposit_event(event_data)
        
        pool_id = event_data.get('pool_id', 'unknown')
        logger.info(f"Mock handling deposit event for pool {pool_id}")
        
        # Add any portfolio-specific optimization logic here
    
    def handle_withdrawal_event(self, event_data: Dict[str, Any]) -> None:
        """Handle withdrawal events with optimization logic.
        
        Args:
            event_data: Event data
        """
        super().handle_withdrawal_event(event_data)
        
        pool_id = event_data.get('pool_id', 'unknown')
        logger.info(f"Mock handling withdrawal event for pool {pool_id}")
        
        # Add any portfolio-specific optimization logic here
    
    def handle_vault_info_record(self, event_data: Dict[str, Any]) -> None:
        """Handle vault info record events with strategy updates.
        
        Args:
            event_data: Event data
        """
        super().handle_vault_info_record(event_data)
        
        pool_id = event_data.get('pool_id', 'unknown')
        logger.info(f"Mock handling vault info record for pool {pool_id}")
        
        # Add any portfolio-specific optimization logic here

# Monkey patch the EventHandler class to use our mocks
original_init = EventHandler.__init__
def patched_init(self, services, config=None):
    original_init(self, services, config)
    self.portfolio_optimization_observer = MockPortfolioOptimizationObserver(
        portfolio_service=services.get('portfolio_service'),
        reoptimization_cooldown_seconds=config.get('reoptimization_cooldown_seconds', 3600) if config else 3600
    )
    self.logging_observer = LoggingObserver(
        log_level=config.get('logging', {}).get('log_level', 'INFO') if config else 'INFO',
        include_data=config.get('logging', {}).get('include_data', True) if config else True
    )

EventHandler.__init__ = patched_init

class EventHandlerTest:
    """Test class for EventHandler."""
    
    def __init__(self, supabase_url: str, supabase_key: str, log_level: str = "INFO"):
        """Initialize the test environment.
        
        Args:
            supabase_url: Supabase URL
            supabase_key: Supabase API key
            log_level: Logging level
        """
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.log_level = log_level
        
        # Mock services
        self.services = {}
        
        # Test observer to track events
        self.test_observer = TestObserver(log_level=log_level)
        
        # Event handler
        self.event_handler = None
        
        logger.info("EventHandlerTest initialized")
    
    def setup_services(self) -> bool:
        """Set up mock services."""
        try:
            # Create mock Supabase service
            self.services['supabase_service'] = MockSupabaseService(
                self.supabase_url, 
                self.supabase_key
            )
            
            # Mock portfolio service
            self.services['portfolio_service'] = {
                'reoptimize': lambda pool_id: logger.info(f"Mock portfolio reoptimization for pool {pool_id}")
            }
            
            logger.info("Services set up successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up services: {str(e)}")
            return False
    
    def setup_event_handler(self) -> bool:
        """Set up and configure the EventHandler."""
        try:
            # Create configuration
            config = {
                'logging': {
                    'log_level': self.log_level,
                    'include_data': True
                },
                'observer': {
                    'market_data_table': 'performance_history',
                    'portfolio_state_table': 'abs_vault_allocation_history',
                    'vault_info_table': 'abs_vault_info'
                },
                'reoptimization_cooldown_seconds': 10  # Short cooldown for testing
            }
            
            # Create event handler
            self.event_handler = EventHandler(self.services, config)
            
            # Custom setup for testing
            self.event_handler._setup_observables()
            
            # Register our test observer with all observables
            for observable_name in ['market_data', 'portfolio_state', 'vault']:
                observable = self.event_handler.get_observable(observable_name)
                
                # Register test observer for various event types
                if observable_name == 'market_data':
                    observable.subscribe(
                        EventTypes.NEW_PERFORMANCE_HISTORY_RECORD,
                        self.test_observer.handle_new_performance_history_record
                    )
                elif observable_name == 'portfolio_state':
                    observable.subscribe(
                        EventTypes.DEPOSIT_EVENT,
                        self.test_observer.handle_deposit_event
                    )
                    observable.subscribe(
                        EventTypes.WITHDRAWAL_EVENT,
                        self.test_observer.handle_withdrawal_event
                    )
                elif observable_name == 'vault':
                    observable.subscribe(
                        EventTypes.VAULT_INFO_RECORD,
                        self.test_observer.handle_vault_info_record
                    )
            
            logger.info("EventHandler set up successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up EventHandler: {str(e)}")
            return False
    
    def test_market_data_event(self) -> bool:
        """Test market data event handling."""
        try:
            logger.info("Testing market data event handling...")
            
            # Ensure test observer is clear
            self.test_observer.clear()
            
            # Create test data
            market_data = {
                'pool_id': 'test_pool_1',
                'apy': 0.05,
                'tvl': 1000000.0,
                'timestamp': datetime.now().isoformat()
            }
            
            # Trigger the event
            self.event_handler.trigger_market_data_update(market_data)
            
            # Check if event was received by test observer
            time.sleep(1)  # Wait a moment for event to be processed
            event_count = self.test_observer.get_event_count(
                event_type='NEW_PERFORMANCE_HISTORY_RECORD'
            )
            
            if event_count > 0:
                logger.info("Market data event test: PASSED")
                return True
            else:
                logger.error("Market data event not received by test observer")
                return False
        except Exception as e:
            logger.error(f"Error in market data event test: {str(e)}")
            return False
    
    def test_deposit_event(self) -> bool:
        """Test deposit event handling."""
        try:
            logger.info("Testing deposit event handling...")
            
            # Ensure test observer is clear
            self.test_observer.clear()
            
            # Create allocation history record for deposit
            # (pool_id equals allocated_pool_id and amount > 0)
            deposit_data = {
                'pool_id': 'test_pool_1',
                'allocated_pool_id': 'test_pool_1',
                'amount': 5000.0,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }
            
            # Get portfolio state observable and process the record
            portfolio_state_observable = self.event_handler.get_observable('portfolio_state')
            portfolio_state_observable.process_allocation_history_record(deposit_data)
            
            # Check if event was received by test observer
            time.sleep(1)  # Wait a moment for event to be processed
            event_count = self.test_observer.get_event_count(
                event_type='DEPOSIT_EVENT'
            )
            
            if event_count > 0:
                logger.info("Deposit event test: PASSED")
                return True
            else:
                logger.error("Deposit event not received by test observer")
                return False
        except Exception as e:
            logger.error(f"Error in deposit event test: {str(e)}")
            return False
    
    def test_withdrawal_event(self) -> bool:
        """Test withdrawal event handling."""
        try:
            logger.info("Testing withdrawal event handling...")
            
            # Ensure test observer is clear
            self.test_observer.clear()
            
            # Create allocation history record for withdrawal
            # (pool_id equals allocated_pool_id, amount < 0, status = 'pending')
            withdrawal_data = {
                'pool_id': 'test_pool_1',
                'allocated_pool_id': 'test_pool_1',
                'amount': -2000.0,
                'status': 'pending',
                'timestamp': datetime.now().isoformat()
            }
            
            # Get portfolio state observable and process the record
            portfolio_state_observable = self.event_handler.get_observable('portfolio_state')
            portfolio_state_observable.process_allocation_history_record(withdrawal_data)
            
            # Check if event was received by test observer
            time.sleep(1)  # Wait a moment for event to be processed
            event_count = self.test_observer.get_event_count(
                event_type='WITHDRAWAL_EVENT'
            )
            
            if event_count > 0:
                logger.info("Withdrawal event test: PASSED")
                return True
            else:
                logger.error("Withdrawal event not received by test observer")
                return False
        except Exception as e:
            logger.error(f"Error in withdrawal event test: {str(e)}")
            return False
    
    def test_vault_info_event(self) -> bool:
        """Test vault info event handling."""
        try:
            logger.info("Testing vault info event handling...")
            
            # Ensure test observer is clear
            self.test_observer.clear()
            
            # Create vault info data
            vault_info_data = {
                'pool_id': 'test_pool_1',
                'strategy': 'BALANCED',
                'allowed_pools': ['test_pool_2', 'test_pool_3'],
                'updated_at': datetime.now().isoformat()
            }
            
            # Get vault observable and process record
            vault_observable = self.event_handler.get_observable('vault')
            vault_observable.process_vault_info_record(vault_info_data)
            
            # Check if event was received by test observer
            time.sleep(1)  # Wait a moment for event to be processed
            event_count = self.test_observer.get_event_count(
                event_type='VAULT_INFO_RECORD'
            )
            
            if event_count > 0:
                logger.info("Vault info event test: PASSED")
                return True
            else:
                logger.error("Vault info event not received by test observer")
                return False
        except Exception as e:
            logger.error(f"Error in vault info event test: {str(e)}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all tests."""
        logger.info("Running all EventHandler tests...")
        
        # Test market data event
        market_data_result = self.test_market_data_event()
        
        # Test deposit event
        deposit_result = self.test_deposit_event()
        
        # Test withdrawal event
        withdrawal_result = self.test_withdrawal_event()
        
        # Test vault info event
        vault_info_result = self.test_vault_info_event()
        
        # Print test results
        print("\n===== EVENT HANDLER TEST RESULTS =====")
        print(f"Market Data Event Test:        {'PASSED' if market_data_result else 'FAILED'}")
        print(f"Deposit Event Test:            {'PASSED' if deposit_result else 'FAILED'}")
        print(f"Withdrawal Event Test:         {'PASSED' if withdrawal_result else 'FAILED'}")
        print(f"Vault Info Event Test:         {'PASSED' if vault_info_result else 'FAILED'}")
        print("=====================================\n")
        
        # Print event summary from test observer
        self.test_observer.print_event_summary()
        
        # Print details for each event type
        for event_type in self.test_observer.event_counts.keys():
            if self.test_observer.get_event_count(event_type) > 0:
                self.test_observer.print_event_details(event_type=event_type)
        
        # Return overall result
        all_passed = (
            market_data_result and 
            deposit_result and 
            withdrawal_result and 
            vault_info_result
        )
        
        if all_passed:
            logger.info("All EventHandler tests PASSED")
        else:
            logger.error("Some EventHandler tests FAILED")
        
        return all_passed
    
    def cleanup(self) -> None:
        """Clean up resources."""
        # Clean up event handler if it was created
        if self.event_handler:
            try:
                self.event_handler.shutdown()
                logger.info("EventHandler shut down")
            except Exception as e:
                logger.error(f"Error shutting down EventHandler: {str(e)}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Test the EventHandler using a real Supabase connection')
    
    parser.add_argument('--url', required=True,
                        help='Supabase URL for real database connection')
                        
    parser.add_argument('--key', required=True,
                        help='Supabase API key for authentication')
                        
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
    
    logger.info("Starting EventHandler test with real Supabase connection")
    logger.info("This test requires the 'supabase' package - install with 'pip install supabase'")
    
    # Create and initialize test
    test = EventHandlerTest(args.url, args.key, args.log_level)
    
    try:
        # Set up services
        if not test.setup_services():
            logger.error("Failed to set up services, exiting")
            return 1
        
        # Set up event handler
        if not test.setup_event_handler():
            logger.error("Failed to set up EventHandler, exiting")
            return 1
        
        # Run tests
        result = test.run_all_tests()
        
        return 0 if result else 1
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1
    finally:
        # Clean up resources
        test.cleanup()

if __name__ == '__main__':
    sys.exit(main()) 