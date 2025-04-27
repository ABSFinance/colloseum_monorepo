"""
Event Handler

This module provides a central event handling system that connects:
1. Observer (for listening to Supabase events)
2. Optimizer (for portfolio optimization)
3. Evaluator (for evaluation and analysis)
4. ZeroMQ (for message passing)

The event flow is:
- Observer listens to Supabase events
- Events are routed to the Optimizer 
- Optimizer results are sent to the Evaluator
- Results are published through ZeroMQ
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List, Callable
import threading
import queue

# Import components
from ..observer import ObserverManager, EventTypes
from ..observer.market_data_observable import MarketDataObservable
from ..observer.portfolio_state_observable import PortfolioStateObservable
from ..observer.vault_observable import VaultObservable
from ..observer.logging_observer import LoggingObserver
from ..observer.observer import Observer
from ..optimizer.optimizer import Optimizer  # Import the Optimizer class

# Define the interface for working with the optimizer and evaluator
class OptimizerInterface:
    """Interface for interacting with the optimizer."""
    
    def __init__(self, optimizer_service=None):
        """Initialize the optimizer interface.
        
        Args:
            optimizer_service: Service for optimization
        """
        self.optimizer_service = optimizer_service
        self.logger = logging.getLogger(f"{__name__}.OptimizerInterface")
    
    def handle_market_data_update(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle market data updates.
        
        Args:
            event_data: Event data for market update
            
        Returns:
            Dict with optimization results
        """

        pool_id = event_data.get('pool_id')
        self.logger.info(f"Processing market data update for pool {pool_id}")
        
        # Call optimizer service if available
        if self.optimizer_service and hasattr(self.optimizer_service, 'handle_market_data'):
            try:
                # Use the handle_market_data method directly from the Optimizer class
                # No need to pass vault_data since it's just market data
                result = self.optimizer_service.handle_market_data(event_data)
                return result
            except Exception as e:
                self.logger.error(f"Error during optimization for pool {pool_id}: {str(e)}")
        
        # If no optimizer service, just return the event data
        return event_data
    
    def handle_deposit_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deposit events.
        
        Args:
            event_data: Event data for deposit
            
        Returns:
            Dict with optimization results
        """
        pool_id = event_data.get('pool_id')
        self.logger.info(f"Processing deposit event for pool {pool_id}")
        
        # Call optimizer service if available
        if self.optimizer_service and hasattr(self.optimizer_service, 'handle_vault_update'):
            try:
                # For deposit events, we pass the event_data as vault_info
                result = self.optimizer_service.handle_vault_update(event_data)
                self.logger.info(f"Reoptimization completed for pool {pool_id} after deposit")
                return result
            except Exception as e:
                self.logger.error(f"Error during reoptimization for pool {pool_id}: {str(e)}")
        
        return event_data
    
    def handle_withdrawal_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle withdrawal events.
        
        Args:
            event_data: Event data for withdrawal
            
        Returns:
            Dict with optimization results
        """
        pool_id = event_data.get('pool_id')
        self.logger.info(f"Processing withdrawal event for pool {pool_id}")
        
        # Call optimizer service if available
        if self.optimizer_service and hasattr(self.optimizer_service, 'handle_vault_update'):
            try:
                # For withdrawal events, we pass the event_data as vault_info
                result = self.optimizer_service.handle_vault_update(event_data)
                self.logger.info(f"Reoptimization completed for pool {pool_id} after withdrawal")
                return result
            except Exception as e:
                self.logger.error(f"Error during reoptimization for pool {pool_id}: {str(e)}")
        
        return event_data
    
    def handle_vault_info_update(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle vault info updates.
        
        Args:
            event_data: Event data for vault info update
            
        Returns:
            Dict with optimization results
        """
        pool_id = event_data.get('pool_id')
        self.logger.info(f"Processing vault info update for pool {pool_id}")
        
        # Call optimizer service if available
        if self.optimizer_service and hasattr(self.optimizer_service, 'handle_vault_update'):
            try:
                # For vault info updates, we pass the event_data as vault_info
                result = self.optimizer_service.handle_vault_update(event_data)
                self.logger.info(f"Strategy update completed for pool {pool_id}")
                return result
            except Exception as e:
                self.logger.error(f"Error during strategy update for pool {pool_id}: {str(e)}")
        
        return event_data


class EvaluatorInterface:
    """Interface for interacting with the evaluator."""
    
    def __init__(self, evaluator_service=None):
        """Initialize the evaluator interface.
        
        Args:
            evaluator_service: Service for evaluation
        """
        self.evaluator_service = evaluator_service
        self.logger = logging.getLogger(f"{__name__}.EvaluatorInterface")
    
    def evaluate_optimization_result(self, optimization_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate optimization results.
        
        Args:
            optimization_result: Results from the optimizer
            
        Returns:
            Dict with evaluation results
        """
        pool_id = optimization_result.get('pool_id')
        self.logger.info(f"Evaluating optimization result for pool {pool_id}")
        
        # Call evaluator service if available
        if self.evaluator_service and hasattr(self.evaluator_service, 'evaluate'):
            try:
                result = self.evaluator_service.evaluate(optimization_result)
                self.logger.info(f"Evaluation completed for pool {pool_id}")
                return result
            except Exception as e:
                self.logger.error(f"Error during evaluation for pool {pool_id}: {str(e)}")
        
        return optimization_result


class MessageBroker:
    """Message broker for handling communication between components."""
    
    def __init__(self, zmq_enabled: bool = False, zmq_publisher=None):
        """Initialize the message broker.
        
        Args:
            zmq_enabled: Whether to enable ZeroMQ for messaging
            zmq_publisher: ZeroMQ publisher instance
        """
        self.zmq_enabled = zmq_enabled
        self.zmq_publisher = zmq_publisher
        self.logger = logging.getLogger(f"{__name__}.MessageBroker")
        
        # Create a processing queue and worker thread for async processing
        self.processing_queue = queue.Queue()
        self.worker_thread = None
        self.is_running = False
    
    def start(self):
        """Start the message broker worker thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()
        self.logger.info("Message broker worker thread started")
    
    def stop(self):
        """Stop the message broker worker thread."""
        if not self.is_running:
            return
        
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
        self.logger.info("Message broker worker thread stopped")
    
    def _process_queue(self):
        """Process the message queue in a worker thread."""
        while self.is_running:
            try:
                # Get a message from the queue with a timeout
                try:
                    message_type, message_data, callbacks = self.processing_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process the message
                self.logger.debug(f"Processing message of type {message_type}")
                
                # Call all callbacks registered for this message
                for callback in callbacks:
                    try:
                        callback(message_data)
                    except Exception as e:
                        self.logger.error(f"Error in message callback: {str(e)}")
                
                # Publish via ZeroMQ if enabled
                if self.zmq_enabled and self.zmq_publisher:
                    self._publish_via_zmq(message_type, message_data)
                
                # Mark the task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in message processing loop: {str(e)}")
    
    def _publish_via_zmq(self, message_type: str, message_data: Dict[str, Any]):
        """Publish a message via ZeroMQ.
        
        Args:
            message_type: Type of message to publish
            message_data: Message data to publish
        """
        try:
            # Create a message with topic and data
            topic = f"colloseum.{message_type}"
            message = {
                'type': message_type,
                'timestamp': time.time(),
                'data': message_data
            }
            
            # Convert to JSON
            json_message = json.dumps(message)
            
            # Publish
            self.zmq_publisher.send_multipart([
                topic.encode('utf-8'),
                json_message.encode('utf-8')
            ])
            
            self.logger.debug(f"Published message of type {message_type} via ZeroMQ")
        except Exception as e:
            self.logger.error(f"Error publishing message via ZeroMQ: {str(e)}")
    
    def publish(self, message_type: str, message_data: Dict[str, Any], callbacks: List[Callable] = None):
        """Publish a message to the broker.
        
        Args:
            message_type: Type of message to publish
            message_data: Message data to publish
            callbacks: List of callback functions to call with the message data
        """
        # Add the message to the processing queue
        self.processing_queue.put((message_type, message_data, callbacks or []))
        self.logger.debug(f"Queued message of type {message_type} for processing")


class EventHandler:
    """Central handler for setting up and managing the event flow between components."""

    def __init__(self, services: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        """Initialize the event handler with required services and optional configuration.
        
        Args:
            services: Dictionary of service objects required by components
            config: Optional configuration for components
        """
        self.services = services
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.EventHandler")
        
        # Create observer manager
        self.observer_manager = ObserverManager()
        
        # Create optimizer instance if not provided in services
        optimizer_service = services.get('optimizer_service')
        if optimizer_service is None and 'supabase_service' in services:
            # Create an optimizer instance with the Supabase client
            optimizer_service = Optimizer(supabase_client=services.get('supabase_service'))
            services['optimizer_service'] = optimizer_service
        
        # Create optimizer interface
        self.optimizer = OptimizerInterface(
            optimizer_service=optimizer_service
        )
        
        # Create evaluator interface
        self.evaluator = EvaluatorInterface(
            evaluator_service=services.get('evaluator_service')
        )
        
        # Create message broker
        zmq_config = self.config.get('zmq', {})
        self.message_broker = MessageBroker(
            zmq_enabled=zmq_config.get('enabled', False),
            zmq_publisher=services.get('zmq_publisher')
        )
        
        # Set up logging observer
        logging_config = self.config.get('logging', {})
        self.logging_observer = LoggingObserver(
            log_level=logging_config.get('log_level', 'INFO'),
            include_data=logging_config.get('include_data', True)
        )
        
        self.logger.info("Initializing Event Handler")
        
    async def setup(self) -> None:
        """Set up all components and connect them together."""
        self.logger.info("Setting up event handling system")
        
        # Initialize all observable objects
        self._setup_observables()
        
        # Connect observers to observables based on event types
        self._connect_observers_to_observables()

        # Initialize market data if optimizer service is available
        if 'optimizer_service' in self.services:
            try:
                self.logger.info("Initializing market data...")
                await self.services['optimizer_service'].initialize_market_data()
                await self.services['optimizer_service'].initialize_vault_info()
                self.logger.info("Market data initialization complete")
            except Exception as e:
                self.logger.error(f"Failed to initialize market data: {str(e)}")
        
        # Set up the Observer if Supabase service is available
        if 'supabase_service' in self.services:
            await self._setup_observer()
        
        # Start the message broker
        self.message_broker.start()
        
        self.logger.info("Event handling system setup complete")
        
    def _setup_observables(self) -> None:
        """Initialize and register all observable objects."""
        # Create and register market data observable
        market_data_observable = MarketDataObservable()
        self.observer_manager.register_observable('market_data', market_data_observable)
        
        # Create and register portfolio state observable
        portfolio_state_observable = PortfolioStateObservable()
        self.observer_manager.register_observable('portfolio_state', portfolio_state_observable)
        
        # Create and register vault observable
        vault_observable = VaultObservable()
        self.observer_manager.register_observable('vault', vault_observable)
        
        self.logger.info(f"Registered observables: market_data, portfolio_state, vault")
    
    def _connect_observers_to_observables(self) -> None:
        """Connect observers to observables for relevant event types."""
        # Create handlers that route events through the optimization -> evaluation -> messaging pipeline
        
        # Market data events
        def handle_market_data(event_data):
            # Ensure consistent naming - if timestamp exists but created_at doesn't, copy it over
            if 'timestamp' in event_data and 'created_at' not in event_data:
                event_data['created_at'] = event_data['timestamp']
            
            # First pass through optimizer
            opt_result = self.optimizer.handle_market_data_update(event_data)
            # Then through evaluator
            eval_result = self.evaluator.evaluate_optimization_result(opt_result)
            # Finally publish via message broker
            self.message_broker.publish(
                'market_data_processed', 
                eval_result, 
                [self.logging_observer.handle_event]
            )
        
        # Deposit events
        def handle_deposit(event_data):
            opt_result = self.optimizer.handle_deposit_event(event_data)
            eval_result = self.evaluator.evaluate_optimization_result(opt_result)
            self.message_broker.publish(
                'deposit_processed', 
                eval_result, 
                [self.logging_observer.handle_event]
            )
        
        # Withdrawal events
        def handle_withdrawal(event_data):
            opt_result = self.optimizer.handle_withdrawal_event(event_data)
            eval_result = self.evaluator.evaluate_optimization_result(opt_result)
            self.message_broker.publish(
                'withdrawal_processed', 
                eval_result, 
                [self.logging_observer.handle_event]
            )
        
        # Vault info events
        def handle_vault_info(event_data):
            opt_result = self.optimizer.handle_vault_info_update(event_data)
            eval_result = self.evaluator.evaluate_optimization_result(opt_result)
            self.message_broker.publish(
                'vault_info_processed', 
                eval_result, 
                [self.logging_observer.handle_event]
            )
        
        # Register specific handlers for each event type
        self.observer_manager.register_observer(
            'portfolio_state', EventTypes.DEPOSIT_EVENT, handle_deposit
        )
        
        self.observer_manager.register_observer(
            'portfolio_state', EventTypes.WITHDRAWAL_EVENT, handle_withdrawal
        )
        
        self.observer_manager.register_observer(
            'vault', EventTypes.VAULT_INFO_RECORD, handle_vault_info
        )
        
        
        self.observer_manager.register_observer(
            'market_data', EventTypes.NEW_PERFORMANCE_HISTORY_RECORD, 
            handle_market_data
        )
        
        self.logger.info("Connected observers to observables")
    
    async def _setup_observer(self) -> None:
        """Set up the Observer to listen to Supabase events."""
        supabase_service = self.services.get('supabase_service')
        if not supabase_service:
            self.logger.warning("Supabase service not available, skipping observer setup")
            return
            
        # Create and initialize the Observer
        try:
            observer_config = self.config.get('observer', {})
            self.observer = Observer(
                supabase_client=supabase_service,
                observer_manager=self.observer_manager,
                market_data_table=observer_config.get('market_data_table', 'performance_history'),
                portfolio_state_table=observer_config.get('portfolio_state_table', 'abs_vault_allocation_history'),
                vault_info_table=observer_config.get('vault_info_table', 'abs_vault_info')
            )
            await self.observer.start()
            self.logger.info("Observer started successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Observer: {str(e)}")
    
    def get_observable(self, name: str):
        """Get an observable by name."""
        return self.observer_manager.get_observable(name)
    
    def trigger_market_data_update(self, data: Dict[str, Any]) -> None:
        """Manually trigger a market data update.
        
        Args:
            data: Dictionary containing market data update
        """
        try:
            market_data_observable = self.observer_manager.get_observable('market_data')
            market_data_observable.update_market_data(data)
            self.logger.debug(f"Manually triggered market data update for pool {data.get('pool_id', 'unknown')}")
        except Exception as e:
            self.logger.error(f"Error triggering market data update: {str(e)}")
    
    def trigger_portfolio_state_update(self, data: Dict[str, Any]) -> None:
        """Manually trigger a portfolio state update.
        
        Args:
            data: Dictionary containing portfolio state update
        """
        try:
            portfolio_state_observable = self.observer_manager.get_observable('portfolio_state')
            portfolio_state_observable.update_portfolio_state(data)
            self.logger.debug(f"Manually triggered portfolio state update for {data.get('portfolio_id', 'unknown')}")
        except Exception as e:
            self.logger.error(f"Error triggering portfolio state update: {str(e)}")
    
    def trigger_vault_info_update(self, data: Dict[str, Any]) -> None:
        """Manually trigger a vault info update.
        
        Args:
            data: Dictionary containing vault info update
        """
        try:
            vault_observable = self.observer_manager.get_observable('vault')
            print(f"vault_observable data: {data}")
            vault_observable.update_vault_info(data)
            self.logger.debug(f"Manually triggered vault info update for pool {data.get('pool_id', 'unknown')}")
        except Exception as e:
            self.logger.error(f"Error triggering vault info update: {str(e)}")
    
    async def shutdown(self) -> None:
        """Clean up resources and shut down the event handling system."""
        self.logger.info("Shutting down event handler")
        
        # Stop the message broker
        if hasattr(self, 'message_broker'):
            try:
                self.message_broker.stop()
                self.logger.info("Message broker stopped")
            except Exception as e:
                self.logger.error(f"Error stopping message broker: {str(e)}")
        
        # Stop the Observer
        if hasattr(self, 'observer'):
            try:
                await self.observer.stop()
                self.logger.info("Observer stopped")
            except Exception as e:
                self.logger.error(f"Error stopping Observer: {str(e)}")


# Example application initialization code:
"""
async def initialize_event_system(services):
    # Define configuration
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
        }
    }
    
    # Create ZeroMQ publisher if needed
    import zmq
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(config['zmq']['pub_address'])
    services['zmq_publisher'] = publisher
    
    # If you have a Supabase client, the Optimizer will be created automatically
    # Or you can create and provide an Optimizer instance manually:
    # from ..optimizer.optimizer import Optimizer
    # optimizer = Optimizer(supabase_client=services.get('supabase_service'))
    # services['optimizer_service'] = optimizer
    
    # Create and set up event handler
    event_handler = EventHandler(services, config)
    # Set up the event handler (this is an async method)
    await event_handler.setup()
    
    return event_handler

# Example usage with manual optimizer initialization:
async def example_with_manual_optimizer():
    services = {}
    
    # Initialize Supabase client (placeholder - replace with actual initialization)
    from supabase import create_client
    supabase_url = "your-supabase-url"
    supabase_key = "your-supabase-key"
    supabase_client = create_client(supabase_url, supabase_key)
    services['supabase_service'] = supabase_client
    
    # Initialize optimizer manually with supabase client
    from ..optimizer.optimizer import Optimizer
    optimizer = Optimizer(supabase_client=supabase_client)
    services['optimizer_service'] = optimizer
    
    # Initialize event system
    event_handler = await initialize_event_system(services)
    
    # You can directly interact with the optimizer interface
    # For example, to manually trigger market data processing:
    # market_data = {"pool_id": "123", "apy": 5.2, "created_at": "2023-01-01T00:00:00Z"}
    # result = event_handler.optimizer.handle_market_data_update(market_data)
    
    return event_handler

# For non-async environments, you can use:
def run_event_system():
    import asyncio
    services = {}
    # ... set up services ...
    event_handler = asyncio.run(initialize_event_system(services))
    return event_handler
""" 