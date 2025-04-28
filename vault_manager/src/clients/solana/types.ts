import { Commitment, PublicKey } from '@solana/web3.js';

export interface SolanaConfig {
  rpcUrl: string;
  wsUrl?: string;
  commitment?: Commitment;
  timeout?: number;
}

export interface TokenAccount {
  pubkey: PublicKey;
  account: {
    data: {
      parsed: {
        info: {
          tokenAmount: {
            amount: string;
            decimals: number;
          };
        };
      };
    };
  };
} 