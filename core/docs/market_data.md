# Market Data Service

This document outlines the market data service that provides core data required for portfolio optimization, reallocation, and backtesting.

## Overview

The Market Data Service is responsible for retrieving, processing, and providing the following types of data:

1. **Market Metrics**: Investment pool information from `drift_vault_info`, `yield_pool_info`, `lending_pool_info`, and `abs_vault_info`
2. **Market Data**: Historical performance data from `performance_history`
3. **Current Portfolio**: Current allocations from `abs_vault_allocation_history`

This service is a critical component in the portfolio reallocation flow, providing the foundational data needed for making investment decisions.

## Data Sources and Structure

### 1. Market Metrics

Market metrics provide essential information about investment pools across different types:

#### Data Sources

- `drift_vault_info`: Information about Drift Protocol Vaults
- `yield_pool_info`: General yield pool information
- `lending_pool_info`: Lending pool data
- `abs_vault_info`: ABS Vault data

#### Data Structure

```json
{
  "market_metrics": {
    "drift_vault_info": [
      {
        "id": 123,
        "name": "Solana Drift Strategy A",
        "address": "0x123...",
        "pool_id": 123,
        "org_id": 123,
        "underlying_token": "0x123...",
        "capacity": 1000000,
        "market_tokens": ["0x123...", "0x123...", "0x123..."],
        "strategy": "JLP Delta Neutral",
        "description": "A drift vault strategy that uses a JLP Delta Neutral strategy to optimize returns"
      }
    ],
    "yield_pool_info": [
      {
        "id": "1inch-network-1inch",
        "name": "1inch",
        "address": "0x456...",
        "pool_id": 456,
        "org_id": 456,
        "chain": "solana",
        "protocol": "1inch",
        "underlying_tokens": ["0x123...", "0x123..."],
        "description": "A yield pool that uses a 1inch strategy to optimize returns"
      }
    ],
    "lending_pool_info": [
      {
        "id": "lending_pool_789",
        "name": "SOL Lending Pool",
        "address": "0x789...",
        "pool_id": 789,
        "org_id": 789,
        "underlying_token": "0x789...",
        "collateral_factor": 0.78,
        "ltv_ratio": 0.032,
        "liquidity_threshold": 0.055,
        "supply_cap": 0.5,
        "borrow_cap": 0.5,
        "description": "A lending pool that uses a Marinade strategy to optimize returns"
      }
    ],
    "abs_vault_info": [
      {
        "id": "abs_vault_101",
        "name": "Diversified ABS Strategy",
        "address": "0x101...",
        "pool_id": 101,
        "org_id": 101,
        "underlying_token": "0x101...",
        "capacity": 1000000,
        "adaptors": ["kamino-lend", "drift-vault"],
        "allowed_pools": ["1105", "1106", "1107"],
        "description": "A diversified ABS strategy that uses a Marinade strategy to optimize returns"
      }
    ]
  }
}
```

### 2. Market Data (Performance History)

Historical performance data for all investment pools, providing time-series data essential for analysis and backtesting.

#### Data Source

- `performance_history`: Time-series performance data for all pools

#### Data Structure

```json
[
  {
    "id": 1,
    "pool_id": 123,
    "tvl": 123,
    "apy": 0.079,
    "volumn": 0.0083,
    "max_drawdown": 0.22,
    "risk_adjusted_return": 0.22,
    "created_at": "2023-01-01"
  }
]
```

### 3. Current Portfolio (Allocation History)

Current portfolio allocations and their historical changes, essential for calculating required assets and utilization metrics.

#### Data Source

- `abs_vault_allocation_history`: Time-series data showing how allocations have changed

#### Data Structure

```json
[
  {
    "id": 1,
    "pool_id": 123,
    "allocated_pool_id": 123,
    "allocated_percentage": 0.5,
    "amount": 123,
    "apy": 0.079,
    "earnings": 123,
    "created_at": "2023-01-01"
  }
]
```

## Role in Portfolio Reallocation Flow

As shown in the portfolio reallocation flowchart, the Market Data Service plays a crucial role in the parallel initial data collection phase:

```
Start
  |
  v
Parallel
  |
  |------> API: Fetch Market Metrics
  |
  |------> Fetch Market Data
  |
  |------> Fetch Current Portfolio
  |
  v
Calculate Target Portfolio
  |
  v
Calculate Required Assets
  |
  v
... (rest of the reallocation flow)
```

### Data Flow in Reallocation Process

1. **Initial Data Collection (Parallel)**

   - **API: Fetch Market Metrics**: Retrieve current market indicators from `drift_vault_info`, `yield_pool_info`, `lending_pool_info`, and `abs_vault_info`
   - **Fetch Market Data**: Obtain historical performance data from `performance_history`
   - **Fetch Current Portfolio**: Get current portfolio composition from `abs_vault_allocation_history`

2. **Target Portfolio Calculation**

   - Uses the collected market metrics, market data, and current portfolio to calculate an optimal target portfolio

3. **Required Assets Calculation**
   - Calculates the required assets needed to achieve the target portfolio
   - Compares current portfolio holdings with target allocations
   - Determines utilization metrics for each asset

## Data Retrieval Methods

The Market Data Service provides several methods for retrieving the necessary data:

### 1. Get Market Metrics

Retrieves current market metrics for specified assets or asset types.

**Parameters:**

- `asset_ids` (optional): List of specific asset IDs to retrieve
- `asset_types` (optional): List of asset types (drift_vault, yield_pool, lending_pool, abs_vault)

### 2. Get Market Data (Historical Performance)

Retrieves historical performance data for specified assets over a time period.

**Parameters:**

- `asset_ids`: List of asset IDs to retrieve data for
- `start_date`: Beginning of the time period
- `end_date`: End of the time period

### 3. Get Current Portfolio

Retrieves the current portfolio composition.

**Parameters:**

- `portfolio_id`: ID of the portfolio to retrieve

## Integration with Optimization Process

The Market Data Service integrates with the portfolio optimization process by:

1. **Providing Input Data**: Supplying the necessary data for the optimization algorithm
2. **Calculating Correlation Matrices**: Generating correlation matrices from historical returns
3. **Risk Metrics Calculation**: Computing volatility, Value at Risk (VaR), and other risk metrics
4. **Performance Benchmarking**: Providing benchmark data for performance comparison

## Implementation Considerations

### 1. Data Freshness

Market data should be updated at appropriate intervals:

- Real-time updates for critical price data
- Daily updates for most performance metrics
- Weekly updates for longer-term statistics

### 2. Caching Strategy

To improve performance:

- Cache frequently accessed market metrics
- Implement time-based cache invalidation
- Layer caching (memory, disk, database)

### 3. Error Handling

Robust error handling for:

- Missing data points
- Stale data detection
- Data quality validation
- Fallback data sources

### 4. Performance Optimization

Techniques for optimizing data retrieval:

- Batch requests for multiple assets
- Parallel data fetching
- Precomputed aggregations for common queries
- Data compression for historical time series

## Data Schema Relationships

The market data service leverages the relationships defined in the database schema:

1. **Central Registry Approach**: All investment types (vaults, yield pools, lending pools) are registered in the central `pool_info` table with their type.

2. **Performance Tracking**: The `performance_history` table references the pool_id, enabling consistent historical data tracking across all investment types.

3. **Token Relationships**: Each investment type has underlying tokens, allowing for tracking exposure across different investment vehicles.

4. **Allocation History**: The `abs_vault_allocation_history` tracks how capital has been allocated across different investment options over time.

## Conclusion

The Market Data Service is a foundational component of the Portfolio Optimization System, providing the essential data needed for making informed investment decisions. By efficiently retrieving and processing data from multiple sources, it enables the system to calculate optimal portfolio allocations, assess utilization, and determine when reallocation is necessary.
