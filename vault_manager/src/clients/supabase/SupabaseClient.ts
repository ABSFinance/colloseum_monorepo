import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { SupabaseConfig, DatabaseOperations } from './types';
import { VaultState, Transaction } from '../../types/vault';

export class SupabaseDatabase implements DatabaseOperations {
  private client: SupabaseClient;

  constructor(config: SupabaseConfig) {
    this.client = createClient(config.url, config.key);
  }

  async updateAllocation(poolId: string, allocated_pool_id: string, amount: number): Promise<void> {
    const { error } = await this.client
      .from('abs_vault_allocation_history')
      .insert({
        pool_id: poolId,
        allocated_pool_id: allocated_pool_id,
        amount: amount,
      });

    if (error) {
      throw new Error(`Failed to update allocation: ${error.message}`);
    }
  }
} 