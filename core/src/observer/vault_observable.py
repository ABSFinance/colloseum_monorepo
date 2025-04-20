"""
Vault Observable

This module provides an observable implementation for vault information events.
It handles notifications related to vault data updates, status changes, and performance metrics.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from . import Observable, EventTypes

class VaultObservable(Observable):
    """Observable for vault information changes."""
    
    def __init__(self):
        """Initialize the VaultObservable."""
        super().__init__()
        self.vault_info = {}  # Store vault information by vault_id
        self.logger = logging.getLogger(f"{__name__}.VaultObservable")
        self.logger.info(f"Initialized VaultObservable")

    def process_vault_info_record(self, record: Dict[str, Any]) -> None:
        """Process a vault info record (new or updated) and emit events.
        
        Args:
            record: The vault info record data
        """
        try:
            # Extract key data from the record
            pool_id = record.get('pool_id') or record.get('id')
            if pool_id is None:
                self.logger.warning("Vault info record missing pool_id field")
                return
                
            # Extract common fields
            strategy = record.get('strategy')
            allowed_pools = record.get('allowed_pools')
            timestamp = record.get('updated_at')
            
            # Prepare event data
            event_data = {
                'pool_id': pool_id,
                'strategy': strategy,
                'allowed_pools': allowed_pools,
                'timestamp': timestamp
            }
            
            # Notify observers of new vault info
            self.notify(EventTypes.VAULT_INFO_RECORD, event_data)
            
        except Exception as e:
            self.logger.error(f"Error processing vault info record: {str(e)}")

    def update_vault_info(self, data: Dict[str, Any]) -> None:
        """Process vault info update - wrapper to maintain backward compatibility.
        
        This method is kept for backward compatibility and delegates to process_vault_info_record.
        
        Args:
            data: Dictionary containing vault info updates
        """
        
        # Process the record
        self.process_vault_info_record(data, is_update=is_update, old_record=old_record) 