# Backtesting Guide

This document outlines the backtesting capabilities of the Portfolio Optimization System, which allows users to test investment strategies against historical data.

## Overview

Backtesting is a methodology for evaluating investment strategies by applying them to historical market data. The system provides a robust backtesting engine that simulates how different portfolio optimization strategies would have performed in the past, offering insights for future investment decisions.

## Backtesting Process Flow

```
                               BACKTESTING PROCESS FLOW
                               ======================

  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | User Request  |----->| Fetch          |----->| Apply Strategy   |----->| Simulate      |
  | via API       |      | Historical     |      | Parameters &     |      | Transactions  |
  |               |      | Data           |      | Constraints      |      | Over Time     |
  +---------------+      +----------------+      +------------------+      +---------------+
         |                      |                        |                        |
         |                      |                        |                        |
         v                      v                        v                        v
  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | Period-by-    |      | Portfolio      |      | Risk Analysis    |      | Performance   |
  | Period        |      | Rebalancing    |      | & Drawdowns      |      | Metrics       |
  | Optimization  |      | Simulation     |      |                  |      | Calculation   |
  +---------------+      +----------------+      +------------------+      +---------------+
                                                                                  |
                                                                                  |
                                                                                  v
  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | Generate      |<-----| Store Results  |<-----| Compare with     |<-----| Statistical   |
  | JSON Results  |      | in Supabase    |      | Benchmarks       |      | Validation    |
  |               |      |                |      |                  |      |               |
  +---------------+      +----------------+      +------------------+      +---------------+
```

## Backtesting API

The backtesting functionality is accessible through the API:

### `POST /api/backtest/run`

Executes a backtest simulation based on specified strategy and parameters.

**Request Body:**

```json
{
  "strategy": {
    "type": "optimization", // "optimization", "fixed_weights", "rebalancing"
    "parameters": {
      "model": "Classic", // "Classic", "BL", "FM"
      "risk_measure": "MV", // "MV", "MAD", "CVaR", etc.
      "objective": "Sharpe" // "MinRisk", "MaxRet", "Sharpe", "Utility"
    },
    "rebalancing_frequency": "monthly", // "daily", "weekly", "monthly", "quarterly"
    "transaction_costs": 0.001 // Percentage as decimal
  },
  "assets": ["AAPL", "MSFT", "AMZN", "GOOGL", "FB"],
  "start_date": "2018-01-01",
  "end_date": "2023-01-01",
  "initial_capital": 100000,
  "benchmark": "SPY", // Optional benchmark ticker
  "constraints": {
    "lower_bound": 0.0,
    "upper_bound": 0.3,
    "groups": {
      "Tech": ["AAPL", "MSFT", "GOOGL"],
      "Retail": ["AMZN"]
    },
    "group_constraints": {
      "Tech": { "min": 0.2, "max": 0.6 },
      "Retail": { "min": 0.1, "max": 0.4 }
    }
  }
}
```

**Response:**

```json
{
  "backtest_id": "67890xyz",
  "status": "completed",
  "summary": {
    "initial_capital": 100000,
    "final_value": 145000,
    "total_return": 0.45,
    "annualized_return": 0.12,
    "volatility": 0.18,
    "sharpe_ratio": 0.67,
    "sortino_ratio": 0.95,
    "max_drawdown": 0.25,
    "calmar_ratio": 0.48,
    "beta": 0.85,
    "alpha": 0.03,
    "tracking_error": 0.05,
    "information_ratio": 0.6
  },
  "time_series": {
    "dates": ["2018-01-01", "2018-01-02", ...],
    "portfolio_values": [100000, 100500, ...],
    "returns": [0, 0.005, ...],
    "drawdowns": [0, 0, ...],
    "benchmark_values": [10000, 10020, ...],
    "benchmark_returns": [0, 0.002, ...]
  },
  "transactions": [
    {
      "date": "2018-01-01",
      "asset": "AAPL",
      "action": "buy",
      "quantity": 100,
      "price": 150.25,
      "cost": 15025,
      "weight": 0.15
    }
  ],
  "period_allocations": [
    {
      "date": "2018-01-01",
      "weights": {
        "AAPL": 0.15,
        "MSFT": 0.20,
        "AMZN": 0.25,
        "GOOGL": 0.22,
        "FB": 0.18
      }
    }
  ]
}
```

### `GET /api/backtest/:backtest_id`

Retrieves the results of a previously executed backtest.

## Backtesting Strategies

The system supports multiple backtesting strategies:

### 1. Optimization Strategy

Applies the portfolio optimization algorithm at each rebalancing period.

### 2. Fixed Weights Strategy

Maintains fixed asset weights, rebalancing at specified intervals.

### 3. Rebalancing Strategy

Starts with an initial optimization and rebalances when asset weights drift beyond specified thresholds.

## Performance Evaluation

The backtesting engine calculates various performance metrics to evaluate strategy effectiveness:

### Time Series Metrics

- **Portfolio Value**: Daily portfolio value over time
- **Returns**: Daily, monthly, and annual returns
- **Drawdowns**: Drawdown magnitude and duration
- **Alpha/Beta**: Excess return and market correlation over time

### Summary Statistics

- **Total Return**: Overall return over the entire backtest period
- **Annualized Return**: Return normalized to annual rate
- **Volatility**: Standard deviation of returns
- **Sharpe Ratio**: Risk-adjusted return using standard deviation
- **Sortino Ratio**: Risk-adjusted return using downside deviation
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Calmar Ratio**: Return relative to maximum drawdown
- **Value at Risk (VaR)**: Potential loss at a given confidence level
- **Conditional Value at Risk (CVaR)**: Expected loss beyond VaR
- **Tracking Error**: Standard deviation of excess returns vs benchmark
- **Information Ratio**: Excess return per unit of tracking risk

## Backtesting Configuration

The backtesting engine can be configured with various parameters:

### Time Period Parameters

- **Start Date**: Beginning of the backtest period
- **End Date**: End of the backtest period
- **Rebalancing Frequency**: How often the portfolio is rebalanced

### Strategy Parameters

- **Optimization Model**: Classic, Black-Litterman, or Factor Model
- **Risk Measure**: MV, MAD, CVaR, etc.
- **Objective Function**: MinRisk, MaxRet, Sharpe, Utility
- **Constraints**: Asset weight bounds, group constraints, etc.

### Transaction Parameters

- **Initial Capital**: Starting investment amount
- **Transaction Costs**: Percentage cost for each trade
- **Tax Considerations**: Impact of taxes on returns (optional)

## Implementation Details

The backtesting engine is implemented using the following technologies:

### Core Components

- **Historical Data Service**: Retrieves and prepares historical market data
- **Optimization Engine**: Leverages riskfolio-lib for portfolio optimization
- **Transaction Simulator**: Simulates trades based on rebalancing decisions
- **Performance Calculator**: Computes performance metrics and statistics

### Integration Points

- **Supabase**: Stores backtest results and historical data
- **API Layer**: Processes user requests and returns backtest results

## Best Practices for Backtesting

### Avoiding Backtest Overfitting

- **Walk-Forward Analysis**: Test strategy on unseen data
- **Cross-Validation**: Split data into multiple periods for testing
- **Parameter Sensitivity**: Analyze sensitivity to parameter changes

### Accounting for Market Frictions

- **Transaction Costs**: Include realistic trading costs
- **Slippage**: Consider price impact of trades
- **Liquidity Constraints**: Factor in asset liquidity
- **Market Impact**: Account for large order impacts

### Realistic Assumptions

- **Point-in-Time Data**: Use only data available at time of decision
- **Dividends and Corporate Actions**: Account for all return components
- **Realistic Rebalancing**: Consider practical rebalancing constraints
- **Risk Management Rules**: Implement realistic risk controls
