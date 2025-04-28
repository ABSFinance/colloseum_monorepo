import { VaultState, Transaction } from '../../types/vault';

export interface SupabaseConfig {
  url: string;
  key: string;
}

export interface DatabaseOperations {
  updateAllocation(poolId: string, allocated_pool_id: string, amount: number): Promise<void>;
} 