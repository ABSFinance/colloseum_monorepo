#!/usr/bin/env python3
"""
Market Data Example

This script demonstrates how to use the MarketData model to fetch and
process market data for portfolio optimization.
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from supabase import create_client, Client

# Add project root to sys.path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.market_data import MarketData, MarketMetrics, DriftVaultMetrics

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key)

async def display_market_metrics_summary(market_data: MarketData):
    """Display a summary of market metrics."""
    print("\n=== Market Metrics Summary ===\n")
    
    # Get all market metrics
    metrics = await market_data.get_market_metrics()
    
    # Print summary counts
    print(f"Total assets: {metrics.total_count}")
    print(f"Drift vaults: {len(metrics.drift_vaults)}")
    print(f"Yield pools: {len(metrics.yield_pools)}")
    print(f"Lending pools: {len(metrics.lending_pools)}")
    print(f"ABS vaults: {len(metrics.abs_vaults)}")
    
    # Calculate average APY by asset type
    if metrics.drift_vaults:
        avg_apy = sum(dv.apy for dv in metrics.drift_vaults) / len(metrics.drift_vaults)
        print(f"Average drift vault APY: {avg_apy:.2%}")
    
    if metrics.yield_pools:
        avg_apy = sum(yp.apy for yp in metrics.yield_pools) / len(metrics.yield_pools)
        print(f"Average yield pool APY: {avg_apy:.2%}")
    
    if metrics.lending_pools:
        avg_apy = sum(lp.apy for lp in metrics.lending_pools) / len(metrics.lending_pools)
        print(f"Average lending pool APY: {avg_apy:.2%}")
    
    if metrics.abs_vaults:
        avg_apy = sum(av.apy for av in metrics.abs_vaults) / len(metrics.abs_vaults)
        print(f"Average ABS vault APY: {avg_apy:.2%}")

async def display_single_asset_details(market_data: MarketData):
    """Display details for a sample asset of each type."""
    print("\n=== Sample Asset Details ===\n")
    
    # Get all market metrics first
    metrics = await market_data.get_market_metrics()
    
    # Display a sample drift vault if available
    if metrics.drift_vaults:
        print("\n--- Sample Drift Vault ---\n")
        sample_asset = metrics.drift_vaults[0]
        asset_id = sample_asset.address
        
        # Get detailed metrics for this asset
        asset_metrics = await market_data.get_single_asset_metrics(asset_id, 'drift_vault')
        
        print(f"Name: {asset_metrics.name}")
        print(f"Address: {asset_metrics.address}")
        print(f"Strategy: {asset_metrics.strategy}")
        print(f"TVL: ${asset_metrics.tvl:,.2f}")
        print(f"APY: {asset_metrics.apy:.2%}")
        print(f"Volatility: {asset_metrics.volatility:.2%}")
        print(f"Organization: {asset_metrics.org_name}")
        print(f"Token: {asset_metrics.token_symbol}")
    
    # Display a sample yield pool if available
    if metrics.yield_pools:
        print("\n--- Sample Yield Pool ---\n")
        sample_asset = metrics.yield_pools[0]
        asset_id = sample_asset.address
        
        # Get detailed metrics for this asset
        asset_metrics = await market_data.get_single_asset_metrics(asset_id, 'yield_pool')
        
        print(f"Name: {asset_metrics.name}")
        print(f"Address: {asset_metrics.address}")
        print(f"Protocol: {asset_metrics.protocol}")
        print(f"Chain: {asset_metrics.chain}")
        print(f"TVL: ${asset_metrics.tvl:,.2f}")
        print(f"APY: {asset_metrics.apy:.2%}")
        print(f"Organization: {asset_metrics.org_name}")
        print(f"Token: {asset_metrics.token_symbol}")

async def analyze_historical_performance(market_data: MarketData):
    """Analyze historical performance for a sample asset."""
    print("\n=== Historical Performance Analysis ===\n")
    
    # Get a sample asset ID
    metrics = await market_data.get_market_metrics(asset_types=['drift_vault'])
    
    if not metrics.drift_vaults:
        print("No drift vaults found to analyze")
        return
    
    sample_asset = metrics.drift_vaults[0]
    asset_id = sample_asset.address
    asset_name = sample_asset.name
    
    print(f"Analyzing historical performance for: {asset_name} ({asset_id})")
    
    # Set date range for last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    # Get historical data
    historical_data = await market_data.get_market_data(
        asset_ids=[asset_id],
        start_date=start_date,
        end_date=end_date,
        frequency='daily'
    )
    
    if asset_id not in historical_data:
        print("No historical data found for this asset")
        return
    
    df = historical_data[asset_id]
    
    # Print summary statistics
    print("\nSummary Statistics:")
    print(f"Data points: {len(df)}")
    print(f"Average TVL: ${df['tvl'].mean():,.2f}")
    print(f"Average APY: {df['apy'].mean():.2%}")
    
    if 'max_drawdown' in df.columns:
        print(f"Average Max Drawdown: {df['max_drawdown'].mean():.2%}")
    
    # Plot TVL over time
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['tvl'])
    plt.title(f"TVL Over Time - {asset_name}")
    plt.xlabel("Date")
    plt.ylabel("TVL ($)")
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig("tvl_over_time.png")
    print("TVL chart saved as 'tvl_over_time.png'")
    
    # Plot APY over time
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['apy'] * 100)  # Convert to percentage
    plt.title(f"APY Over Time - {asset_name}")
    plt.xlabel("Date")
    plt.ylabel("APY (%)")
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig("apy_over_time.png")
    print("APY chart saved as 'apy_over_time.png'")

async def display_portfolio_composition(market_data: MarketData):
    """Display the composition of a sample portfolio."""
    print("\n=== Portfolio Composition ===\n")
    
    # Get all ABS vaults
    metrics = await market_data.get_market_metrics(asset_types=['abs_vault'])
    
    if not metrics.abs_vaults:
        print("No ABS vaults found to analyze")
        return
    
    # Find a vault with allocations
    portfolio_vault = None
    for vault in metrics.abs_vaults:
        if vault.allocation_count > 0:
            portfolio_vault = vault
            break
    
    if not portfolio_vault:
        print("No ABS vault with allocations found")
        return
    
    portfolio_id = portfolio_vault.pool_id
    portfolio_name = portfolio_vault.name
    
    print(f"Analyzing portfolio composition for: {portfolio_name} (ID: {portfolio_id})")
    
    # Get current portfolio
    portfolio = await market_data.get_current_portfolio(
        portfolio_id=portfolio_id,
        include_history=True,
        history_days=30
    )
    
    # Print portfolio summary
    print(f"\nTotal Value: ${portfolio['total_value']:,.2f}")
    print(f"Timestamp: {portfolio['timestamp']}")
    print(f"Number of allocations: {len(portfolio['allocations'])}")
    
    # Print allocations
    print("\nCurrent Allocations:")
    for alloc in portfolio['allocations']:
        asset_id = alloc['asset_id']
        weight = alloc['weight']
        value = alloc['value']
        
        print(f"Asset ID: {asset_id}")
        print(f"  Weight: {weight:.2%}")
        print(f"  Value: ${value:,.2f}")
        print()
    
    # Print historical allocation count if available
    if 'historical_allocations' in portfolio:
        history = portfolio['historical_allocations']
        print(f"\nHistorical allocation data points: {len(history)}")
        
        if history:
            # Get the earliest and latest dates
            earliest_date = history[0]['date']
            latest_date = history[-1]['date']
            
            print(f"Historical data from {earliest_date} to {latest_date}")

async def main():
    """Main function to demonstrate MarketData functionality."""
    # Initialize MarketData with Supabase client
    market_data = MarketData(supabase)
    
    try:
        # Display market metrics summary
        await display_market_metrics_summary(market_data)
        
        # Display single asset details
        await display_single_asset_details(market_data)
        
        # Analyze historical performance
        await analyze_historical_performance(market_data)
        
        # Display portfolio composition
        await display_portfolio_composition(market_data)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 