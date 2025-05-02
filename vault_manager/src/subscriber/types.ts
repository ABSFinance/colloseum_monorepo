import { ZmqMessage as SharedZmqMessage, ReallocationPayload as SharedReallocationPayload } from '../types/messages';
import { ValidationResult as SharedValidationResult } from '../types/vault';

export interface ZmqConfig {
  address: string;
  options?: {
    hwm?: number;
    linger?: number;
    reconnect?: number;
  };
}

// Re-export shared types
export type ZmqMessage = SharedZmqMessage;
export type ReallocationPayload = SharedReallocationPayload;
export type ValidationResult = SharedValidationResult;

export type MessageHandler = (message: ZmqMessage) => Promise<void>; 