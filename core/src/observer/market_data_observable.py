"""
Market Data Observable

This module provides an observable implementation for market data events.
It handles notifications related to performance history and market updates.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from . import Observable, EventTypes

class MarketDataObservable(Observable):
    """Observable for market data events."""

    def __init__(self):
        """Initialize the MarketDataObservable.
        """
        super().__init__()
        self.market_data = {}  # Store recent market data by pool_id
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info(f"Initialized MarketDataObservable")

    def process_performance_history_record(self, record: Dict[str, Any]) -> None:
        """Process a new performance history record and emit events.
        
        Args:
            record: The new performance history record
        """
        # Extract key data from the record
        pool_id = record.get('pool_id')
        timestamp = record.get('timestamp', datetime.now().isoformat())
        apy = record.get('apy', 0.0)
        tvl = record.get('tvl', 0.0)
        
        if pool_id is None:
            self.logger.warning("Received performance history record without pool_id")
            return
            
        # Prepare event data
        event_data = {
            'pool_id': pool_id,
            'apy': apy,
            'tvl': tvl,
            'timestamp': timestamp,
            'record_id': record.get('id'),
            'record': record  # Include the full record for completeness
        }
        
        self.logger.info(f"New performance history record for pool {pool_id}: APY={apy:.2%}, tvl={tvl}")
            
        # Notify observers of the new performance history record
        self.notify(EventTypes.NEW_PERFORMANCE_HISTORY_RECORD, event_data)
    
    def update_market_data(self, data: Dict[str, Any]) -> None:
        """Process market data update - wrapper to maintain backward compatibility.
        
        This method is kept for backward compatibility and now delegates to process_performance_history_record.
        
        Args:
            data: Dictionary containing market data updates
        """
        # Convert the market data to a performance history record format
        record = {
            'pool_id': data.get('pool_id'),
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'APY': data.get('apy', 0.0),
            'tvl': data.get('tvl', 0.0)
        }
        
        # Add any additional fields from the original data
        for key, value in data.items():
            if key not in ['pool_id', 'timestamp', 'apy', 'tvl']:
                record[key] = value
                
        # Process the record
        self.process_performance_history_record(record) 