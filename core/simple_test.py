import asyncio
import random
from datetime import datetime, timedelta, UTC
from supabase import create_async_client
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def insert_performance_data(supabase_url: str, supabase_key: str, pool_id: int, num_records: int = 5, delay: float = 2.0):
    """Insert performance history data for a given pool."""
    try:
        # Create Supabase client
        supabase = await create_async_client(supabase_url, supabase_key)
        logger.info(f"Connected to Supabase, inserting {num_records} records for pool {pool_id}")
        
        for i in range(num_records):
            # Generate random performance data
            record = {
                'pool_id': pool_id,
                'created_at': (datetime.now(UTC) - timedelta(hours=i)).isoformat(),
                'apy': round(random.uniform(0.05, 0.15), 4),  # Random APY between 5% and 15%
                'tvl': round(random.uniform(1000000, 2000000), 2)  # Random TVL between 1M and 2M
            }
            
            # Insert record
            response = await supabase.table('performance_history').insert(record).execute()
            logger.info(f"Inserted record {i+1}/{num_records} for pool {pool_id}: {record}")
            
            # Wait before next insert
            await asyncio.sleep(delay)
            
    except Exception as e:
        logger.error(f"Error inserting performance data: {str(e)}")

async def main():
    parser = argparse.ArgumentParser(description='Insert performance history data')
    parser.add_argument('--url', required=True, help='Supabase URL')
    parser.add_argument('--key', required=True, help='Supabase API key')
    parser.add_argument('--pool-id', type=int, required=True, help='Pool ID to insert data for')
    parser.add_argument('--num-records', type=int, default=5, help='Number of records to insert')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between inserts in seconds')
    
    
    args = parser.parse_args()
    
    try:
        await insert_performance_data(
            args.url,
            args.key,
            args.pool_id,
            args.num_records,
            args.delay
        )
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    asyncio.run(main()) 