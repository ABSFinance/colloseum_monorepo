export interface VaultState {
  totalValue: number;
  strategies: {
    strategyId: string;
    amount: number;
  }[];
}

export interface Allocation {
  [poolId: string]: number;
}

export type VaultStatus = 'active' | 'inactive' | 'pending' | 'error';

export interface Transaction {
  id: string;
  type: 'deposit' | 'withdraw';
  amount: number;
  poolId: string;
  status: TransactionStatus;
  timestamp: Date;
}

export type TransactionStatus = 'pending' | 'confirmed' | 'failed'; 