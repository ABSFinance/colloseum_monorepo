import { ReallocationAction } from './messages';

export interface VaultState {
  poolId: string;
  currentAllocation: Allocation;
  lastUpdated: Date;
  status: VaultStatus;
}

export enum VaultStatus {
  ACTIVE = 'active',
  PENDING = 'pending',
  PAUSED = 'paused',
  CLOSED = 'closed'
}

export interface Allocation {
  assets: AssetAllocation[];
  totalValue: number;
}

export interface AssetAllocation {
  assetId: string;
  amount: number;
  value: number;
  percentage: number;
}

export interface ReallocationPlan {
  poolId: string;
  actions: ReallocationAction[];
  expectedAllocation: Allocation;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface ValidationError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ValidationWarning {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
  timestamp: string;
}

export interface LiquidityInfo {
  assetId: string;
  available: number;
  required: number;
  sufficient: boolean;
} 