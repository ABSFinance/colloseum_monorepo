# Flask Server Structure

This document outlines the structure and organization of the Flask Server component of the Portfolio Optimization Microservice.

## Overview

The Flask Server serves as the Portfolio Evaluator in the system architecture, handling portfolio optimization, backtesting, reallocation, API requests, and event processing. It's designed as a microservice with no UI components, focusing entirely on backend processing and providing JSON responses.

## Directory Structure

```
abs_finance/
├── src/
│   ├── __init__.py                 # Flask app initialization
│   ├── config.py                   # Configuration settings
│   ├── api/                        # API endpoints
│   │   ├── __init__.py
│   │   ├── routes.py               # API route definitions
│   │   ├── portfolio_routes.py     # Portfolio-specific endpoints
│   │   ├── backtest_routes.py      # Backtest-specific endpoints
│   │   └── market_data_routes.py   # Market data endpoints
│   ├── models/                     # Data models
│   │   ├── __init__.py
│   │   ├── portfolio.py            # Portfolio data models
│   │   ├── backtest.py             # Backtest data models
│   │   └── market_data.py          # Market data models
│   ├── services/                   # Business logic
│   │   ├── __init__.py
│   │   ├── portfolio_service.py    # Portfolio optimization service
│   │   ├── backtest_service.py     # Backtesting service
│   │   ├── market_data_service.py  # Market data service
│   │   └── reallocation_service.py # Portfolio reallocation service
│   ├── core/                       # Core components
│   │   ├── __init__.py
│   │   ├── optimizer.py            # Portfolio optimization using Riskfolio-Lib
│   │   ├── risk_models.py          # Risk modeling and calculations
│   │   ├── reallocation.py         # Portfolio reallocation logic
│   │   └── constraints.py          # Portfolio constraints logic
│   ├── backtest/                   # Backtesting components
│   │   ├── __init__.py
│   │   ├── simulator.py            # Backtest simulation engine
│   │   ├── metrics.py              # Performance metrics calculation
│   │   ├── strategies.py           # Strategy implementations
│   │   ├── rebalancing.py          # Rebalancing strategy implementations
│   │   ├── analysis.py             # Performance analysis
│   │   └── visualization.py        # Result visualization
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── helpers.py              # General helper functions
│       ├── date_utils.py           # Date manipulation utilities
│       └── validators.py           # Input validation functions
├── data/                           # Data storage
│   ├── market_data/                # Market price data
│   ├── portfolio_results/          # Portfolio optimization results
│   └── backtest_results/           # Backtest result data
├── docs/                           # Documentation
│   ├── api.md                      # API documentation
│   ├── optimization.md             # Optimization guide
│   ├── backtesting.md              # Backtesting guide
│   └── architecture.md             # System architecture documentation
├── tests/                          # Test files
│   ├── __init__.py
│   ├── test_api/                   # API tests
│   ├── test_services/              # Service tests
│   ├── test_core/                  # Core component tests
│   ├── test_backtest/              # Backtest component tests
│   │   ├── test_simulator.py       # Tests for simulation engine
│   │   └── test_metrics.py         # Tests for performance metrics
│   ├── example_risk_calculation.py # Example risk calculation script
│   ├── example_reallocation.py     # Example reallocation script
│   └── run_tests.py                # Test runner
├── .env.example                    # Example environment variables
├── .gitignore                      # Git ignore file
├── requirements.txt                # Project dependencies
├── setup.py                        # Package setup
└── run.py                          # Application entry point
```

## Component Details

### API Gateway

The API Gateway handles all external communication via RESTful interfaces. It processes incoming requests, routes them to the appropriate services, and formats responses.

Key files:

- `routes.py`: Defines all API endpoints and their handlers
- `portfolio_routes.py`: Endpoints for portfolio-specific operations
- `backtest_routes.py`: Endpoints for backtest-specific operations
- `market_data_routes.py`: Endpoints for market data operations

### Portfolio Service

The Portfolio Service performs portfolio optimization calculations using riskfolio-lib. It implements various optimization strategies, risk models, and reallocation logic.

Key files:

- `optimizer.py`: Core optimization algorithms
- `portfolio.py`: Data models for portfolio configurations
- `constraints.py`: Portfolio constraint definitions
- `risk_models.py`: Risk measurement and management models
- `reallocation.py`: Portfolio reallocation algorithms and utilization analysis
- `portfolio_service.py`: Business logic for portfolio operations

### Risk Models

The Risk Models component provides comprehensive risk assessment capabilities:

- Two main classes: `RiskAnalyzer` and `RiskModel`
- Calculation of covariance matrices using various methods (sample, EWMA)
- Portfolio volatility calculation with optional annualization
- Value at Risk (VaR) calculation using historical or parametric methods
- Conditional Value at Risk (CVaR) analysis
- Drawdown tracking and maximum drawdown identification
- Correlation matrix generation
- Beta calculation against benchmarks
- Tracking error measurement
- Risk contribution analysis

### Reallocation Component

The Reallocation component manages portfolio adjustments based on market conditions:

- Asset utilization analysis (comparing current vs. target allocations)
- Liquidity assessment for potential trades
- Reallocation plan generation with transaction cost optimization
- Market impact simulation for planned transactions
- Reallocation summary creation with detailed metrics
- Integration with RPC services for advanced reallocation strategies

### Backtest Service

The Backtest Service simulates trading strategies against historical data to evaluate performance.

Key files:

- `simulator.py`: Backtesting simulation engine
- `metrics.py`: Performance metric calculations
- `strategies.py`: Strategy implementations for backtesting
- `rebalancing.py`: Portfolio rebalancing algorithms
- `analysis.py`: Performance analysis tools
- `visualization.py`: JSON data structures for visualization

### Event Listeners

The Event Listeners component responds to real-time data updates from Supabase and triggers appropriate actions.

Key files:

- `listeners.py`: Event subscription handlers
- `processors.py`: Event processing logic
- `notifications.py`: Notification generation for important events
- `websocket.py`: WebSocket connection management

### Storage

The Storage component provides interfaces for data persistence and retrieval using Supabase.

Key files:

- `supabase_client.py`: Supabase client implementation
- `market_data_repo.py`: Repository for market data
- `portfolio_repo.py`: Repository for portfolio data
- `backtest_repo.py`: Repository for backtest results
- `reallocation_repo.py`: Repository for reallocation data and history

### Utilities

Utility functions and helpers used throughout the application.

Key files:

- `validators.py`: Data validation utilities
- `helpers.py`: General helper functions
- `logging.py`: Logging configuration
- `security.py`: Security-related utilities
- `strategies.py`: Common strategy implementations
- `date_utils.py`: Date handling utilities

## Process Flows

### Reallocation Flow

The reallocation process follows these steps:

1. **Initial Data Collection (Parallel)**

   - Fetch market metrics from API
   - Fetch current market data
   - Fetch current portfolio composition

2. **Target Portfolio Calculation**

   - Calculate optimal target portfolio based on collected data
   - Apply investment objectives and constraints

3. **Required Assets Calculation**

   - Calculate required assets to achieve target portfolio
   - Assess current vs. required asset levels

4. **Utilization Assessment**

   - Check if asset utilization exceeds target thresholds
   - Determine if reallocation is needed based on utilization metrics

5. **Liquidity Assessment**

   - For high utilization scenarios, fetch reallocation data via RPC
   - Verify sufficient liquidity for reallocation
   - Simulate market impact of planned transactions

6. **Reallocation Plan Generation**

   - Process reallocations if liquidity is available
   - Calculate any liquidity shortfalls
   - Create comprehensive reallocation summary

7. **Output Generation**
   - Output reallocation data if changes are needed
   - Output current portfolio if no reallocation is needed
   - Output failed reallocation report if liquidity is insufficient

### Backtesting Flow

The backtesting process includes:

1. **User Request Handling**

   - Process user request for backtesting via API
   - Validate parameters and constraints

2. **Historical Data Retrieval**

   - Fetch historical market data for specified assets and time period

3. **Strategy Application**

   - Apply specified strategy parameters and constraints
   - Simulate transactions over the specified time period

4. **Performance Analysis**

   - Calculate performance metrics (returns, volatility, drawdowns, etc.)
   - Compare results with benchmarks
   - Generate statistical validation

5. **Result Generation**
   - Store results in Supabase
   - Generate JSON response with detailed performance data

## Communication Flow

1. External requests enter through the API Gateway
2. Requests are validated and routed to the appropriate service
3. Services process requests, often retrieving data from Supabase
4. Results are stored in Supabase and returned via the API
5. Event Listeners continuously monitor for data updates
6. When new data is available, Event Listeners trigger recalculations

## Deployment Considerations

The Flask Server is containerized using Docker for easy deployment and scaling:

- `Dockerfile`: Defines the container image
- `requirements.txt`: Lists all production dependencies
- `requirements-dev.txt`: Additional development dependencies
- `docker-compose.yml`: Local development environment configuration
- `run.py`: Entry point for the application

```

```
