import { Transaction, PublicKey, Connection, Keypair } from '@solana/web3.js';
import { SolanaClient } from '../clients/solana/SolanaClient';
import { ReallocationPlan, VaultState, VaultStatus } from '../types/vault';
import { deposit, DepositParams } from '../clients/voltr/deposit';
import { withdraw, WithdrawParams } from '../clients/voltr/withdraw';
import { VoltrClient } from '@voltr/vault-sdk';
import { ReallocationAction } from '@/types/messages';
import { SupabaseClient } from '@supabase/supabase-js';

export interface TransactionResult {
  success: boolean;
  transactionId: string | null;
  error?: Error;
}

export class Executor {
  private solanaClient: SolanaClient;
  private supabase: SupabaseClient;
  private voltrClient: VoltrClient;
  private connection: Connection;
  private payerKp: Keypair;

  constructor(
    solanaClient: SolanaClient,
    voltrClient: VoltrClient,
    connection: Connection,
    payerKp: Keypair,
    supabase: SupabaseClient    
  ) {
    this.solanaClient = solanaClient;
    this.voltrClient = voltrClient;
    this.connection = connection;
    this.payerKp = payerKp;
    this.supabase = supabase;
  }

  async executeReallocation(plan: ReallocationPlan): Promise<boolean> {
    try {
        console.info(`Executing reallocation for pool ${plan.poolId}`);
      
      // Execute all actions in the plan
      for (const action of plan.actions) {
        if (action.type === 'deposit') {
          const result = await this.executeDeposit(plan.poolId, action);
          if (!result.success) {
            throw new Error(`Failed to execute deposit: ${result.error?.message}`);
          }
        } else if (action.type === 'withdraw') {
          const result = await this.executeWithdraw(plan.poolId, action);
          if (!result.success) {
            throw new Error(`Failed to execute withdraw: ${result.error?.message}`);
          }
        }

        // Update vault state
        await this.updateVaultState(
            plan.poolId,
            action.poolId,
            action.amount,
            VaultStatus.CONFIRMED
        );  
      }

      return true;
    } catch (error) {
      const err = error as Error;
      console.error(`Failed to execute reallocation: ${err.message}`);
      return false;
    }
  }

  private async executeDeposit(poolId: string, action: ReallocationAction): Promise<TransactionResult> {
    
    let allowed_pool: any;
    let org_type: any;
    const vault = await this.supabase.from('abs_vault_info').select('*').eq('pool_id', poolId).single();
    if (!vault.data) throw new Error('Vault not found');
    const token_info = await this.supabase.from('token_info').select('*').eq('address', vault.data.underlying_token).single();
    if (!token_info.data) throw new Error('Token info not found');
    const pool_info = await this.supabase.from('pool_info').select('*').eq('pool_id', action.poolId).single();
    if (!pool_info.data) throw new Error('Pool info not found');
    if (pool_info.data.type === 'drift_vault') {
        const drift_vault = await this.supabase.from('drift_vault_info').select('*').eq('pool_id', poolId).single();
        if (!drift_vault.data) throw new Error('Drift vault info not found');
        allowed_pool = drift_vault.data;
        org_type = 'drift';
    } else if (pool_info.data.type === 'lending_pool') {
        const lending_pool = await this.supabase.from('lending_pool_info').select('*').eq('pool_id', poolId).single();
        if (!lending_pool.data) throw new Error('Lending pool info not found');
        allowed_pool = lending_pool.data;

        let organization = await this.supabase.from('organization_info').select('*').eq('id', allowed_pool.org_id).single();
        if (!organization.data) throw new Error('Organization info not found');
        if (organization.data.type === 'kamino-lend') {
            org_type = 'klend';
        } else if (organization.data.type === 'marginfi') {
            org_type = 'marginfi';
        } else if (organization.data.type === 'save') {
            org_type = 'solend';
        } else {
            throw new Error('Organization type not supported');
        }
    } else {
        throw new Error('Pool type not supported');
    }

    const metadata = token_info.data.metadata;
    const assetTokenProgram = metadata.program_address;

    try {
      const depositParams: DepositParams = {
        vc: this.voltrClient,
        connection: this.connection,
        vault: new PublicKey(poolId),
        payerKp: this.payerKp,
        vaultAssetTokenProgram: new PublicKey(assetTokenProgram),
        vaultAssetMint: new PublicKey(token_info.data.address),
        type: org_type,
        token: token_info.data.symbol,
        address: allowed_pool.address,
        amount: action.amount
      };

      const txSig = await deposit(depositParams);
      return {
        success: true,
        transactionId: txSig
      };
    } catch (error) {
      const err = error as Error;
      console.error(`Failed to execute deposit: ${err.message}`);
      return {
        success: false,
        transactionId: null,
        error: err
      };
    }
  }

  private async executeWithdraw(poolId: string, action: ReallocationAction): Promise<TransactionResult> {

    let allowed_pool: any;
    let org_type: any;
    const vault = await this.supabase.from('abs_vault_info').select('*').eq('pool_id', poolId).single();
    if (!vault.data) throw new Error('Vault not found');
    const token_info = await this.supabase.from('token_info').select('*').eq('address', vault.data.underlying_token).single();
    if (!token_info.data) throw new Error('Token info not found');
    const pool_info = await this.supabase.from('pool_info').select('*').eq('pool_id', action.poolId).single();
    if (!pool_info.data) throw new Error('Pool info not found');
    if (pool_info.data.type === 'drift_vault') {
        const drift_vault = await this.supabase.from('drift_vault_info').select('*').eq('pool_id', poolId).single();
        if (!drift_vault.data) throw new Error('Drift vault info not found');
        allowed_pool = drift_vault.data;
        org_type = 'drift';
    } else if (pool_info.data.type === 'lending_pool') {
        const lending_pool = await this.supabase.from('lending_pool_info').select('*').eq('pool_id', poolId).single();
        if (!lending_pool.data) throw new Error('Lending pool info not found');
        allowed_pool = lending_pool.data;

        let organization = await this.supabase.from('organization_info').select('*').eq('id', allowed_pool.org_id).single();
        if (!organization.data) throw new Error('Organization info not found');
        if (organization.data.type === 'kamino-lend') {
            org_type = 'klend';
        } else if (organization.data.type === 'marginfi') {
            org_type = 'marginfi';
        } else if (organization.data.type === 'save') {
            org_type = 'solend';
        } else {
            throw new Error('Organization type not supported');
        }
    } else {
        throw new Error('Pool type not supported');
    }

    const metadata = token_info.data.metadata;
    const assetTokenProgram = metadata.program_address;

    try {

      const withdrawParams: WithdrawParams = {
        vc: this.voltrClient,
        connection: this.connection,
        vault: new PublicKey(poolId),
        payerKp: this.payerKp,
        vaultAssetTokenProgram: new PublicKey(assetTokenProgram),
        vaultAssetMint: new PublicKey(token_info.data.address),
        type: org_type,
        token: token_info.data.symbol,
        address: allowed_pool.address,
        amount: action.amount
      };

      const txSig = await withdraw(withdrawParams);
      return {
        success: true,
        transactionId: txSig
      };
    } catch (error) {
      const err = error as Error;
      console.error(`Failed to execute withdraw: ${err.message}`);
      return {
        success: false,
        transactionId: null,
        error: err
      };
    }
  }

  async updateVaultState(poolId: string, allocated_pool_id: string, amount: number, status: VaultStatus): Promise<void> {
    try {
      await this.supabase.from('abs_vault_allocation_history').insert({
        pool_id: poolId,
        allocated_pool_id: allocated_pool_id,
        amount: amount,
        status: status
      });
      console.info(`Updated vault state for pool ${poolId}`);
    } catch (error) {
      const err = error as Error;
      console.error(`Failed to update vault state: ${err.message}`);
      throw err;
    }
  }
} 