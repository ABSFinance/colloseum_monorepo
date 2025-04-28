import asyncio
from supabase import create_async_client
from datetime import datetime
import argparse
import time
import json
import sys
import signal

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
    
    # Define callback functions
    def market_data_callback(payload):
        print(f"Received market data: {json.dumps(payload, default=str)}")
    
    def allocation_history_callback(payload):
        print(f"Received allocation history: {json.dumps(payload, default=str)}")
    
    def vault_info_insert_callback(payload):
        print(f"Received vault info insert: {json.dumps(payload, default=str)}")
    
    def vault_info_update_callback(payload):
        print(f"Received vault info update: {json.dumps(payload, default=str)}")
        
    try :

        # Create a single channel for all subscriptions
        channel = supabase.channel('db-changes')
        
        # Set up all subscriptions on the same channel
        channel.on_postgres_changes(
            event="INSERT",
            schema="public",
            table="performance_history",
            callback=market_data_callback
        ).on_postgres_changes(
            event="INSERT",
            schema="public",
            table="abs_vault_allocation_history",
            callback=allocation_history_callback
        ).on_postgres_changes(
            event="INSERT",
            schema="public",
            table="abs_vault_info",
            callback=vault_info_insert_callback
        ).on_postgres_changes(
            event="UPDATE",
            schema="public",
            table="abs_vault_info",
            callback=vault_info_update_callback
        )
        
        # Subscribe to the channel
        print("Subscribing to channel...")
        await channel.subscribe()
        await asyncio.sleep(1)  # Wait for subscription to be established
        print("Channel subscribed successfully")
        
        # Create test data
        perf_record = {
            'pool_id': 2000,
            'created_at': datetime.now().isoformat(),
            'apy': 0.05,
            'tvl': 1000000.0,
        }
        
        vault_info_record = {
            'name': 'test_vault',
            'address': '92choftJrxdnv4FXoau1JsvsCbRcWX8TsUrBcGjo38ea',
            'pool_id': 2000,
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
            'pool_id': 2000,
            'allocated_pool_id': 2000,
            'amount': 1000000.0,
            'status': 'COMPLETED',
            'created_at': datetime.now().isoformat(),
        }
        
        # Insert test data
        print("Inserting test data...")
        await supabase.table("performance_history").insert(perf_record).execute()
        print("Performance history data inserted")
        
        
        # await supabase.table("abs_vault_info").insert(vault_info_record).execute()
        # print("Vault info data inserted")
        
        # await supabase.table("abs_vault_allocation_history").insert(allocation_record).execute()
        # print("Allocation history data inserted")
        
        # Keep the script running to receive events
        # signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
        # signal.pause()
        
        while True :
            await asyncio.sleep(1)
    

    
    except Exception as e:
        print(f"Error in main: {str(e)}")
        sys.exit(1)
    finally:
        await channel.unsubscribe()

if __name__ == "__main__":
    main()