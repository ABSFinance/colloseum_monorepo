# Portfolio Optimization Microservice Architecture

## System Architecture Diagram

```
                               PORTFOLIO OPTIMIZATION MICROSERVICE ARCHITECTURE
                               ==============================================

                         +----------------+             +-------------------+
                         |                |             |                   |
                         |   ETL Server   |------------>|     Supabase      |
                         | (Data Pipeline) |             | (Data Storage)    |
                         |                |             |                   |
                         +----------------+             +-------------------+
                                                                |
                                                                |
                                                                v
                                      +----------------------+
                                      |                      |
                                      |    Flask Server      |
                                      | (Portfolio Evaluator)|
                                      |                      |
                                      +----------------------+
                                       /                     \
                                      /                       \
                                     /                         \
                                    /                           \
                                   v                             v
                +-------------------------+   +-------------------------+
                |                         |   |                         |
                |    API Gateway          |   |  Event Listeners        |
                |  (REST Interfaces)      |   | (Data Updates)          |
                |                         |   |                         |
                +-------------------------+   +-------------------------+
                           |                                |
                           |                                |
                           v                                v
                +-------------------------+   +-------------------------+
                |                         |   |                         |
                |   Backtest Service      |   |  Portfolio Service      |
                | (Strategy Testing)      |   | (Weight Calculation)    |
                |                         |   |                         |
                +-------------------------+   +-------------------------+
```

## Microservices Component Diagram

```
                               MICROSERVICES COMPONENT DIAGRAM
                               =============================

  +-------------------+                  +--------------------------------+
  |                   |                  |                                |
  |    ETL Server     |                  |     Flask Server               |
  |  +-----------+    |                  |    +---------------------+     |
  |  | Data      |    |                  |    | Optimization Service|     |
  |  | Collection|    |                  |    | (riskfolio-lib)     |     |
  |  +-----------+    |                  |    +---------------------+     |
  |  | Data      |    |                  |    | Backtest Service    |     |
  |  | Processing|    |                  |    | (Strategy Testing)  |     |
  |  +-----------+    |                  |    +---------------------+     |
  |  | Data      |    |                  |    | API Gateway         |     |
  |  | Storage   |---------------------→ |    | (REST Endpoints)    |     |
  |  +-----------+    |                  |    +---------------------+     |
  |                   |                  |    | Event Listeners     |     |
  +-------------------+                  |    | (Data Updates)      |     |
           |                             |    +---------------------+     |
           |                             |                                |
           |                             +--------------------------------+
           |                                           ↑
           |                                           |
           v                                           |
  +-------------------+                                |
  |                   |                                |
  |     Supabase      |--------------------------------+
  |   +-----------+   |
  |   | Market Data|   |
  |   +-----------+   |
  |   | Portfolio  |   |
  |   | States     |   |
  |   +-----------+   |
  |   | User       |   |
  |   | Settings   |   |
  |   +-----------+   |
  |                   |
  +-------------------+
```

## Data Flow and Process

```
                               DATA FLOW AND COMMUNICATION PROCESS
                               ================================

  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | ETL Server    |----->| Process &      |----->| Store in         |----->| Notify Flask  |
  | Collects Data |      | Transform Data |      | Supabase         |      | Server        |
  |               |      |                |      |                  |      |               |
  +---------------+      +----------------+      +------------------+      +---------------+
                                                                                  |
                                                                                  |
                                                                                  v
  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | Event Listener|----->| Fetch Updated  |----->| Calculate New    |----->| Store Updated |
  | Receives      |      | Data from      |      | Portfolio        |      | Portfolio     |
  | Notification  |      | Supabase       |      | Weights          |      | State         |
  +---------------+      +----------------+      +------------------+      +---------------+
```

## User Request Flow

```
                               USER REQUEST FLOW
                               ================

  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | User Request  |----->| API Gateway    |----->| Route to         |----->| Process       |
  | (Optimization |      | Receives       |      | Appropriate      |      | Request in    |
  | or Backtest)  |      | Request        |      | Service          |      | Service       |
  +---------------+      +----------------+      +------------------+      +---------------+
         |                                                                        |
         |                                                                        |
         v                                                                        v
  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | Fetch Required|----->| Execute        |----->| Store Results    |----->| Return JSON   |
  | Data from     |      | Calculation    |      | in Supabase      |      | Results to    |
  | Supabase      |      | or Simulation  |      | (if needed)      |      | User          |
  +---------------+      +----------------+      +------------------+      +---------------+
```

## Portfolio Optimization Process Flow

```
                               PORTFOLIO REALLOCATION PROCESS FLOW
                               ================================

  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | Fetch Market  |----->| Fetch Current  |----->| Calculate Target |----->| Calculate     |
  | Data & Metrics|      | Portfolio      |      | Portfolio        |      | Required      |
  |               |      |                |      |                  |      | Assets        |
  |               |      |                |      |                  |      |               |
  +---------------+      +----------------+      +------------------+      +---------------+
         |                      |                        |                        |
         |                      |                        |                        |
         v                      v                        v                        v
  +---------------+      +----------------+              |              +------------------+
  |               |      |                |              |              |                  |
  | Market        |      | Current        |              |              | Utilization >    |
  | Metrics       |      | Portfolio      |              |              | Target?          |
  | Analysis      |      | Analysis       |              v              |                  |
  +---------------+      +----------------+      +---------------+      +------------------+
                                                 |               |               |
                                                 | Portfolio     |<---------|No |
                                                 | State         |<---------|Yes|
                                                 | Evaluation    |               |
                                                 +---------------+               |
                                                        |                        |
                                                        |                        |
                                                        v                        v
  +---------------+      +----------------+      +------------------+     +---------------+
  |               |      |                |      |                  |     |               |
  | Create        |<-----| Process        |<-----| RPC: Fetch       |     | No            |
  | Reallocation  |      | Reallocations  |      | Reallocation     |     | Reallocation  |
  | Summary       |      |                |      | Data             |     | Needed        |
  +---------------+      +----------------+      +------------------+     +---------------+
         |                                               |                        |
         |                                               |                        |
         v                                               v                        v
  +---------------+                             +------------------+     +---------------+
  |               |                             |                  |     |               |
  | Output        |                             | Check for        |     | Output        |
  | Reallocation  |                             | Liquidity        |     | Current       |
  | Data          |                             | Availability     |     | Portfolio     |
  |               |                             +------------------+     +---------------+
  +---------------+                                    |                        |
                                                       |                        |
                                                       v                        |
                                              +------------------+              |
                                              |                  |              |
                                              | Output Failed    |              |
                                              | Reallocation     |              |
                                              | Report           |              |
                                              +------------------+              |
                                                       |                        |
                                                       |                        |
                                                       v                        v
                                                      End<-----------------------
```

The portfolio optimization process follows the reallocation flow outlined in `portfolio-reallocation-flow.md`. The process begins with parallel data collection: fetching market data, market metrics, and current portfolio holdings. This information is used to calculate the target portfolio allocation based on current market conditions and investment objectives.

After determining the target allocation, the system calculates the required assets needed to achieve this target and assesses current utilization levels. Utilization represents how efficiently capital is deployed across assets relative to target allocations.

The key decision point is checking whether utilization exceeds target thresholds. If utilization is within acceptable range (typically 95-105%), no reallocation is needed and the current portfolio is maintained. Otherwise, the system proceeds with reallocation by fetching additional data through RPC calls and checking for available liquidity.

When liquidity is sufficient, the system processes reallocations by calculating the necessary trades and simulating their market impact. It then creates a comprehensive reallocation summary detailing the changes, expected performance metrics, and implementation steps.

All paths - successful reallocation, failed reallocation due to liquidity constraints, or no reallocation needed - converge to a single endpoint where the relevant output is provided. This process ensures efficient capital deployment while maintaining portfolio allocations aligned with optimal targets based on current market conditions.

## Backtesting Process Flow

```
                               BACKTESTING PROCESS FLOW
                               ======================

  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | User Defines  |----->| Fetch          |----->| Apply Strategy   |----->| Simulate      |
  | Strategy &    |      | Historical     |      | Parameters &     |      | Transactions  |
  | Parameters    |      | Data           |      | Constraints      |      | Over Time     |
  +---------------+      +----------------+      +------------------+      +---------------+
         |                      |                        |                        |
         |                      |                        |                        |
         v                      v                        v                        v
  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | Period-by-    |      | Portfolio      |      | Risk Analysis    |      | Performance   |
  | Period        |      | Rebalancing    |      | Simulation       |      | Metrics       |
  | Optimization  |      | Simulation     |      |                  |      | Calculation   |
  +---------------+      +----------------+      +------------------+      +---------------+
                                                                                  |
                                                                                  |
                                                                                  v
  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | Generate      |<-----| Store Results  |<-----| Compare with     |<-----| Statistical   |
  | Interactive   |      | in Supabase    |      | Benchmarks       |      | Validation    |
  | Report        |      |                |      |                  |      |               |
  +---------------+      +----------------+      +------------------+      +---------------+
```

## Real-Time Monitoring Process

```
                               REAL-TIME MONITORING PROCESS
                               =========================

  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | ETL Server    |----->| New Data       |----->| Supabase Update  |----->| Event         |
  | Fetches New   |      | Processing     |      | & Storage        |      | Notification  |
  | Market Data   |      |                |      |                  |      |               |
  +---------------+      +----------------+      +------------------+      +---------------+
         |                      |                        |                        |
         |                      |                        |                        |
         v                      v                        v                        v
  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | Flask Server  |      | Portfolio      |      | Update Real-time |      | Check for     |
  | Event Listener|      | Recalculation  |      | Dashboard        |      | Rebalancing   |
  | Activated     |      | (if needed)    |      |                  |      | Needs         |
  +---------------+      +----------------+      +------------------+      +---------------+
                                                                                  |
                                                                                  |
                                                                                  v
  +---------------+      +----------------+      +------------------+      +---------------+
  |               |      |                |      |                  |      |               |
  | Send User     |<-----| Store New      |<-----| Generate         |<-----| Execute       |
  | Notifications |      | Portfolio      |      | Alerts (if       |      | Optimization  |
  | (if needed)   |      | State          |      | thresholds met)  |      | (if needed)   |
  +---------------+      +----------------+      +------------------+      +---------------+
```

## Microservice Responsibilities

### ETL Server

- Scrape financial data from solana network
- Transform and clean data
- Load data into the database
- Schedule regular data updates
- Handle data validation and error correction
- Process raw data into analytics-ready datasets

### Supabase

- Primary data storage for the application
- Real-time database updates
- User authentication and management
- Store structured data in Supabase
- Trigger notifications when new data is available

### Flask Server (Portfolio Evaluator)

- Listen for data update events from Supabase
- Handle user requests via RESTful API for backtest results
- Execute backtesting simulations and provide JSON results to users
- Evaluate and optimize portfolio compositions using riskfolio-lib
- Calculate optimal portfolio weights based on various strategies
- Provide API endpoints for client applications
- Recalculate portfolio optimization when new data arrives
- No visualization or UI components - focused on portfolio evaluation and optimization

## Request-Response Patterns

### Portfolio Optimization Request

1. User sends optimization request with parameters
2. API Gateway routes request to Optimization Service
3. Service fetches required data from Supabase
4. riskfolio-lib executes optimization calculations
5. Results are stored in Supabase and returned as JSON

### Backtesting Request

1. User sends backtesting request with strategy parameters
2. API Gateway routes request to Backtesting Service
3. Service retrieves historical data from Supabase
4. Simulation engine runs strategy over specified period
5. Performance metrics are calculated
6. Results are stored and returned as JSON

### Automatic Recalculation on Data Updates

1. ETL Server updates market data in Supabase
2. Supabase triggers notification to Flask Server
3. Event Listener activates Portfolio Service
4. Portfolio weights are recalculated automatically
5. New optimal weights are stored in Supabase for client retrieval

## Technology Implementation

### ETL Server

- Python-based ETL pipeline
- Scheduled jobs with APScheduler or Airflow
- Data processing with pandas and numpy
- API clients for data sources

### Flask Server

- Flask/FastAPI web framework
- riskfolio-lib for portfolio optimization
- RESTful API endpoints
- No UI components - JSON responses only
- WebSocket connections for real-time data event listening

### Supabase Integration

- PostgreSQL database for structured data
- Real-time subscriptions for updates
- Row-level security for data access control
- Authentication and authorization

## Implementation Phases

1. **Phase 1: Core Infrastructure**

   - Set up ETL Server and Supabase integration
   - Implement data collection and storage pipeline
   - Create basic Flask Server with API endpoints

2. **Phase 2: Optimization Services**

   - Implement portfolio optimization service
   - Connect to Supabase for data retrieval
   - Create API endpoints for optimization requests

3. **Phase 3: Backtesting Service**

   - Develop backtesting simulation engine
   - Implement strategy testing algorithms
   - Create performance analysis tools

4. **Phase 4: Automatic Recalculation**

   - Implement event listeners for data updates
   - Create automatic portfolio optimization triggers
   - Set up notification system for updates

5. **Phase 5: Advanced Features**
   - Implement advanced optimization models
   - Add machine learning capabilities
   - Enhance real-time processing
