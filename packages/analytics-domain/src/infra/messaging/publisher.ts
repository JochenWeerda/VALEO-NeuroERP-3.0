import { connect, type NatsConnection, JSONCodec } from 'nats';
import { type AnyDomainEvent } from '../../domain/events/domain-events';

export interface PublisherConfig {
  natsUrl: string;
  maxReconnectAttempts?: number;
  reconnectDelayMs?: number;
}

export interface PublishOptions {
  correlationId?: string;
  causationId?: string;
}

export class EventPublisher {
  private connection: NatsConnection | null = null;
  private readonly jsonCodec = JSONCodec();
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelayMs = 1000;

  constructor(private readonly config: PublisherConfig) {
    const DEFAULT_MAX_RECONNECT_ATTEMPTS = 5;
    const DEFAULT_RECONNECT_DELAY_MS = 1000;
    this.maxReconnectAttempts = config.maxReconnectAttempts ?? DEFAULT_MAX_RECONNECT_ATTEMPTS;
    this.reconnectDelayMs = config.reconnectDelayMs ?? DEFAULT_RECONNECT_DELAY_MS;
  }

  async connect(): Promise<void> {
    try {
      this.connection = await connect({
        servers: this.config.natsUrl,
        reconnect: true,
        maxReconnectAttempts: this.maxReconnectAttempts,
        reconnectTimeWait: this.reconnectDelayMs,
      });

      this.isConnected = true;
      this.reconnectAttempts = 0;

      // eslint-disable-next-line no-console
      console.log('Analytics domain event publisher connected to NATS');

      // Handle connection events
      this.connection.closed().then(() => {
        this.isConnected = false;
        // eslint-disable-next-line no-console
        console.log('NATS connection closed');
      });

    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to connect to NATS:', error);
      throw error;
    }
  }

  async disconnect(): Promise<void> {
    if (this.connection) {
      await this.connection.close();
      this.connection = null;
      this.isConnected = false;
    }
  }

  async publish(event: AnyDomainEvent, options: PublishOptions = {}): Promise<void> {
    if (!this.isConnected || !this.connection) {
      throw new Error('Event publisher is not connected to NATS');
    }

    try {
      // Add correlation and causation IDs if provided
      const enrichedEvent = {
        ...event,
        correlationId: options.correlationId ?? event.correlationId,
        causationId: options.causationId ?? event.causationId,
      };

      // Publish to the specific event type subject
      const subject = event.eventType;
      const payload = this.jsonCodec.encode(enrichedEvent);

      await this.connection.publish(subject, payload);

      // eslint-disable-next-line no-console
      console.log(`Published analytics event ${event.eventType} with ID ${event.eventId}`);

    } catch (error) {
      // eslint-disable-next-line no-console
      console.error(`Failed to publish event ${event.eventType}:`, error);
      throw error;
    }
  }

  async publishBatch(events: AnyDomainEvent[], options: PublishOptions = {}): Promise<void> {
    if (!this.isConnected || !this.connection) {
      throw new Error('Event publisher is not connected to NATS');
    }

    try {
      for (const event of events) {
        const enrichedEvent = {
          ...event,
          correlationId: options.correlationId ?? event.correlationId,
          causationId: options.causationId ?? event.causationId,
        };

        const subject = event.eventType;
        const payload = this.jsonCodec.encode(enrichedEvent);

        this.connection.publish(subject, payload);
      }

      // Flush to ensure all messages are sent
      await this.connection.flush();

      // eslint-disable-next-line no-console
      console.log(`Published batch of ${events.length} analytics events`);

    } catch (error) {
      // eslint-disable-next-line no-console
      console.error('Failed to publish event batch:', error);
      throw error;
    }
  }

  isHealthy(): boolean {
    return this.isConnected && this.connection !== null;
  }

  getConnectionStatus(): 'connected' | 'disconnected' | 'connecting' {
    if (!this.connection) return 'disconnected';
    return this.isConnected ? 'connected' : 'disconnected';
  }
}

// Factory function to create event publisher
export function createEventPublisher(config: PublisherConfig): EventPublisher {
  return new EventPublisher(config);
}

// Global publisher instance
let globalPublisher: EventPublisher | null = null;

export function getEventPublisher(): EventPublisher {
  if (globalPublisher === null) {
    const natsUrl = process.env.NATS_URL ?? 'nats://localhost:4222';
    globalPublisher = createEventPublisher({ natsUrl });
  }
  return globalPublisher;
}