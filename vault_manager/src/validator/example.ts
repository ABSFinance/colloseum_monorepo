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
  AssetAllocation,
  VaultStatus
} from '../types/vault';

// Mock data for demonstration
const mockVaultStates: Record<string, VaultState> = {
  'pool-1': {
    poolId: 'pool-1',
    currentAllocation: {
      assets: [
        { assetId: 'BTC', amount: 1.5, value: 60000, percentage: 60 },
        { assetId: 'ETH', amount: 20, value: 40000, percentage: 40 }
      ],
      totalValue: 100000
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
    
    // Create validator
    const validator = new Validator(
      constraints,
      solanaClient,
      getVaultState
    );
    
    // Sample reallocation plan
    const plan: ReallocationPlan = {
      poolId: 'pool-1',
      actions: [
        { poolId: 'BTC', amount: 5000, type: 'withdraw' },
        { poolId: 'ETH', amount: 5000, type: 'deposit' }
      ],
      expectedAllocation: {
        assets: [
          { assetId: 'BTC', amount: 1.4, value: 55000, percentage: 55 },
          { assetId: 'ETH', amount: 22.5, value: 45000, percentage: 45 }
        ],
        totalValue: 100000
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