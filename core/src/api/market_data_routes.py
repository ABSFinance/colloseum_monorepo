#!/usr/bin/env python3
"""
Market Data API Routes.

This module defines the API routes for retrieving and processing market data 
for the Portfolio Optimization System.
"""

from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import pandas as pd
from typing import List, Dict, Any, Optional, Union
import traceback

# Create blueprint for market data routes
market_data_bp = Blueprint('market_data', __name__, url_prefix='/api/data/market')


def parse_comma_separated(param: Optional[str]) -> List[str]:
    """Parse comma-separated string into a list of strings."""
    if not param:
        return []
    return [item.strip() for item in param.split(',')]


def validate_date_format(date_str: str) -> bool:
    """Validate that a string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


@market_data_bp.route('', methods=['GET'])
def get_market_data():
    """
    Get historical market data for specified assets and time period.
    
    Query Parameters:
    - assets: Comma-separated list of asset symbols
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - frequency: Data frequency (daily, weekly, monthly)
    - fields: Comma-separated list of data fields to include
    """
    try:
        # Extract and validate query parameters
        assets = request.args.get('assets')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        frequency = request.args.get('frequency', 'daily')
        fields = request.args.get('fields')
        
        # Validate required parameters
        if not assets:
            return jsonify({'error': 'Missing required parameter: assets'}), 400
        
        if not start_date or not validate_date_format(start_date):
            return jsonify({'error': 'Invalid or missing start_date parameter (YYYY-MM-DD format required)'}), 400
        
        if not end_date or not validate_date_format(end_date):
            return jsonify({'error': 'Invalid or missing end_date parameter (YYYY-MM-DD format required)'}), 400
        
        # Parse comma-separated parameters
        asset_list = parse_comma_separated(assets)
        field_list = parse_comma_separated(fields)
        
        # Validate frequency
        valid_frequencies = ['daily', 'weekly', 'monthly']
        if frequency not in valid_frequencies:
            return jsonify({
                'error': f'Invalid frequency parameter. Must be one of: {", ".join(valid_frequencies)}'
            }), 400
        
        # Here we would call the market data service to retrieve the actual data
        # For now, we'll return a placeholder response
        
        # In a real implementation, you would do something like:
        # market_data = current_app.market_data_service.get_historical_data(
        #     assets=asset_list, 
        #     start_date=start_date,
        #     end_date=end_date,
        #     frequency=frequency,
        #     fields=field_list
        # )
        
        # Placeholder response
        response = {
            "data": {
                "AAPL": {
                    "dates": ["2023-01-01", "2023-01-02", "2023-01-03"],
                    "prices": [150.25, 152.30, 151.45],
                    "returns": [0, 0.014, -0.006],
                    "volumes": [12500000, 13200000, 11800000]
                }
            },
            "metadata": {
                "frequency": frequency,
                "source": "supabase",
                "last_updated": datetime.now().isoformat(),
                "count": len(asset_list),
                "period_days": 30  # This would be calculated based on start and end dates
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_market_data: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@market_data_bp.route('/latest', methods=['GET'])
def get_latest_market_data():
    """
    Get latest market data for specified assets.
    
    Query Parameters:
    - assets: Comma-separated list of asset symbols
    - fields: Comma-separated list of data fields to include
    """
    try:
        # Extract and validate query parameters
        assets = request.args.get('assets')
        fields = request.args.get('fields')
        
        # Validate required parameters
        if not assets:
            return jsonify({'error': 'Missing required parameter: assets'}), 400
        
        # Parse comma-separated parameters
        asset_list = parse_comma_separated(assets)
        field_list = parse_comma_separated(fields)
        
        # Here we would call the market data service to retrieve the latest data
        # For now, we'll return a placeholder response
        
        # In a real implementation, you would do something like:
        # latest_data = current_app.market_data_service.get_latest_data(
        #     assets=asset_list,
        #     fields=field_list
        # )
        
        # Placeholder response
        response = {
            "data": {
                "AAPL": {
                    "date": "2023-05-01",
                    "price": 155.75,
                    "return": 0.02,
                    "volume": 12800000
                }
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "source": "supabase"
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_latest_market_data: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@market_data_bp.route('/metrics', methods=['GET'])
def get_market_metrics():
    """
    Get aggregated market metrics for specified assets.
    
    Query Parameters:
    - assets: Comma-separated list of asset symbols
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - metrics: Comma-separated list of metrics to include
    """
    try:
        # Extract and validate query parameters
        assets = request.args.get('assets')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        metrics = request.args.get('metrics')
        
        # Validate required parameters
        if not assets:
            return jsonify({'error': 'Missing required parameter: assets'}), 400
        
        if not start_date or not validate_date_format(start_date):
            return jsonify({'error': 'Invalid or missing start_date parameter (YYYY-MM-DD format required)'}), 400
        
        if not end_date or not validate_date_format(end_date):
            return jsonify({'error': 'Invalid or missing end_date parameter (YYYY-MM-DD format required)'}), 400
        
        # Parse comma-separated parameters
        asset_list = parse_comma_separated(assets)
        metric_list = parse_comma_separated(metrics)
        
        # Here we would call the market data service to calculate metrics
        # For now, we'll return a placeholder response
        
        # In a real implementation, you would do something like:
        # market_metrics = current_app.market_data_service.calculate_metrics(
        #     assets=asset_list,
        #     start_date=start_date,
        #     end_date=end_date,
        #     metrics=metric_list
        # )
        
        # Placeholder response
        response = {
            "data": {
                "AAPL": {
                    "volatility": 0.25,
                    "sharpe_ratio": 0.8,
                    "beta": 1.2,
                    "var_95": -0.03,
                    "max_drawdown": -0.15
                }
            },
            "market_metrics": {
                "correlation_matrix": {
                    "AAPL": {"AAPL": 1.0}
                },
                "market_volatility": 0.18,
                "risk_free_rate": 0.04
            },
            "metadata": {
                "period_days": 365,  # This would be calculated based on start and end dates
                "calculation_time": datetime.now().isoformat()
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_market_metrics: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@market_data_bp.route('/batch', methods=['POST'])
def batch_market_data():
    """
    Batch retrieve multiple types of market data in a single request.
    
    Request Body:
    {
        "requests": [
            {
                "type": "historical",
                "assets": ["AAPL", "MSFT"],
                "start_date": "2023-01-01",
                "end_date": "2023-01-31",
                "frequency": "daily"
            },
            ...
        ]
    }
    """
    try:
        # Get request body as JSON
        request_data = request.get_json()
        
        if not request_data or 'requests' not in request_data:
            return jsonify({'error': 'Invalid request body. Must contain "requests" array.'}), 400
        
        requests_array = request_data['requests']
        if not isinstance(requests_array, list):
            return jsonify({'error': '"requests" must be an array.'}), 400
        
        # Process each request in the batch
        start_time = datetime.now()
        results = []
        
        for req in requests_array:
            # Validate request structure
            if 'type' not in req:
                results.append({
                    'error': 'Each request must specify a "type".',
                    'request': req
                })
                continue
            
            req_type = req.get('type')
            
            # Process based on request type
            if req_type == 'historical':
                # Here we would call get_historical_data from the service
                results.append({
                    'type': 'historical',
                    'data': {
                        # Placeholder data
                        "AAPL": {
                            "dates": ["2023-01-01", "2023-01-02"],
                            "prices": [150.25, 152.30],
                            "returns": [0, 0.014]
                        }
                    }
                })
            
            elif req_type == 'metrics':
                # Here we would call calculate_metrics from the service
                results.append({
                    'type': 'metrics',
                    'data': {
                        # Placeholder data
                        "AAPL": {
                            "volatility": 0.25,
                            "sharpe_ratio": 0.8
                        }
                    }
                })
            
            elif req_type == 'latest':
                # Here we would call get_latest_data from the service
                results.append({
                    'type': 'latest',
                    'data': {
                        # Placeholder data
                        "AAPL": {
                            "date": "2023-05-01",
                            "price": 155.75
                        }
                    }
                })
            
            else:
                results.append({
                    'error': f'Unsupported request type: {req_type}',
                    'request': req
                })
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds() * 1000  # Convert to milliseconds
        
        response = {
            "results": results,
            "metadata": {
                "request_time": start_time.isoformat(),
                "processing_time_ms": processing_time
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Error in batch_market_data: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@market_data_bp.route('/correlation', methods=['GET'])
def get_correlation_matrix():
    """
    Get correlation matrix for specified assets.
    
    Query Parameters:
    - assets: Comma-separated list of asset symbols
    - start_date: Start date in YYYY-MM-DD format
    - end_date: End date in YYYY-MM-DD format
    - method: Correlation method (pearson, spearman, kendall)
    """
    try:
        # Extract and validate query parameters
        assets = request.args.get('assets')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        method = request.args.get('method', 'pearson')
        
        # Validate required parameters
        if not assets:
            return jsonify({'error': 'Missing required parameter: assets'}), 400
        
        if not start_date or not validate_date_format(start_date):
            return jsonify({'error': 'Invalid or missing start_date parameter (YYYY-MM-DD format required)'}), 400
        
        if not end_date or not validate_date_format(end_date):
            return jsonify({'error': 'Invalid or missing end_date parameter (YYYY-MM-DD format required)'}), 400
        
        # Parse comma-separated parameters
        asset_list = parse_comma_separated(assets)
        
        # Validate correlation method
        valid_methods = ['pearson', 'spearman', 'kendall']
        if method not in valid_methods:
            return jsonify({
                'error': f'Invalid method parameter. Must be one of: {", ".join(valid_methods)}'
            }), 400
        
        # Here we would call the market data service to calculate correlation
        # For now, we'll return a placeholder response
        
        # In a real implementation, you would do something like:
        # correlation_matrix = current_app.market_data_service.calculate_correlation(
        #     assets=asset_list,
        #     start_date=start_date,
        #     end_date=end_date,
        #     method=method
        # )
        
        # Placeholder response for a correlation matrix
        correlation_data = {}
        for asset1 in asset_list:
            correlation_data[asset1] = {}
            for asset2 in asset_list:
                # Diagonal elements are always 1.0
                if asset1 == asset2:
                    correlation_data[asset1][asset2] = 1.0
                # Non-diagonal elements would be calculated based on historical data
                else:
                    # For placeholder, just set some random value
                    correlation_data[asset1][asset2] = 0.5
        
        response = {
            "data": correlation_data,
            "metadata": {
                "method": method,
                "period_days": 365,  # This would be calculated based on start and end dates
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Error in get_correlation_matrix: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


# Register the blueprint in app.py or similar entry point
# app.register_blueprint(market_data_bp)
