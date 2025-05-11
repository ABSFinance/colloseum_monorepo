export interface TokenData {
  id: string
  name: string
  symbol: string
  tvl: string
  volume24h: string
  fees24h: string
  feeRatio: string
  yourBalance: string
}

export interface VaultInfo {
  id: number;
  name: string;
  address: string;
  strategy: string;
  description: string | null;
  org_id: number;
  pool_id: number;
  underlying_token: string;
  capacity: number;
  adaptors: string[];
  allowed_pools: number[];
  weight: number[];
  created_at: string; // ISO 8601 date-time string
  updated_at: string; // ISO 8601 date-time string
}