# Vault Manager Architecture

## Overview

The Vault Manager is the execution layer of the ABS Finance system, responsible for validating and executing portfolio reallocations. It subscribes to ZMQ messages from the Evaluator and performs the final validation and execution steps.

## Components

### 1. ZMQ Subscriber

- Subscribes to reallocation messages from the Evaluator
- Topics:
  - `reallocation.{pool_id}.success` - Fully matched reallocations
  - `reallocation.{pool_id}.partial` - Partially matched reallocations
  - `reallocation.{pool_id}.error` - Failed reallocations
  - `reallocation.{pool_id}.warning` - Warning conditions
  - `reallocation.{pool_id}.no_change` - No reallocation needed

### 2. Validator

- Performs final validation checks before execution:
  - Protocol constraints verification
  - Liquidity verification
  - duplicate check
- Generates validation reports
- Approves or rejects reallocation plans

### 3. Executor

- Executes validated reallocation plans on Solana blockchain
- Handles transaction signing and submission
- Manages transaction retries and error handling
- Tracks execution status and updates vault state
- Update the vault state in the database

## Flow

1. **Message Reception**

   - ZMQ Subscriber receives reallocation messages from Evaluator
   - Messages contain reallocation actions and liquidity metrics

2. **Validation**

   - Validator performs comprehensive checks
   - Verifies protocol constraints
   - Confirms liquidity availability
   - duplicate check

3. **Execution**

   - Executor processes validated reallocation plans
   - Creates and signs transactions
   - Submits transactions to Solana network
   - Monitors execution status

4. **State Update**
   - Updates vault state after successful execution
   - Records execution results
   - Notifies relevant components of completion
   - Update the vault state in the database

## Error Handling

- Transaction failures are handled with retry logic
- Failed validations trigger error notifications
- Partial executions are tracked and reported
- System maintains audit trail of all actions

## Integration Points

- **Evaluator**: Receives reallocation plans via ZMQ
- **Solana RPC**: Executes transactions on blockchain
- **Storage**: Updates vault state and records
- **Monitoring**: Reports execution status and metrics
