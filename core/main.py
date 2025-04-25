import logging
import signal
import sys
from typing import Dict, Any
import zmq
import argparse
from supabase import create_async_client, AsyncClient
import asyncio
from src.event.event_handler import EventHandler

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
            
            print(config['supabase']['url'])
            print(config['supabase']['key'])
            
            supabase: AsyncClient = await create_async_client(
                config['supabase']['url'],
                config['supabase']['key']
            )
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
            'pub_address': 'tcp://*:5555'
        },
        'supabase': {
            'url': args.url,
            'key': args.key
        }
    }
    return config

async def main():
    """Main entry point for the application."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the event handling system')
    parser.add_argument('--url', required=True, help='Supabase URL')
    parser.add_argument('--key', required=True, help='Supabase API key')
    args = parser.parse_args()
    
    try:
        # Setup configuration
        config = setup_config(args)
        
        # Initialize services
        services = await setup_services(config)
        
        # Setup ZeroMQ publisher if enabled
        if config['zmq']['enabled']:
            context = zmq.Context()
            publisher = context.socket(zmq.PUB)
            publisher.bind(config['zmq']['pub_address'])
            services['zmq_publisher'] = publisher
        
        # Create and setup event handler
        event_handler = EventHandler(services, config)
        await event_handler.setup()
        
        # Keep the main thread alive
        logger.info("Event system started. Press Ctrl+C to exit.")
        signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
        signal.pause()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup
        if 'event_handler' in locals():
            await event_handler.shutdown()
        if 'publisher' in locals():
            publisher.close()
            context.term()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())
