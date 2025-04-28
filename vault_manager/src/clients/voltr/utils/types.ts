export interface VoltrConfig {
  apiKey: string;
  baseUrl: string;
}

export interface Trade {
  poolId: string;
  amount: number;
  type: 'buy' | 'sell';
}

export interface TradeResult {
  success: boolean;
  tradeId: string;
  error?: string;
}

export interface MarketData {
  poolId: string;
  price: number;
  volume: number;
  liquidity: number;
  timestamp: Date;
} 