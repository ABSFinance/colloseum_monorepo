import { Connection, PublicKey, Transaction as SolanaTransaction, Commitment } from '@solana/web3.js';
import { SolanaConfig, TokenAccount } from './types';

export class SolanaClient {
  private connection: Connection;
  private wallet: any; // Replace with proper wallet type

  constructor(config: SolanaConfig, wallet: any) {
    this.connection = new Connection(config.rpcUrl, {
      commitment: config.commitment || 'confirmed',
      wsEndpoint: config.wsUrl
    });
    this.wallet = wallet;
  }

  async sendTransaction(transaction: SolanaTransaction): Promise<string> {
    const signature = await this.connection.sendTransaction(
      transaction,
      [this.wallet.payer],
      { skipPreflight: false }
    );
    return signature;
  }

  async confirmTransaction(signature: string): Promise<boolean> {
    const confirmation = await this.connection.confirmTransaction(signature);
    return confirmation.value.err === null;
  }

  async getBalance(publicKey: PublicKey): Promise<number> {
    const balance = await this.connection.getBalance(publicKey);
    return balance;
  }
} 