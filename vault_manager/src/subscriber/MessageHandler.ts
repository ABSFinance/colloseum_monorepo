import { ZmqMessage, ReallocationPayload, ValidationResult } from './types';
import { Validator } from '../validator/Validator';
import { Executor } from '../executor/Executor';
import { ReallocationPlan } from '../types/vault';

export class MessageHandler {
  constructor(
    private validator: Validator,
    private executor: Executor
  ) {}

  public async handleMessage(message: ZmqMessage): Promise<void> {
    try {
      const { topic, poolId, payload } = message;
      
      // Convert payload to ReallocationPlan format
      const reallocationPlan: ReallocationPlan = {
        poolId,
        actions: payload.actions.map(action => ({
          ...action,
          poolId // Add poolId to each action
        })),
        expectedAllocation: {
          details: payload.actions.map(action => ({
            poolId: action.poolId,
            allocated_pool_id: action.poolId,
            amount: action.amount
          }))
        },
        timestamp: new Date().toISOString()
      };

      // Validate the reallocation plan
      const validationResult = await this.validator.validateReallocation(reallocationPlan);
      
      if (!validationResult.isValid) {
        console.error(`Validation failed for pool ${poolId}:`, validationResult.errors);
        return;
      }

      // Execute the reallocation plan
      const executionResult = await this.executor.executeReallocation(reallocationPlan);
      
      if (!executionResult) {
        console.error(`Execution failed for pool ${poolId}`);
        return;
      }

      console.log(`Successfully processed reallocation for pool ${poolId}`);
    } catch (error: unknown) {
      if (error instanceof Error) {
        console.error('Error handling message:', error.message);
      } else {
        console.error('Unknown error handling message');
      }
    }
  }
} 