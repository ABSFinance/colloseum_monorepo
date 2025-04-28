"""
Supabase Listener

This module implements a listener for Supabase realtime updates,
converting them into events for the Observer system.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

from . import EventTypes

class Observer:
    """Listener for Supabase realtime updates that feeds events into the Observer system."""

    def __init__(self, 
                supabase_client,
                observer_manager,
                market_data_table: str = 'performance_history',
                portfolio_state_table: str = 'abs_vault_allocation_history',
                vault_info_table: str = 'abs_vault_info'):
        """Initialize the Supabase listener.
        
        Args:
            supabase_client: Supabase client instance (async only)
            observer_manager: Observer manager instance
            market_data_table: Name of the market data table in Supabase
            portfolio_state_table: Name of the portfolio state table in Supabase
            vault_info_table: Name of the vault info table in Supabase
        """
        self.supabase_client = supabase_client
        self.observer_manager = observer_manager
        self.market_data_table = market_data_table
        self.portfolio_state_table = portfolio_state_table
        self.vault_info_table = vault_info_table
        self.logger = logging.getLogger(f"{__name__}.Observer")
        self.channel = self.supabase_client.channel('db-changed')
        self.is_running = False
        
        self.logger.info(f"Initialized Supabase listener for tables: {market_data_table}, {portfolio_state_table}, {vault_info_table}")
        self.logger.info("Using async Supabase client")
    
    async def start(self) -> None:
        """Start listening for Supabase realtime updates asynchronously.
        
        This method sets up realtime listening to Supabase channels.
        """
        if self.is_running:
            self.logger.warning("Supabase listener already running")
            return
            
        self.logger.info("Starting Supabase listener")
        self.is_running = True
        
        try:
            
            # Set up all subscriptions on the same channel
            self.channel.on_postgres_changes(
                    event="INSERT",
                    schema="public",
                    table=self.market_data_table,
                    callback=self._handle_performance_history
                ).on_postgres_changes(
                    event="INSERT",
                    schema="public",
                    table=self.portfolio_state_table,
                    callback=self._handle_allocation_history
                ).on_postgres_changes(
                    event="INSERT",
                    schema="public",
                    table=self.vault_info_table,
                    callback=self._handle_vault_info
                ).on_postgres_changes(
                    event="UPDATE",
                    schema="public",
                    table=self.vault_info_table,
                    callback=self._handle_vault_info
                )
            
            # Subscribe to the channel
            await self.channel.subscribe()
            await asyncio.sleep(1)  # Wait for subscription to be established
            
            self.logger.info("Supabase listener subscribed successfully to channel")
        except Exception as e:
            self.is_running = False
            self.logger.error(f"Failed to start Supabase listener: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """Stop listening for Supabase realtime updates asynchronously."""
        if not self.is_running:
            self.logger.warning("Supabase listener not running")
            return
            
        self.logger.info("Stopping Supabase listener")
        
        try:
            if self.channel:
                self.channel.unsubscribe()
            
            self.is_running = False
            self.logger.info("Supabase listener stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping Supabase listener: {str(e)}")
            raise
    
    def _handle_performance_history(self, payload: Dict[str, Any]) -> None:
        """Handle new performance history record insertions from Supabase.
        
        Args:
            payload: The payload containing the new record data
        """
        try:
            # Extract the record from the payload
            data = payload.get('data', {})
            record = data.get('record', {})
            if not record:
                self.logger.warning("Received empty performance history record from Supabase")
                return
                
            self.logger.debug(f"Received performance history insert: {json.dumps(record, default=str)}")
            
            # Forward the event to the market data observable
            market_data_observable = self.observer_manager.get_observable('market_data')
            market_data_observable.process_performance_history_record(record)
            
            pool_id = record.get('pool_id')
            self.logger.debug(f"Forwarded performance history record for pool {pool_id}")
        except Exception as e:
            self.logger.error(f"Error handling performance history insert: {str(e)}")
    
    def _handle_allocation_history(self, payload: Dict[str, Any]) -> None:
        """Handle new allocation history record insertions from Supabase.
        
        Args:
            payload: The payload containing the new record data
        """
        try:
            # Extract the new record from the payload

            data = payload.get('data', {})
            record = data.get('record', {})
            if not record:
                self.logger.warning("Received empty allocation history record from Supabase")
                return
                
            self.logger.debug(f"Received allocation history insert: {json.dumps(record, default=str)}")
            
            # Transform the record into the format expected by PortfolioStateObservable
            pool_id = record.get('pool_id')  # Using pool_id as the identifier
            if not pool_id:
                self.logger.warning("Allocation history record missing pool_id field")
                return
            
            # Forward the event to the portfolio state observable
            portfolio_state_observable = self.observer_manager.get_observable('portfolio_state')
            portfolio_state_observable.process_allocation_history_record(record)
            
            self.logger.debug(f"Forwarded allocation history record for pool {pool_id}")
        except Exception as e:
            self.logger.error(f"Error handling allocation history insert: {str(e)}")
    
    def _handle_vault_info(self, payload: Dict[str, Any]) -> None:
        """Handle new vault info record insertions from Supabase.
        
        Args:
            payload: The payload containing the new record data
        """
        try:
            # Extract the new record from the payload
            data = payload.get('data', {})
            record = data.get('record', {})
            if not record:
                self.logger.warning("Received empty vault info record from Supabase")
                return
                
            self.logger.debug(f"Received vault info insert: {json.dumps(record, default=str)}")
            
            # Transform the record into the format expected by UserActionObservable
            pool_id = record.get('pool_id')  # Using pool_id as the identifier
            if not pool_id:
                self.logger.warning("Vault info record missing pool_id field")
                return
            
            # Forward the event to the vault observable
            vault_observable = self.observer_manager.get_observable('vault')
            vault_observable.process_vault_info_record(record)
            
            self.logger.debug(f"Forwarded vault info insert for pool {pool_id}")
        except Exception as e:
            self.logger.error(f"Error handling vault info insert: {str(e)}")

    # For backward compatibility, keeping the original handlers with renamed methods
    def _handle_market_data_update(self, payload: Dict[str, Any]) -> None:
        """Legacy handler for market data updates, now redirects to performance history handler."""
        self._handle_performance_history(payload)
    
    def _handle_portfolio_state_update(self, payload: Dict[str, Any]) -> None:
        """Legacy handler for portfolio state updates, now redirects to allocation history handler."""
        self._handle_allocation_history(payload)
