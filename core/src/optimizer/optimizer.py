"""
Portfolio Optimizer

This module implements portfolio optimization using Riskfolio-Lib.
It maintains vault information and performs reoptimization based on market data
and vault state changes.
"""

import logging
from typing import Dict, Any, Optional, List
import riskfolio as rp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Optimizer:
    """Portfolio optimizer using Riskfolio-Lib."""
    
    def __init__(self, supabase_client=None):
        """Initialize the optimizer.
        
        Args:
            supabase_client: Supabase client for fetching market data
        """
        self.logger = logging.getLogger(f"{__name__}.Optimizer")
        self.vaults: Dict[str, Dict[str, Any]] = {}  # Store vault info by pool_id
        self.port = rp.Portfolio(returns=None)  # Initialize empty portfolio
        self.supabase_client = supabase_client
        self.market_data: Dict[str, pd.DataFrame] = {}  # Store market data by pool_id
        
    async def initialize_market_data(self, pool_id: str, days: int = 30) -> None:
        """Initialize market data from Supabase performance history.
        
        Args:
            pool_id: ID of the pool to initialize data for
            days: Number of days of historical data to fetch
        """
        if not self.supabase_client:
            self.logger.error("Supabase client not initialized")
            return
            
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Fetch performance history
            response = await self.supabase_client.table('performance_history') \
                .select('*') \
                .eq('pool_id', pool_id) \
                .gte('created_at', start_date.isoformat()) \
                .lte('created_at', end_date.isoformat()) \
                .order('created_at', desc=True) \
                .execute()
                
            if not response.data:
                self.logger.warning(f"No performance history found for pool {pool_id}")
                return
                
            # Convert to DataFrame
            df = pd.DataFrame(response.data)
            df['timestamp'] = pd.to_datetime(df['created_at'])
            df.set_index('timestamp', inplace=True)
            
            # Store market data
            self.market_data[pool_id] = df
            self.logger.info(f"Initialized market data for pool {pool_id}")
            
        except Exception as e:
            self.logger.error(f"Error initializing market data for pool {pool_id}: {str(e)}")
            
    def update_market_data(self, performance_data: Dict[str, Any]) -> None:
        """Update market data with new performance history record.
        
        Args:
            performance_data: New performance history record
        """
        pool_id = performance_data.get('pool_id')
        if not pool_id:
            self.logger.error("Performance data missing pool_id")
            return
            
        try:
            # Convert to DataFrame row
            df_row = pd.DataFrame([performance_data])
            df_row['timestamp'] = pd.to_datetime(df_row['created_at'])
            df_row.set_index('timestamp', inplace=True)
            
            # Update or initialize market data
            if pool_id in self.market_data:
                self.market_data[pool_id] = pd.concat([self.market_data[pool_id], df_row])
            else:
                self.market_data[pool_id] = df_row
                
            self.logger.info(f"Updated market data for pool {pool_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating market data for pool {pool_id}: {str(e)}")
            
    def initialize_vault(self, vault_info: Dict[str, Any]) -> None:
        """Initialize or update vault information.
        
        Args:
            vault_info: Dictionary containing vault configuration
        """
        pool_id = vault_info.get('pool_id')
        if not pool_id:
            self.logger.error("Vault info missing pool_id")
            return
            
        # Initialize or update vault data structure
        if pool_id not in self.vaults:
            self.vaults[pool_id] = {
                'vault_info': vault_info,
                'current_allocation': {}
            }
        else:
            self.vaults[pool_id]['vault_info'] = vault_info
            
        self.logger.info(f"Initialized vault {pool_id} with strategy {vault_info.get('strategy', 'min_risk')}")
        
    def update_allocation(self, pool_id: str, allocation_data: Dict[int, float]) -> None:
        """Update current allocation for a vault.
        
        Args:
            pool_id: ID of the vault
            allocation_data: Dictionary mapping allocated_pool_id to amount
        """
        if pool_id not in self.vaults:
            self.logger.error(f"Unknown vault {pool_id}")
            return
            
        self.vaults[pool_id]['current_allocation'] = allocation_data
        self.logger.info(f"Updated allocation for vault {pool_id}")
        
    def _get_adaptor_constraints(self, vault_info: Dict[str, Any]) -> Dict[str, List[float]]:
        """Get adaptor weight constraints from vault info.
        
        Args:
            vault_info: Vault configuration information
            
        Returns:
            Dictionary mapping adaptor names to [min_weight, max_weight]
        """
        adaptors = vault_info.get('adaptors', [])
        weights = vault_info.get('weights', [])
        allowed_pools = vault_info.get('allowed_pools', [])
        
        if not adaptors or not weights or not allowed_pools:
            self.logger.error("Missing adaptor configuration")
            return {}
            
        if len(adaptors) != len(weights):
            self.logger.error("Mismatch between adaptors and weights")
            return {}
            
        # Create mapping of adaptor to its pools
        adaptor_pools = {}
        for i, adaptor in enumerate(adaptors):
            adaptor_pools[adaptor] = []
            for pool in allowed_pools:
                # This is a placeholder - implement actual pool to adaptor mapping logic
                if self._is_pool_in_adaptor(pool, adaptor):
                    adaptor_pools[adaptor].append(pool)
                    
        # Create weight constraints
        constraints = {}
        for adaptor, pools in adaptor_pools.items():
            if pools:  # Only add constraints for adaptors with allowed pools
                weight = weights[adaptors.index(adaptor)] / 100.0  # Convert percentage to decimal
                constraints[adaptor] = [0.0, weight]  # [min_weight, max_weight]
                
        return constraints
        
    def _is_pool_in_adaptor(self, pool_id: str, adaptor: str) -> bool:
        """Check if a pool belongs to an adaptor.
        
        Args:
            pool_id: ID of the pool
            adaptor: Name of the adaptor
            
        Returns:
            True if pool belongs to adaptor, False otherwise
        """
        # This is a placeholder - implement actual pool to adaptor mapping logic
        # For now, we'll assume the mapping is provided in the vault info
        return True
        
    def _prepare_returns(self, market_data: Dict[str, pd.DataFrame], allowed_pools: List[str]) -> pd.DataFrame:
        """Prepare returns DataFrame from market data.
        
        Args:
            market_data: Dictionary of pool_id to DataFrame containing market data
            allowed_pools: List of allowed pool IDs
            
        Returns:
            DataFrame containing asset returns for allowed pools
        """
        # Filter market data for allowed pools
        filtered_data = {
            pool_id: df 
            for pool_id, df in market_data.items() 
            if pool_id in allowed_pools
        }
        
        if not filtered_data:
            self.logger.error("No market data found for allowed pools")
            return pd.DataFrame()
            
        # Collect returns for each allowed pool
        returns_data = []
        for pool_id, df in filtered_data.items():
            # Select the return column from the market data
            # This is a placeholder - adjust based on your actual data structure
            returns = df['return'].to_frame(pool_id)
            returns_data.append(returns)
            
        # Concatenate all returns
        returns = pd.concat(returns_data, axis=1)
        
        # Calculate returns if needed (assuming we have price data)
        # This is a placeholder - implement based on your actual data format
        returns = returns.pct_change().dropna()
        
        return returns
        
    def handle_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new market data and perform reoptimization.
        
        Args:
            market_data: Dictionary containing market data
            
        Returns:
            Dictionary containing optimization results
        """
        pool_id = market_data.get('pool_id')
        if not pool_id or pool_id not in self.vaults:
            self.logger.error(f"Market data for unknown vault {pool_id}")
            return {}
            
        try:
            # Update market data with new record
            self.update_market_data(market_data)
            
            # Get vault configuration
            vault = self.vaults[pool_id]
            vault_info = vault['vault_info']
            
            # Get adaptor constraints
            adaptor_constraints = self._get_adaptor_constraints(vault_info)
            if not adaptor_constraints:
                self.logger.error(f"No valid adaptor constraints for vault {pool_id}")
                return {}
                
            # Configure portfolio with allowed pools
            allowed_pools = vault_info.get('allowed_pools', [])
            self.port.assets = allowed_pools
            self.port.returns = self._prepare_returns(self.market_data, allowed_pools)
            
            # Set optimization parameters based on strategy
            if vault_info.get('strategy') == 'min_risk':
                weights = self.port.optimization(
                    model='Classic',
                    rm='MV',
                    obj='MinRisk',
                    rf=0,
                    hist=True
                )
            elif vault_info.get('strategy') == 'max_sharpe':
                weights = self.port.optimization(
                    model='Classic',
                    rm='MV',
                    obj='Sharpe',
                    rf=0,
                    hist=True
                )
            else:
                self.logger.error(f"Unknown strategy {vault_info.get('strategy')}")
                return {}
                
            # Apply adaptor constraints
            constrained_weights = self._apply_adaptor_constraints(
                weights.to_dict(),
                adaptor_constraints,
                vault_info
            )
            
            # Convert weights to allocation amounts
            total_amount = sum(vault['current_allocation'].values())
            new_allocation = {
                int(asset): weight * total_amount 
                for asset, weight in constrained_weights.items()
            }
            
            # Update vault allocation
            self.vaults[pool_id]['current_allocation'] = new_allocation
            
            return {
                'pool_id': pool_id,
                'allocation': new_allocation,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing portfolio for {pool_id}: {str(e)}")
            return {}
            
    def _apply_adaptor_constraints(self, 
                                 weights: Dict[str, float],
                                 constraints: Dict[str, List[float]],
                                 vault_info: Dict[str, Any]) -> Dict[str, float]:
        """Apply adaptor weight constraints to portfolio weights.
        
        Args:
            weights: Dictionary of pool_id to weight
            constraints: Dictionary of adaptor to [min_weight, max_weight]
            vault_info: Vault configuration information
            
        Returns:
            Dictionary of constrained weights
        """
        # Group weights by adaptor
        adaptor_weights = {}
        for pool_id, weight in weights.items():
            for adaptor in vault_info.get('adaptors', []):
                if self._is_pool_in_adaptor(pool_id, adaptor):
                    if adaptor not in adaptor_weights:
                        adaptor_weights[adaptor] = 0.0
                    adaptor_weights[adaptor] += weight
                    
        # Scale weights to satisfy constraints
        for adaptor, current_weight in adaptor_weights.items():
            if adaptor in constraints:
                min_weight, max_weight = constraints[adaptor]
                if current_weight > max_weight:
                    # Scale down weights for this adaptor
                    scale_factor = max_weight / current_weight
                    for pool_id, weight in weights.items():
                        if self._is_pool_in_adaptor(pool_id, adaptor):
                            weights[pool_id] *= scale_factor
                            
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
            
        return weights
            
    def handle_vault_update(self, vault_info: Dict[str, Any]) -> Dict[str, Any]:
        """Handle vault information updates (deposits/withdrawals/strategy changes).
        
        Args:
            vault_info: Updated vault information
            
        Returns:
            Dictionary containing optimization results
        """
        pool_id = vault_info.get('pool_id')
        if not pool_id:
            self.logger.error("Vault update missing pool_id")
            return {}
            
        # Update vault information
        self.initialize_vault(vault_info)
        
        # If we have market data, perform reoptimization
        if pool_id in self.market_data:
            return self.handle_market_data(vault_info)
            
        return {}
