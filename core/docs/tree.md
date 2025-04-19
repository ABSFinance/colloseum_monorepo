# Portfolio Optimization Microservice Repository Structure

```
portfolio-optimization-microservice/
├── README.md                           # Project overview and setup instructions
├── .gitignore                          # Git ignore file
├── .env.example                        # Example environment variables
├── docker-compose.yml                  # Docker Compose configuration
│
├── etl_server/                         # ETL Server (Data Pipeline)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py                   # ETL configuration settings
│   │   ├── collectors/                 # Data collection modules
│   │   │   ├── __init__.py
│   │   │   ├── market_data_collector.py
│   │   │   └── solana_collector.py     # Solana blockchain data collector
│   │   ├── processors/                 # Data processing modules
│   │   │   ├── __init__.py
│   │   │   ├── data_cleaner.py
│   │   │   └── data_transformer.py
│   │   ├── storage/                    # Data storage handlers
│   │   │   ├── __init__.py
│   │   │   └── supabase_client.py
│   │   └── jobs/                       # Scheduled jobs
│   │       ├── __init__.py
│   │       ├── scheduler.py
│   │       └── job_definitions.py
│   ├── tests/                          # ETL Server tests
│   │   ├── __init__.py
│   │   ├── test_collectors/
│   │   ├── test_processors/
│   │   └── test_storage/
│   ├── requirements.txt                # ETL Server dependencies
│   ├── Dockerfile                      # ETL Server Docker configuration
│   └── run.py                          # ETL Server entry point
│
├── flask_server/                       # Flask Server (Portfolio Evaluator)
│   ├── src/
│   │   ├── __init__.py
│   │   ├── config.py                   # Server configuration
│   │   ├── api/                        # API Gateway
│   │   │   ├── __init__.py
│   │   │   ├── routes.py               # API route definitions
│   │   │   ├── middleware.py           # API middleware
│   │   │   └── validators.py           # Request validators
│   │   ├── portfolio/                  # Portfolio Service
│   │   │   ├── __init__.py
│   │   │   ├── optimizer.py            # Portfolio optimization logic
│   │   │   ├── models.py               # Portfolio data models
│   │   │   └── strategies.py           # Optimization strategies
│   │   ├── backtest/                   # Backtest Service
│   │   │   ├── __init__.py
│   │   │   ├── simulator.py            # Backtest simulation engine
│   │   │   ├── analysis.py             # Performance analysis
│   │   │   └── metrics.py              # Performance metrics
│   │   ├── events/                     # Event Listeners
│   │   │   ├── __init__.py
│   │   │   ├── listeners.py            # Event subscription handlers
│   │   │   └── processors.py           # Event processing logic
│   │   ├── storage/                    # Storage interfaces
│   │   │   ├── __init__.py
│   │   │   └── supabase_client.py      # Supabase client implementation
│   │   └── utils/                      # Utility functions
│   │       ├── __init__.py
│   │       ├── validators.py           # Data validation utilities
│   │       └── helpers.py              # Helper functions
│   ├── tests/                          # Flask Server tests
│   │   ├── __init__.py
│   │   ├── test_api/
│   │   ├── test_portfolio/
│   │   ├── test_backtest/
│   │   └── test_events/
│   ├── requirements.txt                # Flask Server dependencies
│   ├── Dockerfile                      # Flask Server Docker configuration
│   └── run.py                          # Flask Server entry point
│
├── shared/                             # Shared code between services
│   ├── __init__.py
│   ├── models/                         # Shared data models
│   │   ├── __init__.py
│   │   ├── market_data.py
│   │   └── portfolio.py
│   ├── utils/                          # Shared utilities
│   │   ├── __init__.py
│   │   ├── supabase.py                 # Supabase utilities
│   │   └── validators.py               # Common validation
│   └── constants.py                    # Shared constants
│
├── supabase/                           # Supabase configuration
│   ├── migrations/                     # Database migrations
│   │   ├── 00001_initial_schema.sql
│   │   └── 00002_add_indexes.sql
│   ├── triggers/                       # Database triggers
│   │   ├── notify_market_data_update.sql
│   │   └── notify_portfolio_update.sql
│   ├── functions/                      # Database functions
│   │   ├── calculate_portfolio_statistics.sql
│   │   └── get_historical_data.sql
│   └── schema.sql                      # Database schema
│
├── docs/                               # Documentation
│   ├── api.md                          # API documentation
│   ├── backtesting.md                  # Backtesting guide
│   ├── dashboard.md                    # Dashboard guide (future)
│   ├── real-time-monitoring.md         # Real-time monitoring documentation
│   ├── project-architecture.md         # Project architecture overview
│   └── development/                    # Development documentation
│       ├── setup.md                    # Development environment setup
│       ├── testing.md                  # Testing guidelines
│       └── deployment.md               # Deployment instructions
│
├── scripts/                            # Utility scripts
│   ├── setup.sh                        # Project setup script
│   ├── seed_data.py                    # Development data seeding
│   └── deploy.sh                       # Deployment script
│
└── notebooks/                          # Jupyter notebooks for development/research
    ├── optimization_research.ipynb
    ├── backtest_analysis.ipynb
    └── data_exploration.ipynb
```

## Repository Components

### ETL Server

The ETL Server is responsible for collecting, processing, and storing market data. It handles:

- Data collection from various sources
- Data processing and transformation
- Storage of processed data in Supabase
- Scheduled jobs and pipeline management

### Flask Server

The Flask Server is the core portfolio evaluation service that provides:

- RESTful API endpoints via the API Gateway
- Portfolio optimization with riskfolio-lib
- Backtesting services for strategy evaluation
- Event listeners for real-time data updates
- No UI components - focused on backend processing and JSON responses

### Shared Components

Shared code between the ETL Server and Flask Server, including:

- Common data models
- Utility functions
- Constants and configuration
- Supabase integration utilities

### Supabase Configuration

Configuration for Supabase, the primary data storage:

- Database schema
- Migrations for version control
- Triggers for real-time event notifications
- Custom functions for complex operations

### Documentation

Comprehensive documentation for the project:

- API reference
- Architecture overview
- Guides for backtesting and monitoring
- Development guidelines

### Utility Scripts and Notebooks

Supporting files for development, research, and deployment:

- Setup and deployment scripts
- Data seeding utilities
- Research notebooks

```

```
