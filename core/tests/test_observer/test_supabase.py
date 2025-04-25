import asyncio
from supabase import create_async_client
from datetime import datetime
import argparse

def main():
    asyncio.run(async_main())

async def async_main():
    
    parser = argparse.ArgumentParser(description='Test Observer system with real database for standard events: performance history, allocation history, and vault info')
    
    
    parser.add_argument('--url', required=True,
                        help='Supabase URL')
    
    parser.add_argument('--key', required=True,
                        help='Supabase API key')
    
    args = parser.parse_args()
    
    supabase = await create_async_client(
        args.url,
        args.key,
    )
    
    channels = {}
    market_data_table = "performance_history"
    portfolio_state_table = "abs_vault_allocation_history"
    vault_info_table = "abs_vault_info"
    pool_info_table = "pool_info"

    channels["performance_history"] = supabase.channel('performance_changes')
    # Create channels for other tables
    channels["allocation_history"] = supabase.channel('allocation_changes')
    channels["vault_info_insert"] = supabase.channel('vault_info_insert')
    channels["vault_info_update"] = supabase.channel('vault_info_update')

    # Set up Supabase realtime subscription for market data table (performance history)
    channels["performance_history"].on_postgres_changes(
            event="INSERT",
            schema="public",
            table=market_data_table,
            callback=print("market data")
        )
    
    channels["performance_history"].subscribe()
    
            # Set up Supabase realtime subscription for portfolio state table (allocation history)
    channels["allocation_history"].on_postgres_changes(
            event="INSERT",
            schema="public",
            table=portfolio_state_table,
            callback=print("allocation history")
        )
            
    # Set up Supabase realtime subscription for vault info table - INSERT events
    channels["vault_info_insert"].on_postgres_changes(
            event="INSERT",
            schema="public",
            table=vault_info_table,
            callback=print("vault info insert")
        )
            
    # Set up Supabase realtime subscription for vault info table - UPDATE events
    channels["vault_info_update"].on_postgres_changes(
            event="UPDATE",
            schema="public",
            table=vault_info_table,
            callback=print("vault info update")
        )
            
    # Subscribe to all channels
    for channel_name, channel in channels.items():
        print(f"Subscribing to channel: {channel_name}")
        await channel.subscribe()
        
    perf_record = {
        'pool_id': 2000,
        'created_at': datetime.now().isoformat(),
        'apy': 0.05,  # Slightly different APY values
        'tvl': 1000000.0,  # Slightly different TVL values
    }
    
    pool_info_record = {
        'id': 100099,
        'type': 'abs_vault',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
    }
    
    vault_info_record = {
        'name': 'test_vault',
        'address': '92choftJrxdnv4FXoau1JsvsCbRcWX8TsUrBcGjo38ea',
        'pool_id': 100099,
        'org_id': 377,
        'underlying_token': 'Sol11111111111111111111111111111111111111112',
        'capacity': 1000000.0,
        'adaptors': ['kamino-lend', 'drift-vault'],
        'allowed_pools': [1105, 1088],
        'description': 'test_description',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
    }
    
    allocation_record = {
        'pool_id': 100099,
        'allocated_pool_id': 2000,
        'amount': 1000000.0,
        'status': 'COMPLETED',
        'created_at': datetime.now().isoformat(),
    }
    
    await supabase.table(market_data_table).insert(perf_record).execute()
    # await supabase.table(pool_info_table).insert(pool_info_record).execute()
    # await supabase.table(vault_info_table).insert(vault_info_record).execute()
    # await supabase.table(portfolio_state_table).insert(allocation_record).execute()
    

if __name__ == "__main__":
    main()