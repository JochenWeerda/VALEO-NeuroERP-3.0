/**
 * VALEO NeuroERP 3.0 - Finance Domain - Event Publisher
 *
 * Infrastructure for publishing domain events to message brokers
 * Supporting Kafka, NATS, and RabbitMQ with fallback strategies
 */

import { EventPublisher } from '../../application/services/ledger-service';
export interface DomainEvent {
  type: string;
  occurredAt: Date;
  aggregateId: string;
  payload?: unknown;
  metadata?: Record<string, unknown>;
}

// ===== INTERFACES =====

export interface MessageBrokerConfig {
  type: 'KAFKA' | 'NATS' | 'RABBITMQ';
  connectionString: string;
  topicPrefix?: string;
  retryAttempts?: number;
  retryDelay?: number;
}

export interface EventMetadata {
  eventId: string;
  timestamp: Date;
  source: string;
  version: string;
  tenantId: string;
  correlationId?: string;
  causationId?: string;
}

// ===== EVENT PUBLISHER IMPLEMENTATION =====

export class FinanceEventPublisher implements EventPublisher {
  private readonly config: MessageBrokerConfig;
  private readonly isConnected = false;
  private retryCount = 0;
  private readonly maxRetries: number;

  constructor(config: MessageBrokerConfig) {
    this.config = {
      retryAttempts: 3,
      retryDelay: 1000,
      ...config
    };
    this.maxRetries = this.config.retryAttempts!;
  }

  /**
   * Publish domain event to message broker
   */
  async publish(event: DomainEvent): Promise<void> {
    const correlationId = this.getCorrelationId();
    const eventMetadata: EventMetadata = {
      eventId: crypto.randomUUID(),
      timestamp: new Date(),
      source: 'finance-domain',
      version: '1.0.0',
      tenantId: this.extractTenantId(event),
      causationId: event.aggregateId
    };

    if (correlationId !== undefined) {
      eventMetadata.correlationId = correlationId;
    }

    const message = {
      metadata: eventMetadata,
      event: {
        type: event.type,
        data: event
      }
    };

    try {
      await this.publishToBroker(JSON.stringify(message));
      this.retryCount = 0; // Reset retry count on success
      console.log(`[EVENT PUBLISHED] ${event.type} for aggregate ${event.aggregateId}`);
    } catch (error) {
      console.error(`[EVENT PUBLISH FAILED] ${event.type}:`, error);

      if (this.retryCount < this.maxRetries) {
        this.retryCount++;
        await this.delay(this.config.retryDelay! * this.retryCount);
        return await this.publish(event); // Retry
      }

      throw new Error(`Failed to publish event ${event.type} after ${this.maxRetries} attempts`);
    }
  }

  /**
   * Publish message to configured broker
   */
  private async publishToBroker(message: string): Promise<void> {
    switch (this.config.type) {
      case 'KAFKA':
        await this.publishToKafka(message);
        break;
      case 'NATS':
        await this.publishToNATS(message);
        break;
      case 'RABBITMQ':
        await this.publishToRabbitMQ(message);
        break;
      default:
        throw new Error(`Unsupported broker type: ${this.config.type}`);
    }
  }

  /**
   * Publish to Kafka
   */
  private async publishToKafka(message: string): Promise<void> {
    // Kafka implementation would go here
    // For now, simulate successful publish
    console.log(`[KAFKA] Publishing to topic: ${this.getTopicName()}`);
    await this.simulateNetworkDelay();
  }

  /**
   * Publish to NATS
   */
  private async publishToNATS(message: string): Promise<void> {
    // NATS implementation would go here
    console.log(`[NATS] Publishing to subject: ${this.getTopicName()}`);
    await this.simulateNetworkDelay();
  }

  /**
   * Publish to RabbitMQ
   */
  private async publishToRabbitMQ(message: string): Promise<void> {
    // RabbitMQ implementation would go here
    console.log(`[RABBITMQ] Publishing to exchange: ${this.getTopicName()}`);
    await this.simulateNetworkDelay();
  }

  /**
   * Get topic/exchange/subject name for event
   */
  private getTopicName(): string {
    const topicPrefix = this.config.topicPrefix || 'finance';
    const eventType = (this as any).event?.type || 'unknown';

    // Convert event type to topic format
    // e.g., 'finance.journal.posted' -> 'finance.journal.posted'
    return `${topicPrefix}.${eventType}`;
  }

  /**
   * Extract tenant ID from event
   */
  private extractTenantId(event: DomainEvent): string {
    // Try to extract tenant ID from event data
    if ('tenantId' in event && typeof event.tenantId === 'string') {
      return event.tenantId;
    }

    // Fallback to default tenant
    return 'DEFAULT';
  }

  /**
   * Get correlation ID from context
   */
  private getCorrelationId(): string | undefined {
    // In a real implementation, this would get the correlation ID
    // from the current execution context or HTTP headers
    return undefined;
  }

  /**
   * Simulate network delay for testing
   */
  private async simulateNetworkDelay(): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, 10));
  }

  /**
   * Delay execution
   */
  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ===== OUTBOX PATTERN IMPLEMENTATION =====

export interface OutboxEntry {
  id: string;
  eventType: string;
  eventData: string;
  metadata: EventMetadata;
  status: 'PENDING' | 'PUBLISHED' | 'FAILED';
  createdAt: Date;
  publishedAt?: Date;
  retryCount: number;
}

export class OutboxEventPublisher implements EventPublisher {
  private readonly outboxEntries: OutboxEntry[] = [];
  private readonly publisher: FinanceEventPublisher;
  private isProcessing = false;

  constructor(
    config: MessageBrokerConfig,
    private readonly outboxRepository?: any // Would be a real repository in production
  ) {
    this.publisher = new FinanceEventPublisher(config);
  }

  /**
   * Publish event with outbox pattern
   */
  async publish(event: DomainEvent): Promise<void> {
    const entry: OutboxEntry = {
      id: crypto.randomUUID(),
      eventType: event.type,
      eventData: JSON.stringify(event),
      metadata: {
        eventId: crypto.randomUUID(),
        timestamp: new Date(),
        source: 'finance-domain',
        version: '1.0.0',
        tenantId: this.extractTenantId(event)
      },
      status: 'PENDING',
      createdAt: new Date(),
      retryCount: 0
    };

    // Store in outbox
    this.outboxEntries.push(entry);

    // Process outbox asynchronously
    this.processOutbox();
  }

  /**
   * Process outbox entries
   */
  private async processOutbox(): Promise<void> {
    if (this.isProcessing) return;

    this.isProcessing = true;

    try {
      const pendingEntries = this.outboxEntries.filter(e => e.status === 'PENDING');

      for (const entry of pendingEntries) {
        try {
          const event = JSON.parse(entry.eventData);
          await this.publisher.publish(event);

          entry.status = 'PUBLISHED';
          entry.publishedAt = new Date();
        } catch (error) {
          entry.retryCount++;
          entry.status = entry.retryCount >= 3 ? 'FAILED' : 'PENDING';

          console.error(`[OUTBOX] Failed to publish entry ${entry.id}:`, error);
        }
      }
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * Extract tenant ID from event
   */
  private extractTenantId(event: DomainEvent): string {
    if ('tenantId' in event && typeof event.tenantId === 'string') {
      return event.tenantId;
    }
    return 'DEFAULT';
  }

  /**
   * Get outbox statistics
   */
  getOutboxStats(): { pending: number; published: number; failed: number } {
    const stats = {
      pending: this.outboxEntries.filter(e => e.status === 'PENDING').length,
      published: this.outboxEntries.filter(e => e.status === 'PUBLISHED').length,
      failed: this.outboxEntries.filter(e => e.status === 'FAILED').length
    };

    return stats;
  }
}

// ===== EVENT SUBSCRIBER =====

export interface EventHandler {
  handle(event: DomainEvent): Promise<void>;
  getSubscribedEventTypes(): string[];
}

export class FinanceEventSubscriber {
  private readonly handlers = new Map<string, EventHandler[]>();

  /**
   * Subscribe to event type
   */
  subscribe(eventType: string, handler: EventHandler): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }
    this.handlers.get(eventType)!.push(handler);
  }

  /**
   * Handle incoming event
   */
  async handleEvent(event: DomainEvent): Promise<void> {
    const handlers = this.handlers.get(event.type) || [];

    await Promise.all(
      handlers.map(handler => handler.handle(event))
    );
  }

  /**
   * Get subscription statistics
   */
  getSubscriptionStats(): Record<string, number> {
    const stats: Record<string, number> = {};

    for (const [eventType, handlers] of this.handlers.entries()) {
      stats[eventType] = handlers.length;
    }

    return stats;
  }
}

// ===== FACTORY FUNCTIONS =====

export function createEventPublisher(config: MessageBrokerConfig): EventPublisher {
  return new FinanceEventPublisher(config);
}

export function createOutboxEventPublisher(
  config: MessageBrokerConfig,
  outboxRepository?: any
): EventPublisher {
  return new OutboxEventPublisher(config, outboxRepository);
}

export function createEventSubscriber(): FinanceEventSubscriber {
  return new FinanceEventSubscriber();
}

// ===== MESSAGE BROKER CLIENTS =====

export class KafkaClient {
  constructor(private readonly config: MessageBrokerConfig) {}

  async publish(topic: string, message: string): Promise<void> {
    // Kafka client implementation would go here
    console.log(`[KAFKA CLIENT] Publishing to ${topic}: ${message.length} bytes`);
  }

  async subscribe(topic: string, handler: (message: string) => void): Promise<void> {
    // Kafka consumer implementation would go here
    console.log(`[KAFKA CLIENT] Subscribed to ${topic}`);
  }
}

export class NATSClient {
  constructor(private readonly config: MessageBrokerConfig) {}

  async publish(subject: string, message: string): Promise<void> {
    // NATS client implementation would go here
    console.log(`[NATS CLIENT] Publishing to ${subject}: ${message.length} bytes`);
  }

  async subscribe(subject: string, handler: (message: string) => void): Promise<void> {
    // NATS subscriber implementation would go here
    console.log(`[NATS CLIENT] Subscribed to ${subject}`);
  }
}

export class RabbitMQClient {
  constructor(private readonly config: MessageBrokerConfig) {}

  async publish(exchange: string, message: string): Promise<void> {
    // RabbitMQ client implementation would go here
    console.log(`[RABBITMQ CLIENT] Publishing to ${exchange}: ${message.length} bytes`);
  }

  async subscribe(queue: string, handler: (message: string) => void): Promise<void> {
    // RabbitMQ consumer implementation would go here
    console.log(`[RABBITMQ CLIENT] Subscribed to ${queue}`);
  }
}