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
from datetime import datetime, timedelta, UTC

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
        
    async def initialize_market_data(self) -> None:
        """Initialize market data from Supabase performance history for all pools.
        Fetches all available performance history records.
        """
        if not self.supabase_client:
            self.logger.error("Supabase client not initialized")
            return
        
        try:
            # Fetch all performance history records without date restrictions
            response = await self.supabase_client.table('performance_history') \
                .select('*') \
                .order('created_at', desc=True) \
                .execute()
                
            if not response.data:
                self.logger.warning("No performance history found for any pool")
                return
                
            # Convert to DataFrame
            df = pd.DataFrame(response.data)
            
            # Use a better approach to parse timestamps that works for ISO8601 format variants
            try:
                # Use ISO8601 format which handles different ISO format variants
                df['timestamp_parsed'] = pd.to_datetime(df['created_at'], format='ISO8601')
                # Keep only the date part (year, month, day), removing time component
                df['timestamp_parsed'] = df['timestamp_parsed'].dt.date
                # Convert back to datetime for proper indexing
                df['timestamp_parsed'] = pd.to_datetime(df['timestamp_parsed'])
            except Exception as e:
                self.logger.warning(f"ISO8601 parsing failed: {str(e)}")
                # Fall back to pandas' flexible parser with error coercion
                df['timestamp_parsed'] = pd.to_datetime(df['created_at'], errors='coerce')
                # Keep only the date part if parsing succeeded
                if not df['timestamp_parsed'].isna().all():
                    df['timestamp_parsed'] = df['timestamp_parsed'].dt.date
                    # Convert back to datetime for proper indexing
                    df['timestamp_parsed'] = pd.to_datetime(df['timestamp_parsed'])
            
            # Drop rows with invalid timestamps (NaT)
            if df['timestamp_parsed'].isna().any():
                invalid_count = df['timestamp_parsed'].isna().sum()
                self.logger.warning(f"Dropped {invalid_count} rows with invalid timestamps")
                df = df.dropna(subset=['timestamp_parsed'])
            
            # Check if we have any valid data left
            if df.empty:
                self.logger.error("No valid data left after timestamp parsing")
                return
            
            # Before NaN replacement, check and log NaN counts
            for col in ['apy', 'tvl']:
                if col in df.columns:
                    nan_count = df[col].isna().sum()
                    if nan_count > 0:
                        self.logger.warning(f"Found {nan_count} NaN values in {col} column")
            
            # Convert numeric columns and replace NaN with 0
            for col in ['apy', 'tvl']:
                if col in df.columns:
                    # First convert to numeric with errors coerced to NaN
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    
                    # Count NaNs after conversion
                    nan_count = df[col].isna().sum()
                    if nan_count > 0:
                        self.logger.warning(f"After numeric conversion, found {nan_count} NaN values in {col}")
                    
                    # Fill NaN values with 0
                    df[col] = df[col].fillna(0)
                    
                    # Ensure column is float64 type
                    df[col] = df[col].astype(np.float64)
            
            # Group by pool_id and store each group in market_data
            for pool_id, group_df in df.groupby('pool_id'):
                # Set the timestamp as index for each group
                group_df = group_df.set_index('timestamp_parsed')
                
                # Check for any remaining NaN values
                nan_count = group_df.isna().sum().sum()
                if nan_count > 0:
                    self.logger.warning(f"Pool {pool_id}: Found {nan_count} remaining NaN values after grouping")
                
                # Replace any remaining NaN values with 0
                group_df = group_df.fillna(0)
                
                # Final check for NaN values
                if group_df.isna().sum().sum() > 0:
                    self.logger.error(f"Pool {pool_id}: Still have NaN values after fillna operation!")
                    # Forcefully replace any stubborn NaNs
                    for col in group_df.columns:
                        group_df[col] = group_df[col].replace([np.inf, -np.inf, np.nan], 0)
                
                # Store in market_data
                self.market_data[str(pool_id)] = group_df
                self.logger.info(f"Initialized market data for pool {pool_id} with {len(group_df)} records")
            
            self.logger.info(f"Initialized market data for {len(self.market_data)} pools")
            
        except Exception as e:
            self.logger.error(f"Error initializing market data: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
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
            # Ensure the data has the expected structure
            required_fields = ['created_at']
            for field in required_fields:
                if field not in performance_data:
                    self.logger.error(f"Performance data missing required field: {field}")
                    return
                    
            # Ensure apy field is present and convert NaN to 0
            if 'apy' not in performance_data:
                self.logger.warning(f"Performance data for {pool_id} is missing 'apy' field")
                performance_data['apy'] = 0.0  # Default value if apy is missing
            elif pd.isna(performance_data['apy']):
                self.logger.warning(f"Performance data for {pool_id} has NaN 'apy' value, replacing with 0")
                performance_data['apy'] = 0.0
            
            # Ensure tvl field is present and convert NaN to 0
            if 'tvl' not in performance_data:
                self.logger.warning(f"Performance data for {pool_id} is missing 'tvl' field")
                performance_data['tvl'] = 0.0  # Default value if tvl is missing
            elif pd.isna(performance_data['tvl']):
                self.logger.warning(f"Performance data for {pool_id} has NaN 'tvl' value, replacing with 0")
                performance_data['tvl'] = 0.0
            
            # Convert to DataFrame row
            df_row = pd.DataFrame([performance_data])
            
            # Parse timestamp using datetime with UTC timezone
            try:
                # Parse with explicit ISO8601 format to handle timezone information
                df_row['timestamp_parsed'] = pd.to_datetime(df_row['created_at'])
                
                # Ensure all timestamps are timezone-aware and in UTC
                if df_row['timestamp_parsed'].dt.tz is None:
                    df_row['timestamp_parsed'] = df_row['timestamp_parsed'].dt.tz_localize('UTC')
                else:
                    df_row['timestamp_parsed'] = df_row['timestamp_parsed'].dt.tz_convert('UTC')
                
            except Exception as e:
                # If parsing fails, log error and try generic parser with coercion
                self.logger.warning(f"Timestamp parsing failed: {str(e)}")
                df_row['timestamp_parsed'] = pd.to_datetime(df_row['created_at'], errors='coerce')
                # Ensure coerced timestamps are also timezone-aware
                if df_row['timestamp_parsed'].dt.tz is None:
                    df_row['timestamp_parsed'] = df_row['timestamp_parsed'].dt.tz_localize('UTC')
            
            # Check for invalid timestamps
            if df_row['timestamp_parsed'].isna().any():
                self.logger.warning(f"Invalid timestamp format in new performance data: {performance_data['created_at']}")
                return
                
            df_row.set_index('timestamp_parsed', inplace=True)
            
            # Convert any remaining NaN values to 0
            df_row = df_row.fillna(0)
            
            # Update or initialize market data - ensure pool_id is converted to string for consistency
            pool_id_str = str(pool_id)
            if pool_id_str in self.market_data:
                self.market_data[pool_id_str] = pd.concat([self.market_data[pool_id_str], df_row])
            else:
                self.market_data[pool_id_str] = df_row
                
            self.logger.info(f"Updated market data for pool {pool_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating market data for pool {pool_id}: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
    def update_vault(self, vault_info: Dict[str, Any]) -> None:
        """Initialize or update vault information.
        
        Args:
            vault_info: Dictionary containing vault configuration
        """
        pool_id = vault_info.get('pool_id')
        if not pool_id:
            if 'vault_info' in vault_info:
                vault_info = vault_info['vault_info']
                pool_id = vault_info.get('pool_id')
            else:
                self.logger.error(f"Vault info missing pool_id : {vault_info}")
                return
            
        # Initialize or update vault data structure
        if pool_id not in self.vaults:
            self.vaults[pool_id] = {
                'vault_info': vault_info,
                'current_allocation': {}
            }
        else:
            self.vaults[pool_id]['vault_info'] = vault_info
            
        self.logger.info(f"Updated vault {pool_id} with strategy {vault_info.get('strategy', 'min_risk')}")
        
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
        weights = vault_info.get('weight', [])
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
        # Validate inputs
        if not market_data:
            self.logger.error("No market data provided")
            return pd.DataFrame()
            
        if not allowed_pools:
            self.logger.error("No allowed pools specified")
            return pd.DataFrame()
        
        # Filter market data for allowed pools
        filtered_data = {
            pool_id: df 
            for pool_id, df in market_data.items() 
            if int(pool_id) in allowed_pools
        }
        
        if not filtered_data:
            missing_pools = set(allowed_pools) - set(market_data.keys())
            self.logger.error(f"No market data found for any allowed pools. Missing data for: {missing_pools}")
            return pd.DataFrame()
            
        # Check that all pools have data
        if len(filtered_data) != len(allowed_pools):
            missing_pools = set(allowed_pools) - set(filtered_data.keys())
            self.logger.warning(f"Missing market data for some allowed pools: {missing_pools}")
        
        # Collect returns for each allowed pool
        returns_data = []
        for pool_id, df in filtered_data.items():
            try:
                # Check if 'apy' column exists
                if 'apy' not in df.columns:
                    self.logger.error(f"Market data for pool {pool_id} is missing 'apy' column. Available columns: {df.columns.tolist()}")
                    continue
                
                # Ensure return values are numeric
                try:
                    # First ensure we have a proper DatetimeIndex
                    if not isinstance(df.index, pd.DatetimeIndex):
                        # Try to convert the index to datetime, handling timezone-aware datetimes
                        try:
                            # First convert to UTC if timezone-aware
                            if hasattr(df.index, 'tz') and df.index.tz is not None:
                                df.index = df.index.tz_convert('UTC')
                            # Then convert to datetime64
                            df.index = pd.to_datetime(df.index, utc=True)
                        except Exception as e:
                            self.logger.error(f"Failed to convert index to datetime for pool {pool_id}: {str(e)}")
                            continue
                    
                    # Now ensure the index is timezone-aware and in UTC
                    if df.index.tz is None:
                        df.index = df.index.tz_localize('UTC')
                    else:
                        df.index = df.index.tz_convert('UTC')
                    
                    # Convert apy column to numeric, forcing errors to NaN
                    numeric_returns = pd.to_numeric(df['apy'], errors='coerce')
                    
                    # Check if we have any non-numeric values that were converted to NaN
                    if numeric_returns.isna().any():
                        non_numeric_count = numeric_returns.isna().sum()
                        total_count = len(numeric_returns)
                        self.logger.warning(f"Pool {pool_id}: {non_numeric_count} out of {total_count} APY values were non-numeric and converted to NaN")
                    
                    # Drop NaN values if any
                    numeric_returns = numeric_returns.dropna()
                    
                    if len(numeric_returns) == 0:
                        self.logger.error(f"No valid numeric APY values for pool {pool_id}")
                        continue
                        
                    # Create a DataFrame with the numeric values, explicitly as float64
                    returns = numeric_returns.astype(np.float64).to_frame(pool_id)
                    
                    # Handle duplicate timestamps by taking the last value
                    returns = returns.groupby(returns.index).last()
                    
                    # Verify returns are numeric
                    if not pd.api.types.is_numeric_dtype(returns[pool_id]):
                        self.logger.error(f"Failed to convert APY to numeric for pool {pool_id}")
                        continue
                    
                except Exception as e:
                    self.logger.error(f"Error converting APY to numeric for pool {pool_id}: {str(e)}")
                    continue
                
                returns_data.append(returns)
                
            except Exception as e:
                self.logger.error(f"Error processing returns for pool {pool_id}: {str(e)}")
        
        if not returns_data:
            self.logger.error("Could not extract returns from any allowed pool")
            return pd.DataFrame()
            
        # Concatenate all returns
        try:
            returns = pd.concat(returns_data, axis=1)
            
            # Ensure we have enough data for optimization
            if len(returns) < 2:
                self.logger.warning(f"Limited return data available. Only {len(returns)} data points.")
                if len(returns) < 1:
                    self.logger.error("Insufficient data for portfolio optimization")
                    return pd.DataFrame()
            
            # Check for any remaining non-numeric values and convert dtype
            if returns.dtypes.apply(lambda x: not pd.api.types.is_numeric_dtype(x)).any():
                self.logger.warning(f"Non-numeric datatypes detected in returns: {returns.dtypes}")
                # Try to convert each column individually to handle potential errors
                for col in returns.columns:
                    try:
                        returns[col] = returns[col].astype(np.float64)
                    except Exception as e:
                        self.logger.error(f"Failed to convert column {col} to float64: {str(e)}")
                        # Try to handle potential string values by forcing conversion
                        returns[col] = pd.to_numeric(returns[col], errors='coerce')
                        # Drop any NaN values that resulted from the conversion
                        if returns[col].isna().any():
                            self.logger.warning(f"Converted non-numeric values to NaN in column {col}")
                            
            # Final conversion of entire DataFrame to float64
            try:
                returns = returns.astype(np.float64)
            except Exception as e:
                self.logger.error(f"Final conversion to float64 failed: {str(e)}")
                # If conversion fails, try to filter out problematic data
                returns = returns.select_dtypes(include=['number'])
                if returns.empty:
                    self.logger.error("No numeric data available after filtering")
                    return pd.DataFrame()
                returns = returns.astype(np.float64)
            
            return returns
        except Exception as e:
            self.logger.error(f"Error preparing returns data: {str(e)}")
            return pd.DataFrame()
        
    async def handle_market_data(self, data: Optional[Dict[str, Any]], vault_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle new market data and perform reoptimization.
        
        Args:
            data: Dictionary containing market data or event data, or None
            vault_data: Optional dictionary containing vault configuration
                        If provided, will override the existing vault data
            
        Returns:
            Dictionary containing optimization results
        """

        market_data = data

        
        # If we have market data for a pool that might be an underlying asset in vaults
        # Update the market data first
        if market_data:
            self.update_market_data(market_data)
            
            # Check if this pool is part of any vault's allowed pools
            affected_vaults = []
            pool_id = market_data.get('pool_id')
            for vault_id, vault_data in self.vaults.items():
                vault_info = vault_data.get('vault_info', {})
                allowed_pools = vault_info.get('allowed_pools', [])
                
                # Convert all allowed_pools to strings for comparison
                allowed_pools = [str(pool) for pool in allowed_pools]
                
                # If this pool is in the allowed pools, mark the vault for reoptimization
                if str(pool_id) in allowed_pools:
                    affected_vaults.append(vault_id)
            
            # If this pool affects multiple vaults, reoptimize them
            if affected_vaults and len(affected_vaults) > 0:
                self.logger.info(f"Market data for pool {pool_id} affects {len(affected_vaults)} vaults. Reoptimizing.")
                results = {}
                
                for affected_vault_id in affected_vaults:
                    # Reoptimize each affected vault
                    vault_result = await self.handle_market_data(
                        None,
                        self.vaults.get(affected_vault_id).get('vault_info')  # Pass the vault_info directly
                    )
                    results[affected_vault_id] = vault_result
            
        # If vault_data is provided, initialize or update the vault
        if vault_data:
            self.update_vault(vault_data)
            
        try:
            # Get vault configuration
            if not vault_data or 'pool_id' not in vault_data:
                if 'vault_info' in vault_data:
                    vault_data = vault_data['vault_info']
                    pool_id = vault_data.get('pool_id')
                else:
                    self.logger.error(f"Missing pool_id in vault data : {vault_data}")
                    return {
                        'status': 'error',
                        'message': f"Missing pool_id in vault data : {vault_data}",
                        'timestamp': pd.Timestamp.now(UTC).isoformat()
                    }
            else:
                pool_id = vault_data.get('pool_id')
            
            if pool_id not in self.vaults:
                self.logger.error(f"Vault {pool_id} not found")
                return {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': f"Vault {pool_id} not found",
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
            vault = self.vaults[pool_id]
            vault_info = vault['vault_info']
            
            # Get adaptor constraints
            adaptor_constraints = self._get_adaptor_constraints(vault_info)
            if not adaptor_constraints:
                self.logger.error(f"No valid adaptor constraints for vault {pool_id}")
                return {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': f"No valid adaptor constraints for vault {pool_id}",
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
            # Configure portfolio with allowed pools
            allowed_pools = vault_info.get('allowed_pools', [])

            first_allowed_pool = allowed_pools[0]

            # Check if we have market data for the allowed pools
            missing_pools = [p for p in allowed_pools if str(p) not in self.market_data]
            if missing_pools:
                self.logger.error(f"Missing market data for pools: {missing_pools}. Cannot optimize.")
                return {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': f"Missing market data for {len(missing_pools)} pools",
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
    
            self.port.assets = allowed_pools

            returns = self._prepare_returns(self.market_data, allowed_pools)
            
            # Check if we have valid returns data
            if returns.empty:
                self.logger.error(f"No valid returns data available for optimization of vault {pool_id}")
                return {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': "No valid returns data available for optimization",
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
            
            # Ensure returns are float64 before creating the portfolio
            try:
                returns = returns.astype(np.float64)
            except Exception as e:
                self.logger.error(f"Error converting returns to float64: {str(e)}")
                return {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': f"Data type conversion error: {str(e)}",
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }

            # Additional validation - check for NaN/inf values
            if returns.isna().any().any() or np.isinf(returns.values).any():
                # Replace any inf values with NaN
                returns = returns.replace([np.inf, -np.inf], np.nan)
                # Drop rows with any NaN values
                returns = returns.dropna()
                
                if returns.empty or len(returns) < 2:
                    self.logger.error("Insufficient valid data for optimization after cleaning")
                    return {
                        'pool_id': pool_id,
                        'status': 'error',
                        'message': "Insufficient valid data for optimization after cleaning NaN/inf values",
                        'timestamp': pd.Timestamp.now(UTC).isoformat()
                    }
            
            # Create a fresh Portfolio object with the clean returns data
            try:
                # Following the tutorial pattern for portfolio creation
                port = rp.Portfolio(returns=returns)
                
                # Set up the portfolio parameters 
                method_mu = 'hist'  # Method to estimate expected returns based on historical data
                method_cov = 'hist'  # Method to estimate covariance matrix based on historical data
                
                # Calculate asset statistics (this is required before optimization)
                port.assets_stats(method_mu=method_mu, method_cov=method_cov)
                
                # Set optimization parameters based on strategy
                model = 'Classic'  # Classic (historical)
                hist = True  # Use historical scenarios
                rf = 0  # Risk-free rate
                
                if vault_info.get('strategy') == 'min_risk':
                    weights = port.optimization(
                        model=model,
                        rm='MV',  # Mean-Variance
                        obj='MinRisk',  # Minimize risk
                        rf=rf,
                        hist=hist
                    )
                elif vault_info.get('strategy') == 'max_sharpe':
                    weights = port.optimization(
                        model=model,
                        rm='MV',  # Mean-Variance
                        obj='Sharpe',  # Maximize Sharpe ratio
                        rf=rf,
                        hist=hist
                    )
                else:
                    self.logger.error(f"Unknown strategy {vault_info.get('strategy')}")
                    return {
                        'pool_id': pool_id,
                        'status': 'error',
                        'message': f"Unknown strategy: {vault_info.get('strategy')}",
                        'timestamp': pd.Timestamp.now(UTC).isoformat()
                    }
            except Exception as e:
                self.logger.error(f"Error during portfolio optimization: {str(e)}")
                return {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': f"Optimization error: {str(e)}",
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
            # Convert optimization result to dictionary if it's not already
            weights_dict = {}
            if isinstance(weights, pd.Series):
                weights_dict = weights.to_dict()
            elif isinstance(weights, pd.DataFrame):
                # If it's a DataFrame, take the first column
                weights_dict = weights.iloc[:, 0].to_dict()
            elif isinstance(weights, dict):
                weights_dict = weights
            elif isinstance(weights, np.ndarray):
                # Convert numpy array to dictionary
                weights_dict = {
                    allowed_pools[i]: float(weights[i]) 
                    for i in range(min(len(allowed_pools), len(weights)))
                }
            else:
                self.logger.error(f"Unexpected weights type: {type(weights)}")
                weights_dict = {p: 1.0/len(allowed_pools) for p in allowed_pools}  # Equal weights fallback
                

            # Apply adaptor constraints
            constrained_weights = self._apply_adaptor_constraints(
                weights_dict,
                adaptor_constraints,
                vault_info
            )

            
            # Convert weights to allocation amounts
            total_amount = sum(vault['current_allocation'].values())
            # Handle case where there's no allocation yet
            if total_amount <= 0:
                total_amount = 1.0  # Default to 1.0 for initial allocation
                
            new_allocation = {
                int(asset): float(weight * total_amount)  # Ensure float values 
                for asset, weight in constrained_weights.items()
            }
            
            # Update vault allocation
            self.vaults[pool_id]['current_allocation'] = new_allocation
            
            return {
                'pool_id': pool_id,
                'allocation': new_allocation,
                'status': 'success',
                'timestamp': pd.Timestamp.now(UTC).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error optimizing portfolio for {pool_id}: {str(e)}")
            return {
                'pool_id': pool_id,
                'status': 'error',
                'message': str(e),
                'timestamp': pd.Timestamp.now(UTC).isoformat()
            }
            
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
        # Ensure all weights are float values
        weights = {k: float(v) for k, v in weights.items()}
        
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
                    scale_factor = float(max_weight) / float(current_weight)
                    for pool_id, weight in list(weights.items()):
                        if self._is_pool_in_adaptor(pool_id, adaptor):
                            weights[pool_id] = float(weight) * float(scale_factor)
                            
        # Normalize weights to sum to 1
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: float(v/total_weight) for k, v in weights.items()}
            
        # Final check for any non-float values
        for k, v in list(weights.items()):
            if not isinstance(v, float):
                weights[k] = float(v)
                
        return weights
            
    async def handle_vault_update(self, vault_info: Dict[str, Any], market_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle vault information updates (deposits/withdrawals/strategy changes).
        
        Args:
            vault_info: Updated vault information
            market_data: Optional market data to use for reoptimization
            
        Returns:
            Dictionary containing optimization results
        """
        pool_id = vault_info.get('pool_id')
        if not pool_id:
            self.logger.error("Vault update missing pool_id")
            return {
                'status': 'error',
                'message': "Vault update missing pool_id",
                'timestamp': pd.Timestamp.now(UTC).isoformat()
            }
            
        # Update vault information
        self.update_vault(vault_info)
        
        # If market_data is provided, use it for optimization
        if market_data:
            return await self.handle_market_data(market_data, vault_info)
        
        # Otherwise, use the vault_info for optimization if we have existing market data
        if pool_id in self.market_data:
            return await self.handle_market_data({'pool_id': pool_id}, vault_info)
            
        return {
            'pool_id': pool_id,
            'status': 'warning',
            'message': "Vault updated but no market data available for optimization",
            'timestamp': pd.Timestamp.now(UTC).isoformat()
        }

    def create_synthetic_returns(self, pool_ids: List[str], days: int = 30) -> Dict[str, pd.DataFrame]:
        """Create synthetic returns data for testing.
        
        Args:
            pool_ids: List of pool IDs to create data for
            days: Number of days of historical data to create
            
        Returns:
            Dictionary of pool_id to DataFrame with synthetic returns
        """
        self.logger.info(f"Creating synthetic returns data for {len(pool_ids)} pools over {days} days")
        
        # Create date range for the returns
        end_date = datetime.now(UTC)
        dates = pd.date_range(end=end_date, periods=days, freq='D')
        
        # Dictionary to store the synthetic market data
        synthetic_data = {}
        
        for pool_id in pool_ids:
            # Generate random APY values with a realistic distribution
            # Mean around 5% APY, standard deviation around 1%
            apy_values = np.random.normal(5.0, 1.0, size=days).astype(np.float64)
            
            # Create DataFrame
            df = pd.DataFrame({
                'id': range(1, days + 1),
                'pool_id': pool_id,
                'tvl': np.random.uniform(1000000, 5000000, size=days).astype(np.float64),
                'apy': apy_values,  # APY as percentage
                'created_at': [d.isoformat() for d in dates]
            })
            
            # Add datetime index using ISO8601 format for consistency
            try:
                df['timestamp_parsed'] = pd.to_datetime(df['created_at'], format='ISO8601')
            except Exception as e:
                self.logger.warning(f"ISO8601 parsing failed for synthetic data: {str(e)}")
                # Fallback to flexible parser (should not happen with synthetic data)
                df['timestamp_parsed'] = pd.to_datetime(df['created_at'], errors='coerce')
                
            df.set_index('timestamp_parsed', inplace=True)
            
            # Store in synthetic data dictionary
            synthetic_data[pool_id] = df
            
            self.logger.info(f"Created synthetic market data for pool {pool_id} with {len(df)} records")
            
        return synthetic_data

    async def initialize_vault_info(self) -> None:
        """Initialize vault information from Supabase for all vaults.
        Fetches all available vault records from abs_vault_info table.
        Also fetches abs_vault_allocation_history to determine current allocations.
        """
        if not self.supabase_client:
            self.logger.error("Supabase client not initialized")
            return
        
        try:
            # Fetch all vault records
            vault_response = await self.supabase_client.table('abs_vault_info') \
                .select('*') \
                .order('created_at', desc=True) \
                .execute()
                
            if not vault_response.data:
                self.logger.warning("No vault information found")
                return
                
            # Process each vault record
            vault_count = 0
            for vault_record in vault_response.data:
                try:
                    # Extract pool_id from the record
                    pool_id = vault_record.get('pool_id')
                    if not pool_id:
                        self.logger.warning(f"Skipping vault record missing pool_id: {vault_record}")
                        continue
                        
                    # Update the vault info in our local storage (without allocation yet)
                    self.update_vault(vault_record)
                    vault_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing vault record: {str(e)}")
                
            self.logger.info(f"Initialized {vault_count} vault configurations from Supabase")
            
            # Now fetch allocation history to determine current allocations
            alloc_response = await self.supabase_client.table('abs_vault_allocation_history') \
                .select('*') \
                .order('created_at', desc=True) \
                .execute()
                
            if not alloc_response.data:
                self.logger.warning("No allocation history found")
                return
                
            # Convert to DataFrame for easier processing
            alloc_df = pd.DataFrame(alloc_response.data)
            
            # Parse timestamps using ISO8601 format to avoid warnings
            try:
                alloc_df['created_at_parsed'] = pd.to_datetime(alloc_df['created_at'], format='ISO8601')
            except Exception as e:
                self.logger.warning(f"ISO8601 parsing failed for allocation history: {str(e)}")
                # Fall back to pandas' flexible parser with error coercion
                alloc_df['created_at_parsed'] = pd.to_datetime(alloc_df['created_at'], errors='coerce')
                
            # Drop rows with invalid timestamps (NaT)
            if alloc_df['created_at_parsed'].isna().any():
                invalid_count = alloc_df['created_at_parsed'].isna().sum()
                self.logger.warning(f"Dropped {invalid_count} rows with invalid timestamps from allocation history")
                alloc_df = alloc_df.dropna(subset=['created_at_parsed'])
            
            # Process allocation data by vault (pool_id)
            for pool_id, vault_data in self.vaults.items():
                try:
                    # Filter allocations for this vault and create a copy to avoid SettingWithCopyWarning
                    vault_allocations = alloc_df[alloc_df['pool_id'] == int(pool_id)].copy()
                    
                    if vault_allocations.empty:
                        self.logger.warning(f"No allocation history found for vault {pool_id}")
                        continue
                    
                    # Sort by timestamp so most recent allocations are processed first
                    vault_allocations = vault_allocations.sort_values('created_at_parsed', ascending=False)
                    
                    # Initialize allocation dictionary
                    current_allocation = {}
                    
                    # Two approaches are possible:
                    # 1. Use the most recent complete allocation set (snapshot approach)
                    # 2. Reconstruct by summing all additions/subtractions (cumulative approach)
                    
                    # Let's use the snapshot approach for simplicity and reliability
                    # Get unique timestamps in descending order (most recent first)
                    timestamps = vault_allocations['created_at_parsed'].unique()
                    
                    # Find most recent complete allocation
                    found_complete_allocation = False
                    for ts in timestamps:
                        # Get all allocations at this timestamp
                        ts_allocations = vault_allocations[vault_allocations['created_at_parsed'] == ts]
                        
                        # Check if all allocated_pool_ids have non-zero amounts at this timestamp
                        if (ts_allocations['amount'] > 0).all():
                            # This is a complete allocation, use it
                            for _, row in ts_allocations.iterrows():
                                allocated_pool_id = row['allocated_pool_id']
                                amount = row['amount']
                                # Initialize the key if it doesn't exist
                                if int(allocated_pool_id) not in current_allocation:
                                    current_allocation[int(allocated_pool_id)] = 0.0
                                current_allocation[int(allocated_pool_id)] += float(amount)
                            
                            self.logger.info(f"Found complete allocation for vault {pool_id} at {ts}")
                            found_complete_allocation = True
                            break
                    
                    # If no complete allocation found, use the cumulative approach
                    if not found_complete_allocation:
                        self.logger.info(f"No complete allocation found for vault {pool_id}, reconstructing from history")
                        
                        # Group by allocated_pool_id and sum amounts
                        allocation_sums = vault_allocations.groupby('allocated_pool_id')['amount'].sum()
                        
                        # Convert to dictionary
                        for allocated_pool_id, amount in allocation_sums.items():
                            if amount > 0:  # Only include positive allocations
                                # Always initialize the key in the dictionary first
                                current_allocation[int(allocated_pool_id)] = float(amount)
                    
                    # Update the vault's current allocation
                    self.vaults[pool_id]['current_allocation'] = current_allocation
                    self.logger.info(f"Updated current allocation for vault {pool_id} with {len(current_allocation)} allocated pools")
                    
                except Exception as e:
                    self.logger.error(f"Error processing allocation for vault {pool_id}: {str(e)}")
                    import traceback
                    self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            self.logger.info(f"Completed allocation initialization for {len(self.vaults)} vaults")
            
        except Exception as e:
            self.logger.error(f"Error initializing vault information: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
