import { Socket } from 'zmq';

export interface ZmqConfig {
  address: string;
  options?: Socket.Options;
}

export interface ZmqMessageHandler {
  (message: string): Promise<void>;
} 