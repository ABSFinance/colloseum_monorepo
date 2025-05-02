import { ReallocationPlan, AllocationDetail, ValidationError } from '../types/vault';

/**
 * Protocol constraints for vault operations
 */
export class Constraints {
  // Maximum number of assets in a portfolio
  private readonly maxAssets: number;
  
  // Minimum allocation percentage for any asset
  private readonly minAllocationPercentage: number;
  
  // Maximum allocation percentage for any asset
  private readonly maxAllocationPercentage: number;
  
  // Maximum daily percentage change for reallocation
  private readonly maxDailyChangePercentage: number;
  
  // Maximum transaction value
  private readonly maxTransactionValue: number;

  constructor(config?: {
    maxAssets?: number;
    minAllocationPercentage?: number;
    maxAllocationPercentage?: number;
    maxDailyChangePercentage?: number;
    maxTransactionValue?: number;
  }) {
    this.maxAssets = config?.maxAssets || 20;
    this.minAllocationPercentage = config?.minAllocationPercentage || 1.0; // 1%
    this.maxAllocationPercentage = config?.maxAllocationPercentage || 50.0; // 50%
    this.maxDailyChangePercentage = config?.maxDailyChangePercentage || 15.0; // 15%
    this.maxTransactionValue = config?.maxTransactionValue || 1000000; // $1M
  }

  /**
   * Validates asset count in allocation
   * @param allocation - Asset allocations to validate
   * @returns Array of validation errors, empty if valid
   */
  validateAssetCount(assets: AllocationDetail[]): ValidationError[] {
    const errors: ValidationError[] = [];
    
    if (assets.length > this.maxAssets) {
      errors.push({
        code: 'ASSET_COUNT_EXCEEDED',
        message: `Asset count (${assets.length}) exceeds maximum allowed (${this.maxAssets})`,
        details: {
          current: assets.length,
          maximum: this.maxAssets
        }
      });
    }
    
    return errors;
  }

  /**
   * Validates asset allocation percentages
   * @param assets - Asset allocations to validate
   * @returns Array of validation errors, empty if valid
   */
  validateAllocationPercentages(assets: AllocationDetail[]): ValidationError[] {
    const errors: ValidationError[] = [];
    
    for (const asset of assets) {
      if (asset.percentage < this.minAllocationPercentage) {
        errors.push({
          code: 'MIN_ALLOCATION_VIOLATED',
          message: `Asset ${asset.poolId} allocation (${asset.percentage}%) is below minimum (${this.minAllocationPercentage}%)`,
          details: {
            assetId: asset.poolId,
            current: asset.percentage,
            minimum: this.minAllocationPercentage
          }
        });
      }
      
      if (asset.percentage > this.maxAllocationPercentage) {
        errors.push({
          code: 'MAX_ALLOCATION_VIOLATED',
          message: `Asset ${asset.poolId} allocation (${asset.percentage}%) exceeds maximum (${this.maxAllocationPercentage}%)`,
          details: {
            assetId: asset.poolId,
            current: asset.percentage,
            maximum: this.maxAllocationPercentage
          }
        });
      }
    }
    
    return errors;
  }

  /**
   * Validates the total of allocation percentages
   * @param assets - Asset allocations to validate
   * @returns Array of validation errors, empty if valid
   */
  validateTotalAllocation(assets: AllocationDetail[]): ValidationError[] {
    const errors: ValidationError[] = [];
    
    const totalPercentage = assets.reduce((sum, asset) => sum + asset.percentage, 0);
    
    if (Math.abs(totalPercentage - 100) > 0.01) { // Allow 0.01% tolerance for floating point
      errors.push({
        code: 'TOTAL_ALLOCATION_INVALID',
        message: `Total allocation (${totalPercentage}%) is not equal to 100%`,
        details: {
          total: totalPercentage,
          expected: 100
        }
      });
    }
    
    return errors;
  }

  /**
   * Validates transaction value
   * @param plan - Reallocation plan to validate
   * @returns Array of validation errors, empty if valid
   */
  validateTransactionValue(plan: ReallocationPlan): ValidationError[] {
    const errors: ValidationError[] = [];
    
    const totalValue = plan.actions.reduce((sum, action) => sum + action.amount, 0);
    
    if (totalValue > this.maxTransactionValue) {
      errors.push({
        code: 'MAX_TRANSACTION_VALUE_EXCEEDED',
        message: `Transaction value (${totalValue}) exceeds maximum allowed (${this.maxTransactionValue})`,
        details: {
          current: totalValue,
          maximum: this.maxTransactionValue
        }
      });
    }
    
    return errors;
  }

  /**
   * Apply all constraint validations to a reallocation plan
   * @param plan - Reallocation plan to validate
   * @returns Array of validation errors, empty if valid
   */
  validate(plan: ReallocationPlan): ValidationError[] {
    const assetCountErrors = this.validateAssetCount(plan.expectedAllocation.details);
    const percentageErrors = this.validateAllocationPercentages(plan.expectedAllocation.details);
    const totalAllocationErrors = this.validateTotalAllocation(plan.expectedAllocation.details);
    const transactionValueErrors = this.validateTransactionValue(plan);
    
    return [
      ...assetCountErrors,
      ...percentageErrors,
      ...totalAllocationErrors,
      ...transactionValueErrors
    ];
  }
} 