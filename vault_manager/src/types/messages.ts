export interface ZmqMessage {
  topic: string;
  poolId: string;
  payload: ReallocationPayload;
}

export interface ReallocationPayload {
  actions: ReallocationAction[];
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface ReallocationAction {
  poolId: string;
  poolType: string;
  amount: number;
  type: 'deposit' | 'withdraw';
} 