
export interface ZmqConfig {
  address: string;
  options?: Record<string, any>;
}

export interface ZmqMessageHandler {
  (message: string): Promise<void>;
} 