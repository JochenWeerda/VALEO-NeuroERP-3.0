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
export declare class FinanceEventPublisher implements EventPublisher {
    private readonly config;
    private readonly isConnected;
    private retryCount;
    private readonly maxRetries;
    constructor(config: MessageBrokerConfig);
    /**
     * Publish domain event to message broker
     */
    publish(event: DomainEvent): Promise<void>;
    /**
     * Publish message to configured broker
     */
    private publishToBroker;
    /**
     * Publish to Kafka
     */
    private publishToKafka;
    /**
     * Publish to NATS
     */
    private publishToNATS;
    /**
     * Publish to RabbitMQ
     */
    private publishToRabbitMQ;
    /**
     * Get topic/exchange/subject name for event
     */
    private getTopicName;
    /**
     * Extract tenant ID from event
     */
    private extractTenantId;
    /**
     * Get correlation ID from context
     */
    private getCorrelationId;
    /**
     * Simulate network delay for testing
     */
    private simulateNetworkDelay;
    /**
     * Delay execution
     */
    private delay;
}
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
export declare class OutboxEventPublisher implements EventPublisher {
    private readonly outboxRepository?;
    private readonly outboxEntries;
    private readonly publisher;
    private isProcessing;
    constructor(config: MessageBrokerConfig, outboxRepository?: any | undefined);
    /**
     * Publish event with outbox pattern
     */
    publish(event: DomainEvent): Promise<void>;
    /**
     * Process outbox entries
     */
    private processOutbox;
    /**
     * Extract tenant ID from event
     */
    private extractTenantId;
    /**
     * Get outbox statistics
     */
    getOutboxStats(): {
        pending: number;
        published: number;
        failed: number;
    };
}
export interface EventHandler {
    handle(event: DomainEvent): Promise<void>;
    getSubscribedEventTypes(): string[];
}
export declare class FinanceEventSubscriber {
    private readonly handlers;
    /**
     * Subscribe to event type
     */
    subscribe(eventType: string, handler: EventHandler): void;
    /**
     * Handle incoming event
     */
    handleEvent(event: DomainEvent): Promise<void>;
    /**
     * Get subscription statistics
     */
    getSubscriptionStats(): Record<string, number>;
}
export declare function createEventPublisher(config: MessageBrokerConfig): EventPublisher;
export declare function createOutboxEventPublisher(config: MessageBrokerConfig, outboxRepository?: any): EventPublisher;
export declare function createEventSubscriber(): FinanceEventSubscriber;
export declare class KafkaClient {
    private readonly config;
    constructor(config: MessageBrokerConfig);
    publish(topic: string, message: string): Promise<void>;
    subscribe(topic: string, handler: (message: string) => void): Promise<void>;
}
export declare class NATSClient {
    private readonly config;
    constructor(config: MessageBrokerConfig);
    publish(subject: string, message: string): Promise<void>;
    subscribe(subject: string, handler: (message: string) => void): Promise<void>;
}
export declare class RabbitMQClient {
    private readonly config;
    constructor(config: MessageBrokerConfig);
    publish(exchange: string, message: string): Promise<void>;
    subscribe(queue: string, handler: (message: string) => void): Promise<void>;
}
//# sourceMappingURL=event-publisher.d.ts.map