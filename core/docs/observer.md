# Observer Component

## Overview

The Observer component is a critical system in the ABS Finance architecture that provides real-time monitoring, event propagation, and reactive behavior throughout the platform. Based on the Observer design pattern, this component establishes a publish-subscribe relationship between system components, allowing for decoupled communication and efficient event handling.

## Observer Architecture Diagram

```
                               OBSERVER COMPONENT ARCHITECTURE
                               =============================

 +------------------+                                +------------------+
 |                  |        Subscribes to           |                  |
 |  Event Emitters  |<----------------------------- |   Observers      |
 | (Observables)    |                               | (Subscribers)    |
 |                  |------------------------------->|                  |
 +------------------+        Notifies                +------------------+
         ^                                                   |
         |                                                   |
         | Produces                                          | Triggers
         | Events                                            | Actions
         |                                                   v
 +------------------+                                +------------------+
 |                  |                                |                  |
 |  Data Sources    |                                |  Event Handlers  |
 | - Market Data    |                                | - Optimization   |
 | - User Actions   |                                |  |
 | - System States  |                                | - Logging        |
 +------------------+                                +------------------+
```

## Core Components

### 1. Observable Manager

The Observable Manager serves as the central registry for all observables and observers in the system. It provides methods for registering, unregistering, and managing subscriptions between components.

Key responsibilities:

- Maintain a registry of all observable objects
- Track observer subscriptions to specific events
- Provide methods for observers to subscribe/unsubscribe
- Ensure thread-safety for concurrent operations

### 2. Event Emitters (Observables)

Event Emitters are the components that generate events to be observed. These include:

1. **MarketDataObservable**

   - Emits events when market data changes
   - Monitors performance_history
   - Provides severity assessment for changes (minor, moderate, significant)

2. **PortfolioStateObservable**

   - Emits events when portfolio states change
   - Tracks changes in allocations, strategy, and performance
   - Monitors abs_vault_allocation_history

3. **SystemStatusObservable**

   - Emits events related to system health and operations
   - Monitors service availability, latency, and errors
   - Tracks computational resource usage

4. **UserActionObservable**
   - Emits events when users perform relevant actions
   - Tracks preference changes, strategy modifications, and constraint updates
   - Monitors abs_vault_info

### 3. Observers (Subscribers)

Observers are components that respond to events emitted by observables:

1. **PortfolioOptimizationObserver**

   - Triggers portfolio reoptimization when relevant market conditions change
   - Implements configurable thresholds for when to react
   - Manages optimization priority and queuing

2. **LoggingObserver**

   - Records all system events for audit and debugging
   - Implements different logging levels (debug, info, warning, error)
   - Rotates and archives logs according to retention policies

3. **MetricsObserver**
   - Collects performance and operational metrics
   - Calculates statistical summaries of system behavior
   - Stores metrics for historical analysis

## Event Types

The observer system handles the following event categories:

1. **Market Events**

   - `NEW_PERFORMANCE_HISTORY_RECORD`: A new performance history record is created

2. **Portfolio Events**

   - `NEW_ALLOCATION_HISTORY_RECORD`: A new allocation history record is created
   - `DEPOSIT_EVENT`: A deposit event is recorded
   - `WITHDRAWAL_EVENT`: A withdrawal event is recorded

3. **System Events**

   - `SERVICE_STATUS_CHANGE`: Changes in service health
   - `RESOURCE_UTILIZATION`: High resource utilization alerts
   - `ERROR_OCCURRENCE`: System errors requiring attention
   - `SCHEDULED_TASK`: Completion of scheduled operations

4. **User Events**
   - `NEW_VAULT_INFO_RECORD`: A new vault info record is created
   - `UPDATED_VAULT_INFO_RECORD`: An existing vault info record is updated

## Implementation

### Implementing the Observable Interface

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any

class IObservable(ABC):
    """Interface for observable objects that emit events."""

    @abstractmethod
    def subscribe(self, event_type: str, observer: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe an observer to a specific event type."""
        pass

    @abstractmethod
    def unsubscribe(self, event_type: str, observer: Callable[[Dict[str, Any]], None]) -> None:
        """Unsubscribe an observer from a specific event type."""
        pass

    @abstractmethod
    def notify(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        pass


class Observable(IObservable):
    """Base implementation of the Observable interface."""

    def __init__(self):
        self._observers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def subscribe(self, event_type: str, observer: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe an observer to a specific event type."""
        if event_type not in self._observers:
            self._observers[event_type] = []
        if observer not in self._observers[event_type]:
            self._observers[event_type].append(observer)

    def unsubscribe(self, event_type: str, observer: Callable[[Dict[str, Any]], None]) -> None:
        """Unsubscribe an observer from a specific event type."""
        if event_type in self._observers and observer in self._observers[event_type]:
            self._observers[event_type].remove(observer)

    def notify(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        if event_type in self._observers:
            for observer in self._observers[event_type]:
                observer(event_data)
```

### Market Data Observable Example

```python
from datetime import datetime
from typing import Dict, Any, List

class MarketDataObservable(Observable):
    """Observable for market data changes."""

    def __init__(self):
        super().__init__()
        self.last_performance_history: Dict[str, Dict[str, Any]] = {}

    def process_performance_history_record(self, record: Dict[str, Any]) -> None:
        """Process a new performance history record and emit events.

        Args:
            record: The new performance history record
        """
        # Extract key data from the record
        asset_id = record.get('asset_id')
        timestamp = record.get('timestamp', datetime.now().isoformat())
        apy = record.get('apy', 0.0)
        liquidity = record.get('liquidity', 0.0)

        # Prepare event data
        event_data = {
            'asset_symbol': asset_id,
            'apy': apy,
            'tvl': tvl,
            'timestamp': timestamp,
            'record_id': record.get('id'),
            'record': record  # Include the full record for completeness
        }

        # Store this record for future reference
        if asset_id:
            self.last_performance_history[asset_id] = event_data

        # Notify observers of the new performance history record
        self.notify('NEW_PERFORMANCE_HISTORY_RECORD', event_data)
```

### Portfolio Optimization Observer Example

```python
from typing import Dict, Any
import logging

class PortfolioOptimizationObserver:
    """Observer that triggers portfolio optimization when significant market changes occur."""

    def __init__(self, portfolio_service):
        self.portfolio_service = portfolio_service
        self.logger = logging.getLogger(__name__)

    def handle_new_performance_history_record(self, event_data: Dict[str, Any]) -> None:
        """Handle new performance history record events."""
        asset_symbol = event_data['asset_symbol']
        apy = event_data['apy']

        self.logger.info(f"New performance history record for {asset_symbol}: APY={apy:.2%}")

        # Determine affected portfolios
        affected_portfolios = self.portfolio_service.find_portfolios_containing_asset(asset_symbol)

        if affected_portfolios:
            self.logger.info(f"Triggering optimization for {len(affected_portfolios)} affected portfolios")

            # Queue optimization jobs for affected portfolios
            for portfolio_id in affected_portfolios:
                self.portfolio_service.queue_optimization_job(
                    portfolio_id=portfolio_id,
                    trigger="new_performance_data",
                    trigger_data=event_data
                )

    def handle_new_allocation_history_record(self, event_data: Dict[str, Any]) -> None:
        """Handle new allocation history record events."""
        portfolio_id = event_data['portfolio_id']

        self.logger.info(f"New allocation history record for portfolio {portfolio_id}")

        # Check if rebalancing is needed
        if event_data.get('needs_rebalancing', False):
            self.logger.info(f"Triggering rebalancing for portfolio {portfolio_id}")

            # Queue rebalancing job
            self.portfolio_service.queue_optimization_job(
                portfolio_id=portfolio_id,
                trigger="allocation_update",
                trigger_data=event_data
            )
```

## Observer Manager Implementation

```python
class ObserverManager:
    """Central registry for managing observable objects and their subscriptions."""

    _instance = None

    def __new__(cls):
        """Implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ObserverManager, cls).__new__(cls)
            cls._instance._observables = {}
        return cls._instance

    def register_observable(self, name: str, observable: IObservable) -> None:
        """Register an observable with the manager."""
        self._observables[name] = observable

    def get_observable(self, name: str) -> IObservable:
        """Get an observable by name."""
        if name not in self._observables:
            raise KeyError(f"Observable '{name}' not registered")
        return self._observables[name]

    def register_observer(self, observable_name: str, event_type: str,
                         observer_func: Callable[[Dict[str, Any]], None]) -> None:
        """Register an observer with an observable for a specific event type."""
        observable = self.get_observable(observable_name)
        observable.subscribe(event_type, observer_func)

    def setup_default_observers(self, services: Dict[str, Any]) -> None:
        """Set up default observers with their respective observables."""
        # Market Data Observable and its observers
        market_data_observable = MarketDataObservable()
        self.register_observable('market_data', market_data_observable)

        # Create and register portfolio optimization observer
        portfolio_optimization_observer = PortfolioOptimizationObserver(services['portfolio_service'])
        self.register_observer(
            'market_data',
            'NEW_PERFORMANCE_HISTORY_RECORD',
            portfolio_optimization_observer.handle_new_performance_history_record
        )

        # Additional observers and their registrations would be set up here
```

## Integration with Flask Server

The Observer component integrates with the Flask Server architecture in the following ways:

1. **Initialization at Server Startup**

   - Observer Manager is initialized when the Flask server starts
   - Default observers are registered based on configuration

2. **Event Emission Points**

   - Market data updates from Supabase trigger events
   - Portfolio service operations emit relevant events
   - System monitoring metrics generate status events

3. **Observer Action Handlers**
   - Portfolio optimization triggered by market events
   - Notification generation for significant changes
   - Logging of system activity and errors
   - Metrics collection for performance analysis

## Observer Configuration

The behavior of observers can be configured through environment variables or configuration files:

```python
# Example configuration
OBSERVER_CONFIG = {
    'market_data': {
        'tables': {
            'performance_history': 'NEW_PERFORMANCE_HISTORY_RECORD'
        }
    },
    'portfolio': {
        'tables': {
            'abs_vault_allocation_history': 'NEW_ALLOCATION_HISTORY_RECORD'
        },
        'allocation_drift_threshold': 0.05,  # 5% threshold for allocation drift
    },
    'user': {
        'tables': {
            'abs_vault_info': ['NEW_VAULT_INFO_RECORD', 'UPDATED_VAULT_INFO_RECORD']
        }
    },
    'system': {
        'error_notification_level': 'WARNING',  # Minimum level for error notifications
        'resource_utilization_threshold': 0.8,  # 80% resource utilization threshold
    }
}
```

## Future Enhancements

1. **Distributed Event Processing**

   - Implement message queue integration (RabbitMQ, Kafka)
   - Support for distributed observer patterns across microservices
   - Event sourcing for complete history of system events

2. **Advanced Filtering Mechanisms**

   - Fine-grained control over event subscription with filtering
   - Temporal event patterns (event sequences, frequencies)
   - Complex event processing for multi-condition triggers

3. **Machine Learning Integration**
   - Anomaly detection for unusual market conditions
   - Predictive analytics for preemptive optimization
   - Adaptive thresholds based on historical patterns

## Best Practices

1. **Performance Considerations**

   - Keep observer handlers lightweight and fast
   - Use asynchronous processing for time-consuming operations
   - Implement rate limiting for high-frequency events

2. **Error Handling**

   - Implement robust error handling in observers
   - Prevent observer failures from cascading through the system
   - Log all observer exceptions for troubleshooting

3. **Testing**
   - Unit test each observable and observer in isolation
   - Integration test the observer registration process
   - Simulate events to verify correct observer behavior

## Conclusion

The Observer component provides a powerful mechanism for real-time monitoring and reactive behavior in the ABS Finance system. By implementing a decoupled event-driven architecture, it enables efficient communication between components while maintaining separation of concerns and supporting scalable system evolution.
