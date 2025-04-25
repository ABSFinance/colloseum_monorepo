"""
Portfolio State Observable

This module implements the Observable pattern for portfolio state changes.
It monitors allocation history records and vault info records and notifies observers.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from . import Observable, EventTypes

class PortfolioStateObservable(Observable):
    """Observable for portfolio state changes."""

    def __init__(self):
        """Initialize the PortfolioStateObservable.
        """
        super().__init__()
        self._logger = logging.getLogger(f"{__name__}.PortfolioStateObservable")
        self._logger.info(f"Initialized PortfolioStateObservable")

    def process_allocation_history_record(self, record: Dict[str, Any]) -> None:
        """Process a new allocation history record and emit events.
        
        Args:
            record: The allocation history record data
        """
        try:
            # Extract key data from the record
            pool_id = record.get('pool_id')
            allocated_pool_id = record.get('allocated_pool_id')
            amount = record.get('amount', 0)
            status = record.get('status')
            timestamp = record.get('created_at', datetime.now().isoformat())
            
            if pool_id is None:
                self._logger.warning("Allocation history record missing pool_id field")
                return
                
            # Prepare event data
            event_data = {
                'pool_id': pool_id,
                'allocated_pool_id': allocated_pool_id,
                'amount': amount,
                'status': status,
                'timestamp': timestamp,
            }
            
            self._logger.info(f"New allocation history record for pool {pool_id}: allocated_pool_id={allocated_pool_id}, amount={amount}")
            
            # Check for deposit event (pool_id equals allocated_pool_id and amount > 0)
            if pool_id == allocated_pool_id and amount > 0:
                self._logger.info(f"Detected deposit event for pool {pool_id}: amount {amount}")
                self.notify(EventTypes.DEPOSIT_EVENT, event_data)
            # Check for withdrawal event (pool_id equals allocated_pool_id, amount < 0, status = 'pending')
            elif pool_id == allocated_pool_id and amount < 0 and status == 'PENDING':
                self._logger.info(f"Detected withdrawal event for pool {pool_id}: amount {amount}, status {status}")
                self.notify(EventTypes.WITHDRAWAL_EVENT, event_data)
            else:
                self._logger.info(f"Ignoring allocation history record for pool {pool_id}: amount {amount}, status {status}")
  
        except Exception as e:
            self._logger.error(f"Error processing allocation history record: {str(e)}")