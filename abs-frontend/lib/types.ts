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
  id: string;
  name: string;
  description: string;
  address: string;
  capacity: number;
  org_id: number;
  pool_id: number;
  strategy: string;
  underlying_token: string;
  market_tokens: string | null;
  created_at: string;
  updated_at: string;
  timestamp: string;
}