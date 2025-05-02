import { ZmqConfig, ZmqMessage, MessageHandler } from './types';
import * as zmq from 'zeromq';

export class ZmqSubscriber {
  private socket: zmq.Subscriber;
  private messageHandler: MessageHandler | null = null;
  private isConnected: boolean = false;

  constructor(private config: ZmqConfig) {
    this.socket = new zmq.Subscriber();
    this.setupSocket();
  }

  private setupSocket(): void {
    this.socket.connect(this.config.address);
    this.isConnected = true;
  }

  public subscribe(topic: string): void {
    if (!this.isConnected) {
      throw new Error('Socket is not connected');
    }
    this.socket.subscribe(topic);
  }

  public unsubscribe(topic: string): void {
    if (!this.isConnected) {
      throw new Error('Socket is not connected');
    }
    this.socket.unsubscribe(topic);
  }

  public onMessage(handler: MessageHandler): void {
    this.messageHandler = handler;
    this.startListening();
  }

  private async startListening(): Promise<void> {
    if (!this.messageHandler) {
      throw new Error('No message handler registered');
    }

    for await (const [topic, message] of this.socket) {
      try {
        const parsedMessage = this.parseMessage(topic.toString(), message);
        await this.messageHandler(parsedMessage);
      } catch (error: unknown) {
        if (error instanceof Error) {
          console.error('Error processing message:', error.message);
        } else {
          console.error('Unknown error processing message');
        }
      }
    }
  }

  private parseMessage(topic: string, message: Buffer): ZmqMessage {
    try {
      const payload = JSON.parse(message.toString());
      const poolId = topic.split('.')[1]; // Extract poolId from topic format: reallocation.{poolId}.{status}
      
      return {
        topic,
        poolId,
        payload
      };
    } catch (error: unknown) {
      if (error instanceof Error) {
        throw new Error(`Failed to parse message: ${error.message}`);
      }
      throw new Error('Failed to parse message: Unknown error');
    }
  }

  public async close(): Promise<void> {
    if (this.isConnected) {
      this.socket.close();
      this.isConnected = false;
    }
  }
} 