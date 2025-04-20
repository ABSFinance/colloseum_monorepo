"""
Observer Component

This module implements the Observer pattern for the ABS Finance system, providing a decoupled 
event-driven architecture for real-time monitoring and reactive behavior.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Callable, Any, Optional
import logging

# Set up logger for the observer module
logger = logging.getLogger(__name__)

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
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def subscribe(self, event_type: str, observer: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribe an observer to a specific event type."""
        if event_type not in self._observers:
            self._observers[event_type] = []
        if observer not in self._observers[event_type]:
            self._observers[event_type].append(observer)
            self._logger.debug(f"Observer {observer.__qualname__} subscribed to {event_type}")

    def unsubscribe(self, event_type: str, observer: Callable[[Dict[str, Any]], None]) -> None:
        """Unsubscribe an observer from a specific event type."""
        if event_type in self._observers and observer in self._observers[event_type]:
            self._observers[event_type].remove(observer)
            self._logger.debug(f"Observer {observer.__qualname__} unsubscribed from {event_type}")

    def notify(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Notify all observers of an event."""
        if event_type in self._observers:
            self._logger.debug(f"Notifying {len(self._observers[event_type])} observers of {event_type} event")
            for observer in self._observers[event_type]:
                try:
                    observer(event_data)
                except Exception as e:
                    self._logger.error(f"Error in observer {observer.__qualname__} handling {event_type}: {str(e)}")


class ObserverManager:
    """Central registry for managing observable objects and their subscriptions."""

    _instance = None

    def __new__(cls):
        """Implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(ObserverManager, cls).__new__(cls)
            cls._instance._observables = {}
            cls._instance._logger = logging.getLogger(f"{__name__}.ObserverManager")
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._logger.info("Initializing Observer Manager")
            self._initialized = True

    def register_observable(self, name: str, observable: IObservable) -> None:
        """Register an observable with the manager."""
        self._observables[name] = observable
        self._logger.info(f"Registered observable: {name}")

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
        self._logger.info(f"Registered observer {observer_func.__qualname__} for {observable_name}.{event_type}")

    def setup_default_observers(self, services: Dict[str, Any]) -> None:
        """Set up default observers with their respective observables.
        
        Args:
            services: Dictionary of service objects required by observers
        """
        self._logger.info("Setting up default observers")

# Define event type constants
class EventTypes:
    """Constants for event types used throughout the system."""
    
    # Market Events
    NEW_PERFORMANCE_HISTORY_RECORD = "NEW_PERFORMANCE_HISTORY_RECORD"
    
    # Portfolio Events
    NEW_ALLOCATION_HISTORY_RECORD = "NEW_ALLOCATION_HISTORY_RECORD"
    ALLOCATION_DRIFT = "ALLOCATION_DRIFT"
    DEPOSIT_EVENT = "DEPOSIT_EVENT"
    WITHDRAWAL_EVENT = "WITHDRAWAL_EVENT"
    
    # System Events
    SERVICE_STATUS_CHANGE = "SERVICE_STATUS_CHANGE"
    RESOURCE_UTILIZATION = "RESOURCE_UTILIZATION"
    ERROR_OCCURRENCE = "ERROR_OCCURRENCE"
    SCHEDULED_TASK = "SCHEDULED_TASK"
    
    # User Events
    VAULT_INFO_RECORD = "VAULT_INFO_RECORD"
