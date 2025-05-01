import { Connection, PublicKey } from '@solana/web3.js';
import { Constraints } from './Constraints';
import { 
  ReallocationPlan, 
  ValidationResult, 
  ValidationError, 
  ValidationWarning,
  VaultState,
  LiquidityInfo
} from '../types/vault';
import { SolanaClient } from '../clients/solana/SolanaClient';
import { VoltrClient } from '@voltr/vault-sdk';

const { getPosition } = require('../clients/voltr/position');


/**
 * Validator responsible for validating reallocation plans
 * before execution in the Vault Manager
 */
export class Validator {
  private constraints: Constraints;
  private solanaClient: SolanaClient;
  private vaultStateProvider: (poolId: string) => Promise<VaultState | null>;
  
  /**
   * Creates a new validator instance
   * @param constraints - Protocol constraints configuration
   * @param solanaClient - Solana client for liquidity verification
   * @param vaultStateProvider - Function to retrieve current vault state
   */
  constructor(
    constraints: Constraints,
    solanaClient: SolanaClient,
    vaultStateProvider: (poolId: string) => Promise<VaultState | null>
  ) {
    this.constraints = constraints;
    this.solanaClient = solanaClient;
    this.vaultStateProvider = vaultStateProvider;
  }

  /**
   * Validates a reallocation plan against protocol constraints
   * @param plan - Reallocation plan to validate
   * @returns Promise resolving to validation result
   */
  async validateReallocation(plan: ReallocationPlan): Promise<ValidationResult> {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];
    
    try {
      // Check protocol constraints
      const constraintErrors = this.constraints.validate(plan);
      errors.push(...constraintErrors);
      
      // Verify liquidity
      const hasLiquidity = await this.verifyLiquidity(plan);
      
      if (!hasLiquidity) {
        errors.push({
          code: 'INSUFFICIENT_LIQUIDITY',
          message: `Insufficient liquidity for reallocation plan.`,
          details: {
            poolId: plan.poolId
          }
        });
      }
      
      // Check for duplicates
      const duplicateResult = await this.checkDuplicates(plan);
      if (duplicateResult) {
        warnings.push({
          code: 'DUPLICATE_REALLOCATION',
          message: 'A similar reallocation has been executed recently',
          details: duplicateResult
        });
      }
      
    } catch (error) {
      errors.push({
        code: 'VALIDATION_ERROR',
        message: `Validation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
        details: { error: error instanceof Error ? error.message : String(error) }
      });
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      timestamp: new Date().toISOString()
    };
  }

  /**
   * Verifies protocol constraints for a reallocation plan
   * @param plan - Reallocation plan to validate
   * @returns Promise resolving to boolean indicating if constraints are satisfied
   */
  async checkProtocolConstraints(plan: ReallocationPlan): Promise<boolean> {
    const constraintErrors = this.constraints.validate(plan);
    return constraintErrors.length === 0;
  }

  /**
   * Verifies available liquidity for the reallocation
   * @param plan - Reallocation plan to validate
   * @returns Promise resolving to boolean indicating if there is sufficient liquidity
   */
  async verifyLiquidity(vc: VoltrClient, vault: PublicKey, plan: ReallocationPlan): Promise<boolean> {
    try {
      // Import the getPosition function directly to avoid module import issues
      
      const total_position = await getPosition(vc, vault, vault_asset_mint, strategy);
      
      for (const action of plan.actions) {
        try {
          if (action.poolType === "drift_vault") {
            total_position.drift = total_position.drift.subn(action.amount);
          } else if (action.poolType === "klend_vault") {
            total_position.klend = total_position.klend.subn(action.amount);
          } else if (action.poolType === "solend_vault") {
            total_position.solend = total_position.solend.subn(action.amount);
          } else if (action.poolType === "marginfi_vault") {
            total_position.marginfi = total_position.marginfi.subn(action.amount);
          }
          
          // Check if any position would go negative
          if (total_position.drift.isNeg() || 
              total_position.klend.isNeg() || 
              total_position.solend.isNeg() || 
              total_position.marginfi.isNeg()) {
            return false;
          }
        } catch (error) {
          console.error(`Error verifying liquidity for ${action.poolId}:`, error);
          return false;
        }
      }
      
      return true;
    } catch (error) {
      console.error('Error verifying liquidity:', error);
      return false;
    }
  }

  /**
   * Checks for duplicate reallocation plans
   * @param plan - Reallocation plan to check
   * @returns Promise resolving to duplicate details or null if no duplicates
   */
  async checkDuplicates(plan: ReallocationPlan): Promise<Record<string, unknown> | null> {
    try {
      // Get the current vault state
      const currentVaultState = await this.vaultStateProvider(plan.poolId);
      
      if (!currentVaultState) {
        return null; // No current state to compare against
      }
      
      // Check if this is a duplicate by comparing with the current allocation
      // This is a simplified check - real implementation would use more sophisticated comparison
      const isSimilar = this.isAllocationSimilar(
        plan.expectedAllocation, 
        currentVaultState.currentAllocation,
        0.1 // 0.1% threshold for similarity
      );
      
      if (isSimilar) {
        return {
          existing: {
            poolId: currentVaultState.poolId,
            lastUpdated: currentVaultState.lastUpdated,
          },
          similarity: 'high'
        };
      }
      
      return null;
    } catch (error) {
      console.error('Error checking for duplicates:', error);
      return null;
    }
  }

  /**
   * Compares two allocations for similarity
   * @param allocation1 - First allocation to compare
   * @param allocation2 - Second allocation to compare
   * @param threshold - Percentage threshold for similarity
   * @returns Boolean indicating if allocations are similar
   */
  private isAllocationSimilar(allocation1: any, allocation2: any, threshold: number): boolean {
    // Simple implementation for demo purposes
    // In a real scenario, this would properly compare asset distributions
    
    if (!allocation1 || !allocation2) return false;
    if (!allocation1.assets || !allocation2.assets) return false;
    
    if (allocation1.assets.length !== allocation2.assets.length) {
      return false;
    }
    
    // Check if the asset compositions are similar
    for (const asset1 of allocation1.assets) {
      const asset2 = allocation2.assets.find((a: { assetId: string }) => a.assetId === asset1.assetId);
      
      if (!asset2) {
        return false; // Asset in allocation1 not found in allocation2
      }
      
      // Check if percentages are similar within threshold
      if (Math.abs(asset1.percentage - asset2.percentage) > threshold) {
        return false;
      }
    }
    
    return true;
  }
} 