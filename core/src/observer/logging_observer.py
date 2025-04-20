"""
Logging Observer

This module implements a logging observer that records all system events for audit and debugging.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

class LoggingObserver:
    """Observer that logs system events for auditing and debugging."""

    def __init__(self, log_level: str = "INFO", include_data: bool = True):
        """Initialize the logging observer.
        
        Args:
            log_level: Level at which to log events (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            include_data: Whether to include the full event data in logs (may be verbose)
        """
        self.log_level = getattr(logging, log_level.upper())
        self.include_data = include_data
        self.logger = logging.getLogger(f"{__name__}.LoggingObserver")
        self.event_counts: Dict[str, int] = {}  # Track counts of each event type
        
        self.logger.info(f"Initialized LoggingObserver with log_level={log_level}, include_data={include_data}")

    def _get_log_level_for_event(self, event_type: str) -> int:
        """Determine the appropriate log level based on event type."""
        # System errors get logged at ERROR level
        if event_type in ["ERROR_OCCURRENCE", "SERVICE_STATUS_CHANGE"] and "error" in str(event_type).lower():
            return logging.ERROR
            
        # High resource utilization and rebalance needed get logged at WARNING level
        if event_type in ["RESOURCE_UTILIZATION", "REBALANCE_NEEDED"]:
            return logging.WARNING
            
        # Everything else gets logged at the configured level
        return self.log_level

    def _format_event_data(self, event_data: Dict[str, Any]) -> str:
        """Format event data for logging."""
        if not self.include_data:
            return "Event data omitted"
            
        # Attempt to convert to JSON with nice formatting
        try:
            return json.dumps(event_data, indent=2, default=str)
        except Exception:
            # Fall back to simple string representation if JSON conversion fails
            return str(event_data)

    def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle any type of event by logging it appropriately.
        
        Args:
            event_type: The type of event being logged
            event_data: Data associated with the event
        """
        # Update event counter
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
        
        # Determine log level for this event
        log_level = self._get_log_level_for_event(event_type)
        
        # Create a formatted log message
        timestamp = event_data.get('timestamp', datetime.now().isoformat())
        log_prefix = f"EVENT [{event_type}] at {timestamp}"
        
        # Extract key identifiers from the event data for the log message
        identifiers = []
        if 'portfolio_id' in event_data:
            identifiers.append(f"portfolio={event_data['portfolio_id']}")
        if 'asset_symbol' in event_data:
            identifiers.append(f"asset={event_data['asset_symbol']}")
        if 'service' in event_data:
            identifiers.append(f"service={event_data['service']}")
            
        # Create the log message
        if identifiers:
            log_message = f"{log_prefix} ({', '.join(identifiers)})"
        else:
            log_message = log_prefix
            
        # Log the event
        self.logger.log(log_level, log_message)
        
        # If detailed logging is enabled, also log the event data
        if self.include_data and log_level >= self.log_level:
            data_str = self._format_event_data(event_data)
            # Log data at DEBUG level to avoid cluttering the main logs
            self.logger.debug(f"Event data for {event_type}:\n{data_str}")

    # Define specific handler methods for different event types
    # These all delegate to the general handle_event method but provide typing benefits
    
    # Market Events
    def handle_apy_change(self, event_data: Dict[str, Any]) -> None:
        """Handle APY change events by logging them."""
        self.handle_event("APY_CHANGE", event_data)
        
    def handle_liquidity_event(self, event_data: Dict[str, Any]) -> None:
        """Handle liquidity events by logging them."""
        self.handle_event("LIQUIDITY_EVENT", event_data)
    
    # Portfolio Events
    def handle_allocation_drift(self, event_data: Dict[str, Any]) -> None:
        """Handle allocation drift events by logging them."""
        self.handle_event("ALLOCATION_DRIFT", event_data)
        
    def handle_rebalance_needed(self, event_data: Dict[str, Any]) -> None:
        """Handle rebalance needed events by logging them."""
        self.handle_event("REBALANCE_NEEDED", event_data)
        
    def handle_performance_threshold(self, event_data: Dict[str, Any]) -> None:
        """Handle performance threshold events by logging them."""
        self.handle_event("PERFORMANCE_THRESHOLD", event_data)
    
    # System Events
    def handle_service_status_change(self, event_data: Dict[str, Any]) -> None:
        """Handle service status change events by logging them."""
        self.handle_event("SERVICE_STATUS_CHANGE", event_data)
        
    def handle_resource_utilization(self, event_data: Dict[str, Any]) -> None:
        """Handle resource utilization events by logging them."""
        self.handle_event("RESOURCE_UTILIZATION", event_data)
        
    def handle_error_occurrence(self, event_data: Dict[str, Any]) -> None:
        """Handle error occurrence events by logging them."""
        self.handle_event("ERROR_OCCURRENCE", event_data)
        
    def handle_scheduled_task(self, event_data: Dict[str, Any]) -> None:
        """Handle scheduled task events by logging them."""
        self.handle_event("SCHEDULED_TASK", event_data)
    
    # User Events
    def handle_preference_change(self, event_data: Dict[str, Any]) -> None:
        """Handle preference change events by logging them."""
        self.handle_event("PREFERENCE_CHANGE", event_data)
        
    def handle_strategy_modification(self, event_data: Dict[str, Any]) -> None:
        """Handle strategy modification events by logging them."""
        self.handle_event("STRATEGY_MODIFICATION", event_data)
        
    def handle_constraint_update(self, event_data: Dict[str, Any]) -> None:
        """Handle constraint update events by logging them."""
        self.handle_event("CONSTRAINT_UPDATE", event_data)
        
    def get_event_stats(self) -> Dict[str, int]:
        """Get statistics on the number of events logged by type."""
        return self.event_counts 