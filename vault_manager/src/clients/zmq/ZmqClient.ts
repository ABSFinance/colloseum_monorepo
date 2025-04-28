import { Socket } from 'zmq';
import { ZmqConfig, ZmqMessageHandler } from './types';

export class ZmqClient {
  private socket: Socket;
  private messageHandler?: ZmqMessageHandler;

  constructor(config: ZmqConfig) {
    this.socket = new Socket('sub');
    this.socket.connect(config.address);
    this.setupMessageHandler();
  }

  private setupMessageHandler(): void {
    this.socket.on('message', async (message: string) => {
      if (this.messageHandler) {
        await this.messageHandler(message);
      }
    });
  }

  subscribe(topic: string): void {
    this.socket.subscribe(topic);
  }

  onMessage(handler: ZmqMessageHandler): void {
    this.messageHandler = handler;
  }

  async close(): Promise<void> {
    this.socket.close();
  }
} 