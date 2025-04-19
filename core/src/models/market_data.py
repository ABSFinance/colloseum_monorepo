#!/usr/bin/env python3
"""
Market Data Model

This module defines the data models and interfaces for retrieving and
processing market data required for portfolio optimization.
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass, field


@dataclass
class MarketMetricsBase:
    """Base class for all market metric data types."""
    id: str
    name: str
    address: str
    pool_id: int
    org_id: int
    underlying_token: str
    description: str
    tvl: float
    apy: float = 0.0
    created_at: datetime
    org_name: str
    org_logo: str
    token_symbol: str
    token_logo: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'pool_id': self.pool_id,
            'org_id': self.org_id,
            'underlying_token': self.underlying_token,
            'description': self.description,
            'tvl': self.tvl,
            'apy': self.apy,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'org_name': self.org_name,
            'org_logo': self.org_logo,
            'token_symbol': self.token_symbol,
            'token_logo': self.token_logo
        }


@dataclass
class DriftVaultMetrics(MarketMetricsBase):
    """Data model for Drift Vault metrics."""
    capacity: float
    strategy: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'capacity': self.capacity,
            'strategy': self.strategy
        })
        return base_dict


@dataclass
class TokenInfo:
    """Data model for token information."""
    address: str
    symbol: str
    logo_url: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'address': self.address,
            'symbol': self.symbol,
            'logo_url': self.logo_url
        }


@dataclass
class YieldPoolMetrics(MarketMetricsBase):
    """Data model for Yield Pool metrics."""
    chain: str
    underlying_tokens: List[str] = field(default_factory=list)  # Changed to array
    token_details: List[TokenInfo] = field(default_factory=list)  # Added for token details

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'chain': self.chain,
            'underlying_tokens': self.underlying_tokens,
            'token_details': [token.to_dict() for token in self.token_details]
        })
        return base_dict


@dataclass
class LendingPoolMetrics(MarketMetricsBase):
    """Data model for Lending Pool metrics."""
    collateral_factor: float
    ltv_ratio: float
    liquidity_threshold: float
    supply_cap: float
    borrow_cap: float
    utilization_rate: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'collateral_factor': self.collateral_factor,
            'ltv_ratio': self.ltv_ratio,
            'liquidity_threshold': self.liquidity_threshold,
            'supply_cap': self.supply_cap,
            'borrow_cap': self.borrow_cap,
            'utilization_rate': self.utilization_rate
        })
        return base_dict


@dataclass
class AbsVaultMetrics(MarketMetricsBase):
    """Data model for ABS Vault metrics."""
    capacity: float
    adaptors: List[str]
    allowed_pools: List[str]
    allocation_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'capacity': self.capacity,
            'adaptors': self.adaptors,
            'allowed_pools': self.allowed_pools,
            'allocation_count': self.allocation_count
        })
        return base_dict


@dataclass
class PerformanceHistory:
    """Data model for historical performance data."""
    id: int
    pool_id: int
    tvl: float
    apy: float
    volume: float
    max_drawdown: float
    risk_adjusted_return: float
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'pool_id': self.pool_id,
            'tvl': self.tvl,
            'apy': self.apy,
            'volume': self.volume,
            'max_drawdown': self.max_drawdown,
            'risk_adjusted_return': self.risk_adjusted_return,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


@dataclass
class AllocationHistory:
    """Data model for allocation history data."""
    id: int
    pool_id: int
    allocated_pool_id: int
    allocated_percentage: float
    amount: float
    apy: float
    earnings: float
    created_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.id,
            'pool_id': self.pool_id,
            'allocated_pool_id': self.allocated_pool_id,
            'allocated_percentage': self.allocated_percentage,
            'amount': self.amount,
            'apy': self.apy,
            'earnings': self.earnings,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at
        }


@dataclass
class MarketMetrics:
    """Container for all market metrics data."""
    drift_vaults: List[DriftVaultMetrics] = field(default_factory=list)
    yield_pools: List[YieldPoolMetrics] = field(default_factory=list)
    lending_pools: List[LendingPoolMetrics] = field(default_factory=list)
    abs_vaults: List[AbsVaultMetrics] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_count(self) -> int:
        """Get total count of all assets."""
        return len(self.drift_vaults) + len(self.yield_pools) + len(self.lending_pools) + len(self.abs_vaults)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'drift_vaults': [dv.to_dict() for dv in self.drift_vaults],
            'yield_pools': [yp.to_dict() for yp in self.yield_pools],
            'lending_pools': [lp.to_dict() for lp in self.lending_pools],
            'abs_vaults': [av.to_dict() for av in self.abs_vaults],
            'timestamp': self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MarketMetrics':
        """Create a MarketMetrics instance from a dictionary."""
        # Process timestamp
        timestamp = data.get('timestamp')
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        # Convert lists of dicts to lists of objects
        drift_vaults = [
            DriftVaultMetrics(
                id=dv.get('id'),
                name=dv.get('name'),
                address=dv.get('address'),
                pool_id=dv.get('pool_id'),
                org_id=dv.get('org_id'),
                underlying_token=dv.get('underlying_token'),
                description=dv.get('description', ''),
                tvl=dv.get('tvl', 0.0),
                apy=dv.get('apy', 0.0),
                created_at=datetime.fromisoformat(dv.get('created_at')) if isinstance(dv.get('created_at'), str) else dv.get('created_at'),
                org_name=dv.get('org_name', ''),
                org_logo=dv.get('org_logo', ''),
                token_symbol=dv.get('token_symbol', ''),
                token_logo=dv.get('token_logo', ''),
                capacity=dv.get('capacity', 0.0),
                strategy=dv.get('strategy', '')
            )
            for dv in data.get('drift_vaults', [])
        ]
        
        yield_pools = []
        for yp in data.get('yield_pools', []):
            # Process token details
            token_details = []
            if 'token_details' in yp and yp['token_details']:
                token_details = [
                    TokenInfo(
                        address=td.get('address', ''),
                        symbol=td.get('symbol', ''),
                        logo_url=td.get('logo_url', '')
                    )
                    for td in yp['token_details']
                ]
            
            yield_pools.append(
                YieldPoolMetrics(
                    id=yp.get('id'),
                    name=yp.get('name'),
                    address=yp.get('address'),
                    pool_id=yp.get('pool_id'),
                    org_id=yp.get('org_id'),
                    underlying_token=yp.get('underlying_tokens', [])[0] if yp.get('underlying_tokens') and len(yp.get('underlying_tokens', [])) > 0 else '',
                    description=yp.get('description', ''),
                    tvl=yp.get('tvl', 0.0),
                    apy=yp.get('apy', 0.0),
                    created_at=datetime.fromisoformat(yp.get('created_at')) if isinstance(yp.get('created_at'), str) else yp.get('created_at'),
                    org_name=yp.get('org_name', ''),
                    org_logo=yp.get('org_logo', ''),
                    token_symbol=yp.get('token_symbol', ''),
                    token_logo=yp.get('token_logo', ''),
                    chain=yp.get('chain', ''),
                    underlying_tokens=yp.get('underlying_tokens', []),
                    token_details=token_details
                )
            )
        
        lending_pools = [
            LendingPoolMetrics(
                id=lp.get('id'),
                name=lp.get('name'),
                address=lp.get('address'),
                pool_id=lp.get('pool_id'),
                org_id=lp.get('org_id'),
                underlying_token=lp.get('underlying_token'),
                description=lp.get('description', ''),
                tvl=lp.get('tvl', 0.0),
                apy=lp.get('apy', 0.0),
                created_at=datetime.fromisoformat(lp.get('created_at')) if isinstance(lp.get('created_at'), str) else lp.get('created_at'),
                org_name=lp.get('org_name', ''),
                org_logo=lp.get('org_logo', ''),
                token_symbol=lp.get('token_symbol', ''),
                token_logo=lp.get('token_logo', ''),
                collateral_factor=lp.get('collateral_factor', 0.0),
                ltv_ratio=lp.get('ltv_ratio', 0.0),
                liquidity_threshold=lp.get('liquidation_threshold', 0.0),
                supply_cap=lp.get('supply_cap', 0.0),
                borrow_cap=lp.get('borrow_cap', 0.0),
                utilization_rate=lp.get('utilization_rate', 0.0)
            )
            for lp in data.get('lending_pools', [])
        ]
        
        abs_vaults = [
            AbsVaultMetrics(
                id=av.get('id'),
                name=av.get('name'),
                address=av.get('address'),
                pool_id=av.get('pool_id'),
                org_id=av.get('org_id'),
                underlying_token=av.get('underlying_token'),
                description=av.get('description', ''),
                tvl=av.get('tvl', 0.0),
                apy=av.get('apy', 0.0),
                created_at=datetime.fromisoformat(av.get('created_at')) if isinstance(av.get('created_at'), str) else av.get('created_at'),
                org_name=av.get('org_name', ''),
                org_logo=av.get('org_logo', ''),
                token_symbol=av.get('token_symbol', ''),
                token_logo=av.get('token_logo', ''),
                capacity=av.get('capacity', 0.0),
                adaptors=av.get('adaptors', []),
                allowed_pools=av.get('allowed_pools', []),
                allocation_count=av.get('allocation_count', 0)
            )
            for av in data.get('abs_vaults', [])
        ]
        
        return cls(
            drift_vaults=drift_vaults,
            yield_pools=yield_pools,
            lending_pools=lending_pools,
            abs_vaults=abs_vaults,
            timestamp=timestamp,
            metadata=data.get('metadata', {})
        )


class MarketData:
    """
    Market Data service for retrieving and processing market data.
    This class serves as the primary interface for accessing market data.
    """
    
    def __init__(self, supabase_client=None):
        """
        Initialize the MarketData service.
        
        Args:
            supabase_client: The Supabase client for database access
        """
        self.supabase = supabase_client
        
    async def get_market_metrics(
        self, 
        asset_ids: Optional[List[str]] = None, 
        asset_types: Optional[List[str]] = None
    ) -> MarketMetrics:
        """
        Retrieve market metrics for specified assets or asset types.
        
        Args:
            asset_ids: Optional list of asset IDs to retrieve
            asset_types: Optional list of asset types (drift_vault, yield_pool, lending_pool, abs_vault)
            
        Returns:
            MarketMetrics object containing the requested metrics
        """
        if self.supabase is None:
            raise ValueError("Supabase client is not initialized")
        
        # Call the get_market_metrics function in the database
        response = await self.supabase.rpc(
            'get_market_metrics',
            {
                'asset_ids': asset_ids,
                'asset_types': asset_types
            }
        ).execute()
        
        if 'error' in response:
            raise Exception(f"Error retrieving market metrics: {response['error']}")
        
        # Convert the response data to a MarketMetrics object
        return MarketMetrics.from_dict(response['data'])
    
    # async def get_market_data(
    #     self,
    #     asset_ids: List[str],
    #     start_date: datetime,
    #     end_date: datetime,
    #     frequency: str = 'daily'
    # ) -> Dict[str, pd.DataFrame]:
    #     """
    #     Retrieve historical market data for specified assets over a time period.
        
    #     Args:
    #         asset_ids: List of asset IDs to retrieve data for
    #         start_date: Beginning of the time period
    #         end_date: End of the time period
    #         frequency: Data frequency (daily, weekly, monthly)
            
    #     Returns:
    #         Dictionary mapping asset IDs to DataFrames of historical data
    #     """
    #     if self.supabase is None:
    #         raise ValueError("Supabase client is not initialized")
        
    #     result = {}
        
    #     # Process each asset ID
    #     for asset_id in asset_ids:
    #         # First determine the pool_id from the asset_id
    #         pool_id = await self._get_pool_id_from_asset_id(asset_id)
            
    #         if not pool_id:
    #             continue
            
    #         # Fetch performance history data
    #         query = self.supabase.table('performance_history') \
    #             .select('*') \
    #             .eq('pool_id', pool_id) \
    #             .gte('created_at', start_date.isoformat()) \
    #             .lte('created_at', end_date.isoformat()) \
    #             .order('created_at', ascending=True)
            
    #         response = await query.execute()
            
    #         if 'error' in response:
    #             raise Exception(f"Error retrieving market data: {response['error']}")
            
    #         if not response['data']:
    #             continue
            
    #         # Convert to DataFrame
    #         df = pd.DataFrame(response['data'])
            
    #         # Convert created_at to datetime
    #         df['created_at'] = pd.to_datetime(df['created_at'])
    #         df.set_index('created_at', inplace=True)
            
    #         # Resample based on frequency
    #         if frequency == 'weekly':
    #             df = df.resample('W').mean()
    #         elif frequency == 'monthly':
    #             df = df.resample('M').mean()
            
    #         result[asset_id] = df
        
    #     return result
    
    # async def get_current_portfolio(
    #     self,
    #     portfolio_id: int,
    #     include_history: bool = False,
    #     history_days: int = 30
    # ) -> Dict[str, Any]:
    #     """
    #     Retrieve the current portfolio composition.
        
    #     Args:
    #         portfolio_id: ID of the portfolio to retrieve
    #         include_history: Whether to include historical allocation data
    #         history_days: Number of days of historical data to include
            
    #     Returns:
    #         Dictionary containing the portfolio information
    #     """
    #     if self.supabase is None:
    #         raise ValueError("Supabase client is not initialized")
        
    #     # Get the latest allocations for the portfolio
    #     query = self.supabase.table('abs_vault_allocation_history') \
    #         .select('*, vault:pool_id(name, address)') \
    #         .eq('pool_id', portfolio_id) \
    #         .order('created_at', ascending=False)
        
    #     response = await query.execute()
        
    #     if 'error' in response:
    #         raise Exception(f"Error retrieving current portfolio: {response['error']}")
        
    #     # Group allocations by allocated_pool_id
    #     allocations = {}
    #     total_value = 0
        
    #     for row in response['data']:
    #         allocated_pool_id = row.get('allocated_pool_id')
            
    #         # Skip if we already have a more recent allocation for this pool
    #         if allocated_pool_id in allocations:
    #             continue
            
    #         allocations[allocated_pool_id] = {
    #             'asset_id': allocated_pool_id,
    #             'value': row.get('amount', 0),
    #             'apy': row.get('apy', 0),
    #             'created_at': row.get('created_at')
    #         }
            
    #         total_value += row.get('amount', 0)
        
    #     # Calculate weights
    #     allocation_list = []
    #     for pool_id, alloc in allocations.items():
    #         weight = alloc['value'] / total_value if total_value > 0 else 0
    #         allocation_list.append({
    #             'asset_id': alloc['asset_id'],
    #             'weight': weight,
    #             'value': alloc['value'],
    #             'apy': alloc['apy']
    #         })
        
    #     # Get historical allocations if requested
    #     historical_allocations = []
    #     if include_history and history_days > 0:
    #         cutoff_date = datetime.now() - timedelta(days=history_days)
            
    #         # Get distinct dates in the history period
    #         date_query = self.supabase.table('abs_vault_allocation_history') \
    #             .select('created_at') \
    #             .eq('pool_id', portfolio_id) \
    #             .gte('created_at', cutoff_date.isoformat()) \
    #             .order('created_at', ascending=True)
            
    #         date_response = await date_query.execute()
            
    #         if 'error' not in date_response:
    #             # Get unique dates
    #             dates = set()
    #             for row in date_response['data']:
    #                 date_str = row.get('created_at', '').split('T')[0]  # Extract date part
    #                 dates.add(date_str)
                
    #             # For each date, get the allocations
    #             for date_str in sorted(dates):
    #                 date_end = f"{date_str}T23:59:59"
                    
    #                 history_query = self.supabase.table('abs_vault_allocation_history') \
    #                     .select('*') \
    #                     .eq('pool_id', portfolio_id) \
    #                     .lte('created_at', date_end) \
    #                     .order('created_at', ascending=False)
                    
    #                 history_response = await history_query.execute()
                    
    #                 if 'error' not in history_response:
    #                     # Group allocations by allocated_pool_id for this date
    #                     date_allocations = {}
    #                     for row in history_response['data']:
    #                         allocated_pool_id = row.get('allocated_pool_id')
                            
    #                         # Skip if we already have a more recent allocation for this pool
    #                         if allocated_pool_id in date_allocations:
    #                             continue
                            
    #                         date_allocations[allocated_pool_id] = row.get('amount', 0)
                        
    #                     historical_allocations.append({
    #                         'date': date_str,
    #                         'allocations': date_allocations
    #                     })
        
    #     # Build the result
    #     result = {
    #         'portfolio_id': portfolio_id,
    #         'total_value': total_value,
    #         'timestamp': datetime.now().isoformat(),
    #         'allocations': allocation_list
    #     }
        
    #     if include_history:
    #         result['historical_allocations'] = historical_allocations
        
    #     return result
    
    # async def _get_pool_id_from_asset_id(self, asset_id: str) -> Optional[int]:
    #     """
    #     Helper method to get pool_id from asset_id.
        
    #     Args:
    #         asset_id: The asset ID to lookup
            
    #     Returns:
    #         The pool_id if found, None otherwise
    #     """
    #     # Try to find the asset in each of the asset tables
    #     tables = ['drift_vault_info', 'yield_pool_info', 'lending_pool_info', 'abs_vault_info']
        
    #     for table in tables:
    #         # Create the query string properly to avoid syntax errors
    #         query = self.supabase.table(table).select('pool_id')
            
    #         # Use the proper or filter syntax
    #         query = query.or(f"address.eq.{asset_id},id.eq.{asset_id}")
            
    #         response = await query.execute()
            
    #         if 'error' not in response and response['data']:
    #             return response['data'][0].get('pool_id')
        
    #     return None
