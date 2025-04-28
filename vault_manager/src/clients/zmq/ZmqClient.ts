import * as zmq from 'zeromq';
import { ZmqConfig, ZmqMessageHandler } from './types';

export class ZmqClient {
  private socket: zmq.Subscriber;
  private messageHandler?: ZmqMessageHandler;
  private address: string;

  constructor(config: ZmqConfig) {
    this.socket = new zmq.Subscriber();
    this.address = config.address;
    this.socket.connect(this.address);
    this.setupMessageHandler();
  }

  private async setupMessageHandler(): Promise<void> {
    for await (const [topic, message] of this.socket) {
      if (this.messageHandler) {
        await this.messageHandler(message.toString());
      }
    }
  }

  subscribe(topic: string): void {
    this.socket.subscribe(topic);
  }

  onMessage(handler: ZmqMessageHandler): void {
    this.messageHandler = handler;
  }

  async close(): Promise<void> {
    await this.socket.disconnect(this.address);
    this.socket.close();
  }
} 