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
  CLOSED = 'closed',
  CONFIRMED = 'confirmed'
}

export interface Allocation {
  details: AllocationDetail[];
}

export interface AllocationDetail {
  poolId: string;
  allocated_pool_id: string;
  amount: number;
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