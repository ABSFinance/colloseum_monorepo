"""
Test Observer

This module implements a TestObserver class for testing and debugging the Observer system.
It logs and stores all events it receives.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Use absolute imports instead of relative imports
from src.observer import EventTypes
from src.observer.logging_observer import LoggingObserver

class TestObserver(LoggingObserver):
    """Observer for testing event handling.
    
    This observer stores all events it receives, allowing tests to check if
    events were properly triggered and handled. Useful for debugging and testing
    the Observer system.
    """
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize the test observer.
        
        Args:
            log_level: The logging level to use
        """
        super().__init__(log_level)
        self.events: Dict[str, List[Dict[str, Any]]] = {}
        self.event_counts: Dict[str, int] = {}
        self.logger.info("TestObserver initialized")
    
    def _store_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Store an event for later inspection.
        
        Args:
            event_type: The type of event
            event_data: The event data
        """
        if event_type not in self.events:
            self.events[event_type] = []
        
        # Add event data with timestamp
        event_data_with_timestamp = event_data.copy()
        if 'timestamp' not in event_data_with_timestamp:
            event_data_with_timestamp['_received_at'] = datetime.now().isoformat()
        
        self.events[event_type].append(event_data_with_timestamp)
        
        # Update count
        if event_type not in self.event_counts:
            self.event_counts[event_type] = 0
        self.event_counts[event_type] += 1
    
    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle any type of event.
        
        Args:
            event_type: The type of event
            event_data: The event data
        """
        super().handle_event(event_type, event_data)
        self._store_event(event_type, event_data)
    
    # Specific event type handlers
    
    def handle_new_performance_history_record(self, event_data: Dict[str, Any]) -> None:
        """Handle performance history record events.
        
        Args:
            event_data: The event data
        """
        self.handle_event(EventTypes.NEW_PERFORMANCE_HISTORY_RECORD, event_data)
    
    def handle_deposit_event(self, event_data: Dict[str, Any]) -> None:
        """Handle deposit events.
        
        Args:
            event_data: The event data
        """
        self.handle_event(EventTypes.DEPOSIT_EVENT, event_data)
    
    def handle_withdrawal_event(self, event_data: Dict[str, Any]) -> None:
        """Handle withdrawal events.
        
        Args:
            event_data: The event data
        """
        self.handle_event(EventTypes.WITHDRAWAL_EVENT, event_data)
    
    def handle_vault_info_record(self, event_data: Dict[str, Any]) -> None:
        """Handle vault info record events.
        
        Args:
            event_data: The event data
        """
        self.handle_event(EventTypes.VAULT_INFO_RECORD, event_data)
    
    # Utility methods for testing and reporting
    
    def clear(self) -> None:
        """Clear stored events."""
        self.events = {}
        self.event_counts = {}
        self.logger.info("TestObserver cleared")
    
    def get_events(self, event_type: str = None, pool_id: str = None) -> List[Dict[str, Any]]:
        """Get stored events of a specific type and/or for a specific pool.
        
        Args:
            event_type: The event type to filter by, or None for all events
            pool_id: The pool ID to filter by, or None for all pools
            
        Returns:
            A list of events
        """
        if event_type is None:
            # Return all events
            all_events = []
            for event_list in self.events.values():
                all_events.extend(event_list)
            
            # Filter by pool ID if provided
            if pool_id is not None:
                all_events = [e for e in all_events if e.get('pool_id') == pool_id]
                
            return all_events
        
        events = self.events.get(event_type, [])
        
        # Filter by pool ID if provided
        if pool_id is not None:
            events = [e for e in events if e.get('pool_id') == pool_id]
            
        return events
    
    def get_event_count(self, event_type: str = None, pool_id: str = None) -> int:
        """Get the count of events of a specific type and/or for a specific pool.
        
        Args:
            event_type: The event type to filter by, or None for all events
            pool_id: The pool ID to filter by, or None for all pools
            
        Returns:
            The number of matching events
        """
        if event_type is None and pool_id is None:
            # Return total count across all event types
            return sum(self.event_counts.values())
        
        if event_type is not None and pool_id is None:
            # Return count for specific event type
            return self.event_counts.get(event_type, 0)
        
        # Filter by both event type and pool ID or just pool ID
        matching_events = 0
        events_to_check = self.get_events(event_type)
        
        for event in events_to_check:
            if event.get('pool_id') == pool_id:
                matching_events += 1
        
        return matching_events
    
    def print_event_summary(self) -> None:
        """Print a summary of all received events."""
        print("\n===== EVENT SUMMARY =====")
        if not self.event_counts:
            print("No events received")
        else:
            for event_type, count in sorted(self.event_counts.items()):
                print(f"{event_type}: {count} events")
        print("========================\n")
    
    def print_event_details(self, event_type: str = None, pool_id: str = None) -> None:
        """Print details of events matching the filters.
        
        Args:
            event_type: The event type to filter by, or None for all events
            pool_id: The pool ID to filter by, or None for all pools
        """
        events = self.get_events(event_type, pool_id)
        
        if not events:
            print(f"No events found for filters: event_type={event_type}, pool_id={pool_id}")
            return
        
        print(f"\n===== EVENT DETAILS {'for ' + event_type if event_type else ''} "
              f"{'for pool ' + pool_id if pool_id else ''} =====")
        
        for i, event in enumerate(events):
            print(f"Event {i+1}:")
            for key, value in event.items():
                print(f"  {key}: {value}")
            print("")
        
        print("========================\n") 