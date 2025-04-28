"""
Portfolio Evaluator

This module implements the portfolio reallocation evaluation flow as described in the documentation.
It calculates the difference between current and target allocations, determines if reallocation
is needed, and generates the appropriate reallocation transactions.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, UTC
import json
import zmq

class Evaluator:
    """Portfolio evaluator for reallocation decisions."""
    
    def __init__(self, supabase_client=None, reallocation_threshold=0.05, zmq_publisher=None):
        """Initialize the evaluator.
        
        Args:
            supabase_client: Supabase client for data operations
            reallocation_threshold: Threshold percentage difference that triggers reallocation (default: 5%)
            zmq_publisher: ZMQ publisher socket for sending reallocation notifications
        """
        self.logger = logging.getLogger(f"{__name__}.Evaluator")
        self.vaults: Dict[str, Dict[str, Any]] = {}  # Store vault info by pool_id
        self.supabase_client = supabase_client
        self.reallocation_threshold = reallocation_threshold
        self.zmq_publisher = zmq_publisher
        
    def initialize_zmq_publisher(self, zmq_address="tcp://*:5555"):
        """Initialize ZMQ publisher socket.
        
        Args:
            zmq_address: ZMQ binding address (default: tcp://*:5555)
        """
        try:
            context = zmq.Context()
            self.zmq_publisher = context.socket(zmq.PUB)
            self.zmq_publisher.bind(zmq_address)
            self.logger.info(f"ZMQ publisher initialized and bound to {zmq_address}")
        except Exception as e:
            self.logger.error(f"Error initializing ZMQ publisher: {str(e)}")
            self.zmq_publisher = None
            
    def publish_zmq_message(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish a message to the ZMQ publisher socket.
        
        Args:
            topic: Message topic
            message: Message payload as a dictionary
            
        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self.zmq_publisher:
            self.logger.warning("ZMQ publisher not initialized, cannot send message")
            return False
            
        try:
            # Convert message to JSON
            json_message = json.dumps(message)
            
            # Send message with topic prefix
            self.zmq_publisher.send_string(f"{topic} {json_message}")
            
            self.logger.info(f"Published ZMQ message with topic '{topic}'")
            return True
        except Exception as e:
            self.logger.error(f"Error publishing ZMQ message: {str(e)}")
            return False
        
    async def initialize_vault_info(self) -> None:
        """Initialize vault information from Supabase for all vaults.
        Fetches all available vault records from abs_vault_info table.
        Also fetches abs_vault_allocation_history to determine current allocations.
        """
        if not self.supabase_client:
            self.logger.error("Supabase client not initialized")
            return
        
        try:
            # Fetch all vault records
            vault_response = await self.supabase_client.table('abs_vault_info') \
                .select('*') \
                .order('created_at', desc=True) \
                .execute()
                
            if not vault_response.data:
                self.logger.warning("No vault information found")
                return
                
            # Process each vault record
            vault_count = 0
            for vault_record in vault_response.data:
                try:
                    # Extract pool_id from the record
                    pool_id = vault_record.get('pool_id')
                    if not pool_id:
                        self.logger.warning(f"Skipping vault record missing pool_id: {vault_record}")
                        continue
                        
                    # Update the vault info in our local storage (without allocation yet)
                    self.update_vault(vault_record)
                    vault_count += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing vault record: {str(e)}")
                
            self.logger.info(f"Initialized {vault_count} vault configurations from Supabase")
            
            # Now fetch allocation history to determine current allocations
            alloc_response = await self.supabase_client.table('abs_vault_allocation_history') \
                .select('*') \
                .order('created_at', desc=True) \
                .execute()
                
            if not alloc_response.data:
                self.logger.warning("No allocation history found")
                return
                
            # Convert to DataFrame for easier processing
            alloc_df = pd.DataFrame(alloc_response.data)
            
            # Parse timestamps using ISO8601 format to avoid warnings
            try:
                alloc_df['created_at_parsed'] = pd.to_datetime(alloc_df['created_at'], format='ISO8601')
            except Exception as e:
                self.logger.warning(f"ISO8601 parsing failed for allocation history: {str(e)}")
                # Fall back to pandas' flexible parser with error coercion
                alloc_df['created_at_parsed'] = pd.to_datetime(alloc_df['created_at'], errors='coerce')
                
            # Drop rows with invalid timestamps (NaT)
            if alloc_df['created_at_parsed'].isna().any():
                invalid_count = alloc_df['created_at_parsed'].isna().sum()
                self.logger.warning(f"Dropped {invalid_count} rows with invalid timestamps from allocation history")
                alloc_df = alloc_df.dropna(subset=['created_at_parsed'])
            
            # Process allocation data by vault (pool_id)
            for pool_id, vault_data in self.vaults.items():
                try:
                    # Filter allocations for this vault and create a copy to avoid SettingWithCopyWarning
                    vault_allocations = alloc_df[alloc_df['pool_id'] == int(pool_id)].copy()
                    
                    if vault_allocations.empty:
                        self.logger.warning(f"No allocation history found for vault {pool_id}")
                        continue
                    
                    # Sort by timestamp so most recent allocations are processed first
                    vault_allocations = vault_allocations.sort_values('created_at_parsed', ascending=False)
                    
                    # Initialize allocation dictionary
                    current_allocation = {}
                    
                    # Two approaches are possible:
                    # 1. Use the most recent complete allocation set (snapshot approach)
                    # 2. Reconstruct by summing all additions/subtractions (cumulative approach)
                    
                    # Let's use the snapshot approach for simplicity and reliability
                    # Get unique timestamps in descending order (most recent first)
                    timestamps = vault_allocations['created_at_parsed'].unique()
                    
                    # Find most recent complete allocation
                    found_complete_allocation = False
                    for ts in timestamps:
                        # Get all allocations at this timestamp
                        ts_allocations = vault_allocations[vault_allocations['created_at_parsed'] == ts]
                        
                        # Check if all allocated_pool_ids have non-zero amounts at this timestamp
                        if (ts_allocations['amount'] > 0).all():
                            # This is a complete allocation, use it
                            for _, row in ts_allocations.iterrows():
                                allocated_pool_id = row['allocated_pool_id']
                                amount = row['amount']
                                # Initialize the key if it doesn't exist
                                if int(allocated_pool_id) not in current_allocation:
                                    current_allocation[int(allocated_pool_id)] = 0.0
                                current_allocation[int(allocated_pool_id)] += float(amount)
                            
                            self.logger.info(f"Found complete allocation for vault {pool_id} at {ts}")
                            found_complete_allocation = True
                            break
                    
                    # If no complete allocation found, use the cumulative approach
                    if not found_complete_allocation:
                        self.logger.info(f"No complete allocation found for vault {pool_id}, reconstructing from history")
                        
                        # Group by allocated_pool_id and sum amounts
                        allocation_sums = vault_allocations.groupby('allocated_pool_id')['amount'].sum()
                        
                        # Convert to dictionary
                        for allocated_pool_id, amount in allocation_sums.items():
                            if amount > 0:  # Only include positive allocations
                                # Always initialize the key in the dictionary first
                                current_allocation[int(allocated_pool_id)] = float(amount)
                    
                    # Update the vault's current allocation
                    print(f"current_allocation {current_allocation}")
                    self.vaults[pool_id]['current_allocation'] = current_allocation
                    self.logger.info(f"Updated current allocation for vault {pool_id} with {len(current_allocation)} allocated pools")
                    
                except Exception as e:
                    self.logger.error(f"Error processing allocation for vault {pool_id}: {str(e)}")
                    import traceback
                    self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            self.logger.info(f"Completed allocation initialization for {len(self.vaults)} vaults")
            
        except Exception as e:
            self.logger.error(f"Error initializing vault information: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
        
    def update_vault(self, vault_info: Dict[str, Any]) -> None:
        """Initialize or update vault information.
        
        Args:
            vault_info: Dictionary containing vault configuration
        """
        pool_id = vault_info.get('pool_id')
        if not pool_id:
            if 'vault_info' in vault_info:
                vault_info = vault_info['vault_info']
                pool_id = vault_info.get('pool_id')
            else:
                self.logger.error(f"Vault info missing pool_id : {vault_info}")
                return
            
        # Initialize or update vault data structure
        if pool_id not in self.vaults:
            self.vaults[pool_id] = {
                'vault_info': vault_info,
                'current_allocation': {}
            }
        else:
            self.vaults[pool_id]['vault_info'] = vault_info
        
    def update_allocation(self, pool_id: str, allocation_data: Dict[int, float]) -> None:
        """Update current allocation for a vault.
        
        Args:
            pool_id: ID of the vault
            allocation_data: Dictionary mapping allocated_pool_id to amount
        """
        if pool_id not in self.vaults:
            self.logger.error(f"Unknown vault {pool_id}")
            return
            
        self.vaults[pool_id]['current_allocation'] = allocation_data
        self.logger.info(f"Updated allocation for vault {pool_id}")
        
    def calculate_utilization(self, 
                            current_allocation: Dict[int, float], 
                            target_allocation: Dict[int, float]) -> Dict[str, Any]:
        """Calculate the utilization metrics between current and target allocations.
        
        Args:
            current_allocation: Dictionary mapping pool_id to current amount
            target_allocation: Dictionary mapping pool_id to target amount
            
        Returns:
            Dictionary containing utilization metrics
        """
        # Initialize metrics
        metrics = {
            'overall': 0.0,
            'by_asset': []
        }
        
        # Calculate per-asset utilization first
        utilization_values = []
        
        for pool_id in set(list(current_allocation.keys()) + list(target_allocation.keys())):
            current_amount = current_allocation.get(pool_id, 0.0)
            target_amount = target_allocation.get(pool_id, 0.0)
            
            # Avoid division by zero
            if target_amount == 0:
                utilization = 0.0 if current_amount == 0 else float('inf')
            else:
                utilization = current_amount / target_amount
                utilization_values.append(utilization)  # Add to list for median calculation
                
            metrics['by_asset'].append({
                'asset': pool_id,
                'utilization': utilization
            })
        
        # Calculate overall utilization as the median of individual asset utilizations
        # This provides a more robust measure that isn't skewed by outliers
        if utilization_values:
            overall_utilization = np.median(utilization_values)
        else:
            # Default value if there are no valid utilization values
            overall_utilization = 1.0
            
        metrics['overall'] = overall_utilization
        
        return metrics
    
    def calculate_reallocation_needs(self, 
                                   current_allocation: Dict[int, float], 
                                   target_allocation: Dict[int, float]) -> Tuple[List[Dict[str, Any]], bool]:
        """Calculate the reallocation needs based on current and target allocations.
        
        Args:
            current_allocation: Dictionary mapping pool_id to current amount
            target_allocation: Dictionary mapping pool_id to target amount
            
        Returns:
            Tuple containing:
            - List of reallocation actions (pool_id and amount)
            - Boolean indicating if reallocation is needed
        """
        # Initialize reallocation actions list
        reallocation_actions = []
        
        # Check if there are any significant differences
        needs_reallocation = False
        overall = 0
        
        print(f"current_allocation : {current_allocation}")
        print(f"target_allocation : {target_allocation}")
        
        # Check each asset in both current and target allocations
        for pool_id in set(list(current_allocation.keys()) + list(target_allocation.keys())):
            current_amount = current_allocation.get(pool_id, 0.0)
            target_amount = target_allocation.get(pool_id, 0.0)
            
            # Calculate absolute difference
            target_difference = target_amount - current_amount
            current_difference = current_amount - target_amount
            
            # Handle division by zero cases
            if target_amount == 0 and current_amount == 0:
                # Both are zero, no difference
                difference = 0
            elif target_amount == 0:
                # Target is zero but current is not, difference is 100%
                difference = 1.0
            elif current_amount == 0:
                # Current is zero but target is not, difference is 100%
                difference = 1.0
            else:
                # Normal case - calculate percentage difference
                difference = max(target_difference / target_amount, current_difference / current_amount)
            
            # Skip insignificant differences (below threshold)
            if abs(difference) == 0:
                continue
            
            overall += difference
                
            reallocation_actions.append({
                'pool_id': pool_id,
                'amount': target_difference
            })
            
        if overall / len(current_allocation) > self.reallocation_threshold:
            needs_reallocation = True
                
        return reallocation_actions, needs_reallocation
    
    async def check_liquidity(self, reallocation_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check if there is sufficient liquidity for the reallocation actions.
        Calls RPC service to fetch liquidity data.
        
        Args:
            reallocation_actions: List of reallocation actions (pool_id and amount)
            
        Returns:
            Dictionary with liquidity assessment results
        """
        if not self.supabase_client:
            self.logger.error("Supabase client not initialized")
            return {
                'has_liquidity': False,
                'fully_matched': False,
                'details': "Supabase client not initialized"
            }
            
        # Separate the actions that require liquidity (negative amounts)
        withdraw_actions = [action for action in reallocation_actions if action['amount'] < 0]
        deposit_actions = [action for action in reallocation_actions if action['amount'] > 0]
        
        total_withdraw = sum(abs(action['amount']) for action in withdraw_actions)
        total_deposit = sum(action['amount'] for action in deposit_actions)
        
        try:
            # Call RPC to fetch liquidity data
            # This is a placeholder for the actual RPC call
            # In a real implementation, this would call your liquidity service
            
            # Check if we have enough to withdraw (placeholder logic)
            has_liquidity = True
            fully_matched = True
            liquidity_details = []
            shortfall = 0.0
            
            # Example logic for checking liquidity for each pool
            for action in withdraw_actions:
                pool_id = action['pool_id']
                amount = abs(action['amount'])  # Convert to positive for withdrawal
                
                # Placeholder for RPC call to check pool liquidity
                try:
                    # In a real implementation, call your liquidity service
                    # For now, assume all pools have enough liquidity for simplicity
                    available_liquidity = amount  # Placeholder
                    
                    if available_liquidity < amount:
                        fully_matched = False
                        shortfall += (amount - available_liquidity)
                        
                    liquidity_details.append({
                        'pool_id': pool_id,
                        'requested': amount,
                        'available': available_liquidity,
                        'fully_matched': available_liquidity >= amount
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error checking liquidity for pool {pool_id}: {str(e)}")
                    has_liquidity = False
                    fully_matched = False
                    liquidity_details.append({
                        'pool_id': pool_id,
                        'requested': amount,
                        'available': 0,
                        'fully_matched': False,
                        'error': str(e)
                    })
            
            return {
                'has_liquidity': has_liquidity,
                'fully_matched': fully_matched,
                'total_withdraw': total_withdraw,
                'total_deposit': total_deposit,
                'liquidity_shortfall': shortfall if not fully_matched else 0.0,
                'details': liquidity_details
            }
            
        except Exception as e:
            self.logger.error(f"Error checking liquidity: {str(e)}")
            return {
                'has_liquidity': False,
                'fully_matched': False,
                'error': str(e)
            }
            
    def evaluate_portfolio(self, 
                         pool_id: str, 
                         optimization_result: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the portfolio and determine if reallocation is needed.
        
        Args:
            pool_id: ID of the vault to evaluate
            optimization_result: Dictionary containing optimization results from optimizer
            
        Returns:
            Dictionary containing evaluation results and reallocation plan if needed
        """
        try:
            # Validate inputs
            if pool_id not in self.vaults:
                self.logger.error(f"Unknown vault {pool_id}")
                return {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': f"Unknown vault {pool_id}",
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
            # Get current allocation
            current_allocation = self.vaults[pool_id].get('current_allocation', {})
            if not current_allocation:
                self.logger.warning(f"No current allocation data for vault {pool_id}")
                
            # Get new allocation from optimization result
            new_allocation = optimization_result.get('allocation', {})
            if not new_allocation:
                self.logger.error(f"No allocation data in optimization result for vault {pool_id}")
                return {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': "No allocation data in optimization result",
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
            # Calculate utilization metrics
            utilization_metrics = self.calculate_utilization(current_allocation, new_allocation)
            
            # Check if utilization exceeds target
            overall_utilization = utilization_metrics.get('overall', 0.0)
            
            # If utilization is within acceptable range (e.g., 95-105%), no reallocation needed
            if 1.0 - self.reallocation_threshold <= overall_utilization <= 1.0 + self.reallocation_threshold:
                self.logger.info(f"Vault {pool_id} utilization ({overall_utilization:.2f}) within acceptable range, no reallocation needed")
                return {
                    'pool_id': pool_id,
                    'status': 'success',
                    'needs_reallocation': False,
                    'utilization_metrics': utilization_metrics,
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
            # Calculate reallocation actions
            reallocation_actions, needs_reallocation = self.calculate_reallocation_needs(
                current_allocation, new_allocation
            )
            
            # If no significant reallocation needed, return early
            if not needs_reallocation:
                self.logger.info(f"No significant reallocation needed for vault {pool_id}")
                return {
                    'pool_id': pool_id,
                    'status': 'success',
                    'needs_reallocation': False,
                    'utilization_metrics': utilization_metrics,
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
            # At this point, we need reallocation
            self.logger.info(f"Reallocation needed for vault {pool_id}, preparing plan")
            
            # Return evaluation result with reallocation actions
            return {
                'pool_id': pool_id,
                'status': 'success',
                'needs_reallocation': True,
                'utilization_metrics': utilization_metrics,
                'reallocation_actions': reallocation_actions,
                'timestamp': pd.Timestamp.now(UTC).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error evaluating portfolio for vault {pool_id}: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                'pool_id': pool_id,
                'status': 'error',
                'message': str(e),
                'timestamp': pd.Timestamp.now(UTC).isoformat()
            }
    
    async def process_reallocation(self, 
                                pool_id: str, 
                                reallocation_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process the reallocation by executing the reallocation actions.
        
        Args:
            pool_id: ID of the vault being reallocated
            reallocation_actions: List of reallocation actions (pool_id and amount)
            
        Returns:
            Dictionary containing reallocation results
        """
        try:
            # Check liquidity for the reallocation actions
            liquidity_result = await self.check_liquidity(reallocation_actions)
            
            # If no liquidity, cannot proceed with reallocation
            if not liquidity_result.get('has_liquidity', False):
                self.logger.error(f"Insufficient liquidity for vault {pool_id} reallocation")
                error_result = {
                    'pool_id': pool_id,
                    'status': 'error',
                    'message': "Insufficient liquidity for reallocation",
                    'liquidity_result': liquidity_result,
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
                # Publish error status to ZMQ
                self.publish_zmq_message(
                    topic=f"reallocation.{pool_id}.error",
                    message=error_result
                )
                
                return error_result
                
            # Check if liquidity is fully matched
            fully_matched = liquidity_result.get('fully_matched', False)
            
            # Create reallocation summary
            reallocation_summary = {
                'reallocation_id': f"RA{int(datetime.now(UTC).timestamp())}",
                'timestamp': pd.Timestamp.now(UTC).isoformat(),
                'status': 'MATCHED' if fully_matched else 'PARTIAL',
                'pool_id': pool_id,
                'reallocation_actions': reallocation_actions,
                'liquidity_metrics': liquidity_result
            }
            
            # If not fully matched, include shortfall information
            if not fully_matched:
                reallocation_summary['liquidity_shortfall'] = liquidity_result.get('liquidity_shortfall', 0.0)
                
            # Simulate market impact (placeholder)
            # In a real implementation, this would model the market impact of the reallocation
            estimated_market_impact = 0.001  # 0.1% placeholder
            reallocation_summary['estimated_market_impact'] = estimated_market_impact
            
            # Calculate total reallocation amount (sum of absolute values)
            total_reallocation_amount = sum(abs(action['amount']) for action in reallocation_actions)
            reallocation_summary['total_reallocation_amount'] = total_reallocation_amount
            
            # Prepare result
            result = {
                'status': 'success',
                'reallocation_summary': reallocation_summary,
                'timestamp': pd.Timestamp.now(UTC).isoformat()
            }
            
            # Send reallocation result to ZMQ
            status_topic = "reallocation.success" if fully_matched else "reallocation.partial"
            self.publish_zmq_message(
                topic=f"{status_topic}.{pool_id}",
                message=result
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing reallocation for vault {pool_id}: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            error_result = {
                'pool_id': pool_id,
                'status': 'error',
                'message': str(e),
                'timestamp': pd.Timestamp.now(UTC).isoformat()
            }
            
            # Publish error status to ZMQ
            self.publish_zmq_message(
                topic=f"reallocation.{pool_id}.error",
                message=error_result
            )
            
            return error_result
            
    async def run_reallocation_flow(self, 
                                  pool_id: str, 
                                  optimization_result: Dict[str, Any]) -> Dict[str, Any]:
        """Run the complete reallocation flow for a vault.
        
        Args:
            pool_id: ID of the vault to reallocate
            optimization_result: Dictionary containing optimization results from optimizer
            
        Returns:
            Dictionary containing reallocation results
        """
        try:
            # 1. Evaluate the portfolio
            evaluation_result = self.evaluate_portfolio(pool_id, optimization_result)
            
            # 2. Check if reallocation is needed
            if not evaluation_result.get('needs_reallocation', False):
                self.logger.info(f"No reallocation needed for vault {pool_id}")
                result = {
                    'pool_id': pool_id,
                    'status': 'success',
                    'reallocation_needed': False,
                    'evaluation_result': evaluation_result,
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
                # Publish no reallocation needed status to ZMQ
                self.publish_zmq_message(
                    topic=f"reallocation.{pool_id}.no_change",
                    message=result
                )
                
                return result
                
            # 3. Process reallocation
            reallocation_actions = evaluation_result.get('reallocation_actions', [])
            if not reallocation_actions:
                self.logger.warning(f"Reallocation needed but no actions specified for vault {pool_id}")
                result = {
                    'pool_id': pool_id,
                    'status': 'warning',
                    'message': "Reallocation needed but no actions specified",
                    'evaluation_result': evaluation_result,
                    'timestamp': pd.Timestamp.now(UTC).isoformat()
                }
                
                # Publish warning status to ZMQ
                self.publish_zmq_message(
                    topic=f"reallocation.{pool_id}.warning",
                    message=result
                )
                
                return result
                
            # 4. Process reallocation
            reallocation_result = await self.process_reallocation(pool_id, reallocation_actions)
            
            # 5. Return complete result
            result = {
                'pool_id': pool_id,
                'status': 'success',
                'reallocation_needed': True,
                'evaluation_result': evaluation_result,
                'reallocation_result': reallocation_result,
                'timestamp': pd.Timestamp.now(UTC).isoformat()
            }
            
            # Note: ZMQ message already sent in process_reallocation
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error running reallocation flow for vault {pool_id}: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            
            error_result = {
                'pool_id': pool_id,
                'status': 'error',
                'message': str(e),
                'timestamp': pd.Timestamp.now(UTC).isoformat()
            }
            
            # Publish error status to ZMQ
            self.publish_zmq_message(
                topic=f"reallocation.{pool_id}.error",
                message=error_result
            )
            
            return error_result 