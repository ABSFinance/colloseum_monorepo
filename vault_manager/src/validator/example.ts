/**
 * Example usage of the Validator module
 * This file is for demonstration purposes and is not part of the core functionality
 */

import { Validator, Constraints } from './';
import { SolanaClient } from '../clients/solana/SolanaClient';
import { 
  VaultState, 
  ReallocationPlan,
  Allocation,
  AllocationDetail,
  VaultStatus
} from '../types/vault';
import { VoltrClient } from '@voltr/vault-sdk';
import { createClient } from '@supabase/supabase-js';

// Mock data for demonstration
const mockVaultStates: Record<string, VaultState> = {
  'pool-1': {
    poolId: 'pool-1',
    currentAllocation: {
      details: [
        { poolId: '10002', amount: 1.5, allocated_pool_id: '1105' },
        { poolId: '10002', amount: 20, allocated_pool_id: '1088' }
      ],
    },
    lastUpdated: new Date(),
    status: VaultStatus.ACTIVE
  }
};

// Example function to get vault state
async function getVaultState(poolId: string): Promise<VaultState | null> {
  return mockVaultStates[poolId] || null;
}

// Example of creating and using the validator
async function validateExample() {
  try {
    // Create instances
    const constraints = new Constraints();
    
    // Initialize Solana client (this would normally use actual wallet)
    const solanaConfig = { 
      rpcUrl: 'https://api.mainnet-beta.solana.com', 
      commitment: 'confirmed' as const 
    };
    const solanaClient = new SolanaClient(solanaConfig, { payer: null });

    const vc = new VoltrClient(
      solanaClient.connection,
      solanaClient.wallet
    );

    const supabaseUrl = process.env.SUPABASE_URL;
    const supabaseKey = process.env.SUPABASE_ANON_KEY;
    
    if (!supabaseUrl || !supabaseKey) {
      throw new Error('Missing Supabase credentials');
    }

    const supabase = createClient(supabaseUrl, supabaseKey);
    
    // Create validator
    const validator = new Validator(
      constraints,
      solanaClient,
      supabase,
      vc,
      getVaultState
    );
    
    // Sample reallocation plan
    const plan: ReallocationPlan = {
      poolId: '10002',
      actions: [
        { poolId: '1105', amount: 5000, type: 'withdraw' },
        { poolId: '1088', amount: 5000, type: 'deposit' }
      ],
      expectedAllocation: {
        details: [
          { poolId: '10002', amount: 1.4, allocated_pool_id: '1105' },
          { poolId: '10002', amount: 22.5, allocated_pool_id: '1088' }
        ],
      },
      timestamp: new Date().toISOString()
    };
    
    // Validate the plan
    const result = await validator.validateReallocation(plan);
    
    // Print the result
    console.log('Validation Result:', JSON.stringify(result, null, 2));
    
    if (result.isValid) {
      console.log('Reallocation plan is valid and ready for execution');
    } else {
      console.log('Reallocation plan has validation errors:');
      result.errors.forEach(error => {
        console.log(`- ${error.code}: ${error.message}`);
      });
    }
    
    if (result.warnings.length > 0) {
      console.log('Warnings:');
      result.warnings.forEach(warning => {
        console.log(`- ${warning.code}: ${warning.message}`);
      });
    }
    
  } catch (error) {
    console.error('Error in validation example:', error);
  }
}

// Run the example (would be properly integrated in a real application)
// validateExample().catch(console.error);

export { validateExample }; 