# Real-Time Monitoring and Automatic Portfolio Optimization

This document outlines how the system monitors new market data and automatically recalculates portfolio optimization in real-time.

## Overview

The real-time monitoring system continuously observes changes in market data stored in Supabase and triggers the recalculation of optimal portfolio weights when significant updates occur. This ensures that portfolio allocations remain optimal even as market conditions change.

## Real-Time Monitoring Process Flow

```
                            REAL-TIME MONITORING PROCESS FLOW
                            ===============================

+---------------+      +----------------+      +------------------+      +---------------+
|               |      |                |      |                  |      |               |
| ETL Server    |----->| New Data       |----->| Supabase Update  |----->| Database      |
| Fetches New   |      | Processing     |      | Operation        |      | Trigger       |
| Market Data   |      |                |      |                  |      | Activation    |
+---------------+      +----------------+      +------------------+      +---------------+
        |                      |                        |                        |
        |                      |                        |                        |
        v                      v                        v                        v
+---------------+      +----------------+      +------------------+      +---------------+
|               |      |                |      |                  |      |               |
| Flask Server  |      | Data Analysis  |      | Significance     |      | Optimization  |
| Event Listener|----->| & Validation   |----->| Check (Threshold |----->| Execution     |
| Receives      |      |                |      | Evaluation)      |      | Decision      |
| Notification  |      |                |      |                  |      |               |
+---------------+      +----------------+      +------------------+      +---------------+
                                                                                |
                                                                                |
                                                                                v
+---------------+      +----------------+      +------------------+      +---------------+
|               |      |                |      |                  |      |               |
| Notify        |<-----| Store Updated  |<-----| Generate         |<-----| Portfolio     |
| Connected     |      | Portfolio      |      | Optimization     |      | Recalculation |
| Clients       |      | State          |      | Results          |      | Using Updated |
|               |      |                |      |                  |      | Data          |
+---------------+      +----------------+      +------------------+      +---------------+
```

## ETL Server Data Update Flow

The ETL (Extract, Transform, Load) server periodically fetches new market data and updates the Supabase database:

1. **Scheduled Data Collection**

   - Fetches latest market data from sources like Yahoo Finance or Alpha Vantage
   - Processes and transforms the data (calculates returns, cleans outliers, etc.)
   - Validates data quality and consistency

2. **Supabase Update**
   - Inserts new data points into the `market_data` table
   - Updates existing records if necessary
   - Triggers database events when new data is inserted

```python
# Example ETL server code for data collection and update
def collect_and_update_market_data():
    # Fetch latest data for monitored assets
    assets = get_monitored_assets()
    today = datetime.now().strftime("%Y-%m-%d")

    for asset in assets:
        # Fetch latest data
        new_data = fetch_data_from_source(asset, today)

        # Process data
        processed_data = process_market_data(new_data)

        # Insert into Supabase
        result = supabase.table('market_data').insert(processed_data).execute()

        # Log update
        if result.data:
            log_data_update(asset, today, "success")
        else:
            log_data_update(asset, today, "failed", result.error)
```

## Automatic Portfolio Recalculation

When new market data is available, the Flask server automatically recalculates optimal portfolio weights:

1. **Event Notification**

   - Supabase triggers a notification when new market data is inserted
   - Flask server listens for these notifications via WebSocket connection
   - Event listeners capture event details (affected assets, timestamp, etc.)

2. **Data Significance Check**

   - System analyzes if the new data is significant enough to warrant recalculation
   - Checks thresholds for price changes, volatility shifts, or correlation changes
   - Determines which portfolios are affected by the data update

3. **Portfolio Optimization Execution**

   - Fetches complete updated dataset for affected assets
   - Applies portfolio optimization algorithms using riskfolio-lib
   - Calculates new optimal weights based on the latest market data

4. **Result Storage and Notification**
   - Stores new portfolio weights in Supabase
   - Logs the recalculation event with timestamp and trigger reason
   - Makes results available through API endpoints

```python
# Example Flask server event listener for data updates
@app.route('/api/webhook/market-data-update', methods=['POST'])
def handle_market_data_update():
    # Extract data from webhook
    data = request.json
    assets_updated = data.get('assets', [])
    update_timestamp = data.get('timestamp')

    # Check significance
    if is_update_significant(assets_updated, update_timestamp):
        # Identify affected portfolios
        affected_portfolios = find_affected_portfolios(assets_updated)

        # Recalculate each affected portfolio
        for portfolio_id in affected_portfolios:
            portfolio_data = get_portfolio_data(portfolio_id)

            # Execute optimization
            new_weights = recalculate_portfolio(portfolio_data, assets_updated)

            # Store updated weights
            store_updated_weights(portfolio_id, new_weights, update_timestamp)

            # Log the recalculation
            log_portfolio_update(portfolio_id, update_timestamp, "data update")

    return jsonify({"status": "processed"})
```

## Supabase Integration

Supabase serves as both the data store and the event trigger mechanism:

1. **Database Triggers**

   - PostgreSQL triggers detect insertions to the `market_data` table
   - Triggers invoke PostgreSQL functions that notify connected clients
   - Notifications are sent via Supabase Realtime

2. **WebSocket Subscriptions**
   - Flask server maintains WebSocket connections to Supabase
   - Subscriptions target specific tables or channels
   - Events are received in real-time when data changes

```sql
-- Example Supabase PostgreSQL trigger function
CREATE OR REPLACE FUNCTION notify_market_data_update()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM pg_notify(
    'market_data_updates',
    json_build_object(
      'asset', NEW.asset_symbol,
      'timestamp', NEW.timestamp,
      'price', NEW.price,
      'operation', TG_OP
    )::text
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger on market_data insert
CREATE TRIGGER market_data_insert_trigger
AFTER INSERT ON market_data
FOR EACH ROW
EXECUTE FUNCTION notify_market_data_update();
```

```python
# Example Flask server Supabase WebSocket subscription
from supabase import create_client, Client

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def subscribe_to_market_data_updates():
    channel = supabase.channel('market_data_updates')

    channel.on(
        'postgres_changes',
        event='INSERT',
        schema='public',
        table='market_data',
        callback=on_market_data_update
    ).subscribe()

def on_market_data_update(payload):
    # Extract data from payload
    asset = payload['new']['asset_symbol']
    timestamp = payload['new']['timestamp']
    price = payload['new']['price']

    # Log reception of update
    logger.info(f"Received market data update for {asset} at {timestamp}: {price}")

    # Trigger portfolio recalculation if needed
    handle_market_data_update(asset, timestamp, price)
```

## Significance Thresholds

To avoid unnecessary recalculations, the system employs thresholds to determine when updates are significant:

1. **Price Change Thresholds**

   - Absolute or percentage change in asset prices
   - Different thresholds for different asset classes (stocks, bonds, etc.)
   - Customizable sensitivity based on user preferences

2. **Volatility Shift Detection**

   - Changes in rolling volatility measurements
   - Detection of volatility regime shifts
   - Sudden spikes in market volatility

3. **Correlation Changes**

   - Shifts in correlation structure between assets
   - Detection of correlation breakdowns during market stress
   - Changes in systemic risk indicators

4. **Time-Based Policies**
   - Minimum time between recalculations
   - Scheduled recalculations (daily, weekly, etc.)
   - Market hours vs. after-hours update policies

```python
# Example significance check function
def is_update_significant(assets_updated, update_timestamp):
    significant = False

    # Get previous data points for comparison
    previous_data = get_previous_data_points(assets_updated)
    current_data = get_current_data_points(assets_updated, update_timestamp)

    # Check price change thresholds
    for asset in assets_updated:
        prev_price = previous_data.get(asset, {}).get('price', 0)
        curr_price = current_data.get(asset, {}).get('price', 0)

        if prev_price > 0:
            pct_change = abs((curr_price - prev_price) / prev_price)

            # Different thresholds for different asset types
            asset_type = get_asset_type(asset)
            threshold = SIGNIFICANCE_THRESHOLDS.get(asset_type, 0.01)

            if pct_change > threshold:
                significant = True
                break

    # Check time-based policies
    if not significant:
        last_calculation = get_last_calculation_time()
        time_diff = update_timestamp - last_calculation

        if time_diff > MIN_RECALCULATION_INTERVAL:
            significant = True

    return significant
```

## Portfolio Recalculation Process

The actual portfolio recalculation process involves:

1. **Data Preparation**

   - Fetching all relevant historical data
   - Calculating returns, covariances, and other statistics
   - Preparing inputs for the optimization engine

2. **Optimization Execution**

   - Executing the riskfolio-lib optimization with current parameters
   - Applying current constraints and objectives
   - Generating optimal portfolio weights

3. **Validation and Filtering**

   - Validating that the new weights make sense
   - Filtering out minor weight changes to reduce turnover
   - Checking for extreme or unexpected allocations

4. **Result Storage**
   - Storing the new weights in Supabase
   - Recording the full optimization parameters and inputs
   - Tracking the optimization history

```python
# Example portfolio recalculation function
def recalculate_portfolio(portfolio_data, assets_updated):
    # Get portfolio parameters
    portfolio_id = portfolio_data['id']
    optimization_params = portfolio_data['optimization_params']
    constraints = portfolio_data['constraints']

    # Fetch historical data for all assets in portfolio
    all_assets = portfolio_data['assets']
    historical_data = get_historical_data(all_assets)

    # Create riskfolio-lib portfolio object
    import riskfolio as rp

    port = rp.Portfolio(returns=historical_data)

    # Set up the portfolio with current parameters
    model = optimization_params.get('model', 'Classic')
    risk_measure = optimization_params.get('risk_measure', 'MV')
    objective = optimization_params.get('objective', 'Sharpe')

    # Calculate asset statistics
    port.assets_stats(method_mu='hist', method_cov='hist')

    # Run optimization
    weights = port.optimization(
        model=model,
        rm=risk_measure,
        obj=objective,
        rf=optimization_params.get('risk_free_rate', 0),
        l=optimization_params.get('risk_aversion', 0),
        hist=True
    )

    # Convert to dictionary format
    weights_dict = weights.to_dict()[0]

    # Validate and filter weights
    filtered_weights = filter_insignificant_weights(weights_dict)

    return filtered_weights
```

## System Configuration

The real-time monitoring system is highly configurable:

1. **Update Frequency**

   - ETL server data collection schedule
   - Minimum time between recalculations
   - Maximum number of recalculations per day

2. **Significance Thresholds**

   - Price change thresholds by asset class
   - Volatility thresholds
   - Correlation change thresholds

3. **Notification Settings**

   - Which events trigger notifications
   - Notification methods (in-app, email, etc.)
   - Urgency levels for different types of updates

4. **Processing Limits**
   - Maximum number of simultaneous recalculations
   - Timeout settings for optimization processes
   - Resource allocation for different optimization tasks

```json
// Example configuration
{
  "etl_server": {
    "market_data_update_schedule": "0 */1 * * 1-5", // Every hour on weekdays
    "data_sources": ["yahoo_finance", "alpha_vantage"],
    "max_historical_days": 1095 // 3 years
  },
  "recalculation": {
    "min_time_between_recalcs": 3600, // 1 hour
    "max_daily_recalcs": 24,
    "significance_thresholds": {
      "stocks": 0.01, // 1% change
      "bonds": 0.005, // 0.5% change
      "forex": 0.008, // 0.8% change
      "crypto": 0.03 // 3% change
    }
  },
  "notifications": {
    "enable_recalculation_notifications": true,
    "notify_on_threshold_breach": true,
    "notify_methods": ["api", "database"]
  },
  "processing": {
    "max_concurrent_recalcs": 5,
    "optimization_timeout": 300, // 5 minutes
    "priority_portfolios": ["portfolio_123", "portfolio_456"]
  }
}
```

## API Endpoints for Real-time Monitoring

The system provides API endpoints to interact with the real-time monitoring system:

### `GET /api/monitor/status`

Returns the current status of the monitoring system.

**Response:**

```json
{
  "status": "active",
  "last_etl_update": "2023-05-01T12:00:00Z",
  "last_recalculation": "2023-05-01T12:15:00Z",
  "monitored_assets": 125,
  "active_portfolios": 15,
  "pending_recalculations": 0
}
```

### `GET /api/monitor/portfolio/:portfolio_id/status`

Returns the monitoring status for a specific portfolio.

**Response:**

```json
{
  "portfolio_id": "portfolio_123",
  "last_update": "2023-05-01T12:15:00Z",
  "update_trigger": "market_data_change",
  "monitored_assets": ["AAPL", "MSFT", "AMZN", "GOOGL", "FB"],
  "significance_thresholds": {
    "price_change": 0.01,
    "volatility_change": 0.2,
    "correlation_change": 0.15
  },
  "recalculation_schedule": {
    "automatic": true,
    "minimum_interval": 3600,
    "scheduled_times": ["09:30", "16:00"]
  }
}
```

### `PUT /api/monitor/portfolio/:portfolio_id/config`

Updates the monitoring configuration for a specific portfolio.

**Request Body:**

```json
{
  "automatic_recalculation": true,
  "significance_thresholds": {
    "price_change": 0.01,
    "volatility_change": 0.2,
    "correlation_change": 0.15
  },
  "minimum_interval": 3600,
  "scheduled_recalculations": ["09:30", "16:00"]
}
```

**Response:**

```json
{
  "status": "updated",
  "portfolio_id": "portfolio_123",
  "config": {
    "automatic_recalculation": true,
    "significance_thresholds": {
      "price_change": 0.01,
      "volatility_change": 0.2,
      "correlation_change": 0.15
    },
    "minimum_interval": 3600,
    "scheduled_recalculations": ["09:30", "16:00"]
  }
}
```

### `POST /api/monitor/portfolio/:portfolio_id/recalculate`

Manually triggers a portfolio recalculation.

**Response:**

```json
{
  "status": "recalculation_queued",
  "portfolio_id": "portfolio_123",
  "request_time": "2023-05-01T13:45:00Z",
  "estimated_completion": "2023-05-01T13:47:00Z",
  "job_id": "recalc_789"
}
```

## Best Practices for Real-time Monitoring

1. **Balance Responsiveness and Stability**

   - Set appropriate thresholds to avoid excessive recalculations
   - Consider market volatility when setting thresholds
   - Implement cooling-off periods after major market events

2. **Ensure Data Quality**

   - Validate all incoming market data
   - Filter out outliers and erroneous data points
   - Maintain data consistency across sources

3. **Optimize Resource Usage**

   - Prioritize portfolio recalculations based on importance
   - Schedule heavy computations during off-peak hours
   - Implement caching strategies for common operations

4. **Implement Failsafes**

   - Set up error handling for all real-time processes
   - Create fallback mechanisms for optimization failures
   - Maintain audit logs of all automated activities

5. **Monitor System Performance**
   - Track response times for recalculations
   - Monitor resource usage during peak activity
   - Set alerts for performance degradation
