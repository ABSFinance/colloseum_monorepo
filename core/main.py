import logging
import signal
import sys
from typing import Dict, Any
import zmq
import argparse
from supabase import create_async_client, AsyncClient
import asyncio
from src.event.event_handler import EventHandler
from tests.test_event_handler.test_event_handler_with_db import EventHandlerDBTest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def setup_services(config: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize and return required services."""
    services = {}
    
    # Setup Supabase client if configured
    if 'supabase' in config:
        try:
            # Create client with realtime enabled
            supabase: AsyncClient = await create_async_client(
                config['supabase']['url'],
                config['supabase']['key']
            )
            
            # Store in services
            services['supabase_service'] = supabase
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise
    
    return services

def setup_config(args: argparse.Namespace) -> Dict[str, Any]:
    """Initialize and return configuration."""
    config = {
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
            'pub_address': 'tcp://*:5555',
            'sub_address': 'tcp://localhost:5555'  # Add subscriber address for testing
        },
        'supabase': {
            'url': args.url,
            'key': args.key
        }
    }
    return config

async def run_test_sequence(config: Dict[str, Any], services: Dict[str, Any]):
    """Run the test sequence."""
    try:
        # Create test instance
        test = EventHandlerDBTest(config['supabase']['url'], config['supabase']['key'])
        
        # Connect to Supabase
        if not await test.connect_to_supabase():
            logger.error("Failed to connect to Supabase")
            return False
            
        # Set up ZeroMQ
        if not test.setup_zmq():
            logger.error("Failed to set up ZeroMQ")
            return False
            
        # Set up event handler
        if not await test.setup_event_handler():
            logger.error("Failed to set up event handler")
            return False
            
        # Generate test data
        test.generate_test_pools(2)  # Create 2 test pools
        test.generate_test_data()
        
        # Run test sequence
        success = await test.run_test_sequence(delay_between_inserts=2.0, cleanup_after_test=True)
        
        # Clean up
        await test.cleanup()
        
        return success
        
    except Exception as e:
        logger.error(f"Error in test sequence: {str(e)}")
        return False

async def main():
    """Main entry point for the application."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the event handling system')
    parser.add_argument('--url', required=True, help='Supabase URL')
    parser.add_argument('--key', required=True, help='Supabase API key')
    parser.add_argument('--test', action='store_true', help='Run test sequence')
    args = parser.parse_args()
    
    try:
        # Setup configuration
        config = setup_config(args)
        
        # Initialize services
        services = await setup_services(config)
        
        if args.test:
            # Run test sequence
            success = await run_test_sequence(config, services)
            if not success:
                logger.error("Test sequence failed")
                sys.exit(1)
            logger.info("Test sequence completed successfully")
            return
            
        # Setup ZeroMQ publisher if enabled
        if config['zmq']['enabled']:
            context = zmq.Context()
            publisher = context.socket(zmq.PUB)
            publisher.bind(config['zmq']['pub_address'])
            services['zmq_publisher'] = publisher
        
        # Create and setup event handler
        event_handler = EventHandler(services, config)
        await event_handler.setup()
        
        # Start the event handler and keep it running
        logger.info("Event system started. Press Ctrl+C to exit.")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        finally:
            # Cleanup
            await event_handler.shutdown()
            if 'publisher' in locals():
                publisher.close()
                context.term()
            logger.info("Application shutdown complete")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
