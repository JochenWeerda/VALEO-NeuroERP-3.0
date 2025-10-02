"use strict";
/**
 * VALEO NeuroERP 3.0 - Finance Domain - Event Publisher
 *
 * Infrastructure for publishing domain events to message brokers
 * Supporting Kafka, NATS, and RabbitMQ with fallback strategies
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.RabbitMQClient = exports.NATSClient = exports.KafkaClient = exports.FinanceEventSubscriber = exports.OutboxEventPublisher = exports.FinanceEventPublisher = void 0;
exports.createEventPublisher = createEventPublisher;
exports.createOutboxEventPublisher = createOutboxEventPublisher;
exports.createEventSubscriber = createEventSubscriber;
// ===== EVENT PUBLISHER IMPLEMENTATION =====
class FinanceEventPublisher {
    config;
    isConnected = false;
    retryCount = 0;
    maxRetries;
    constructor(config) {
        this.config = {
            retryAttempts: 3,
            retryDelay: 1000,
            ...config
        };
        this.maxRetries = this.config.retryAttempts;
    }
    /**
     * Publish domain event to message broker
     */
    async publish(event) {
        const correlationId = this.getCorrelationId();
        const eventMetadata = {
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
        }
        catch (error) {
            console.error(`[EVENT PUBLISH FAILED] ${event.type}:`, error);
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                await this.delay(this.config.retryDelay * this.retryCount);
                return await this.publish(event); // Retry
            }
            throw new Error(`Failed to publish event ${event.type} after ${this.maxRetries} attempts`);
        }
    }
    /**
     * Publish message to configured broker
     */
    async publishToBroker(message) {
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
    async publishToKafka(message) {
        // Kafka implementation would go here
        // For now, simulate successful publish
        console.log(`[KAFKA] Publishing to topic: ${this.getTopicName()}`);
        await this.simulateNetworkDelay();
    }
    /**
     * Publish to NATS
     */
    async publishToNATS(message) {
        // NATS implementation would go here
        console.log(`[NATS] Publishing to subject: ${this.getTopicName()}`);
        await this.simulateNetworkDelay();
    }
    /**
     * Publish to RabbitMQ
     */
    async publishToRabbitMQ(message) {
        // RabbitMQ implementation would go here
        console.log(`[RABBITMQ] Publishing to exchange: ${this.getTopicName()}`);
        await this.simulateNetworkDelay();
    }
    /**
     * Get topic/exchange/subject name for event
     */
    getTopicName() {
        const topicPrefix = this.config.topicPrefix || 'finance';
        const eventType = this.event?.type || 'unknown';
        // Convert event type to topic format
        // e.g., 'finance.journal.posted' -> 'finance.journal.posted'
        return `${topicPrefix}.${eventType}`;
    }
    /**
     * Extract tenant ID from event
     */
    extractTenantId(event) {
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
    getCorrelationId() {
        // In a real implementation, this would get the correlation ID
        // from the current execution context or HTTP headers
        return undefined;
    }
    /**
     * Simulate network delay for testing
     */
    async simulateNetworkDelay() {
        return new Promise(resolve => setTimeout(resolve, 10));
    }
    /**
     * Delay execution
     */
    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
exports.FinanceEventPublisher = FinanceEventPublisher;
class OutboxEventPublisher {
    outboxRepository;
    outboxEntries = [];
    publisher;
    isProcessing = false;
    constructor(config, outboxRepository // Would be a real repository in production
    ) {
        this.outboxRepository = outboxRepository;
        this.publisher = new FinanceEventPublisher(config);
    }
    /**
     * Publish event with outbox pattern
     */
    async publish(event) {
        const entry = {
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
    async processOutbox() {
        if (this.isProcessing)
            return;
        this.isProcessing = true;
        try {
            const pendingEntries = this.outboxEntries.filter(e => e.status === 'PENDING');
            for (const entry of pendingEntries) {
                try {
                    const event = JSON.parse(entry.eventData);
                    await this.publisher.publish(event);
                    entry.status = 'PUBLISHED';
                    entry.publishedAt = new Date();
                }
                catch (error) {
                    entry.retryCount++;
                    entry.status = entry.retryCount >= 3 ? 'FAILED' : 'PENDING';
                    console.error(`[OUTBOX] Failed to publish entry ${entry.id}:`, error);
                }
            }
        }
        finally {
            this.isProcessing = false;
        }
    }
    /**
     * Extract tenant ID from event
     */
    extractTenantId(event) {
        if ('tenantId' in event && typeof event.tenantId === 'string') {
            return event.tenantId;
        }
        return 'DEFAULT';
    }
    /**
     * Get outbox statistics
     */
    getOutboxStats() {
        const stats = {
            pending: this.outboxEntries.filter(e => e.status === 'PENDING').length,
            published: this.outboxEntries.filter(e => e.status === 'PUBLISHED').length,
            failed: this.outboxEntries.filter(e => e.status === 'FAILED').length
        };
        return stats;
    }
}
exports.OutboxEventPublisher = OutboxEventPublisher;
class FinanceEventSubscriber {
    handlers = new Map();
    /**
     * Subscribe to event type
     */
    subscribe(eventType, handler) {
        if (!this.handlers.has(eventType)) {
            this.handlers.set(eventType, []);
        }
        this.handlers.get(eventType).push(handler);
    }
    /**
     * Handle incoming event
     */
    async handleEvent(event) {
        const handlers = this.handlers.get(event.type) || [];
        await Promise.all(handlers.map(handler => handler.handle(event)));
    }
    /**
     * Get subscription statistics
     */
    getSubscriptionStats() {
        const stats = {};
        for (const [eventType, handlers] of this.handlers.entries()) {
            stats[eventType] = handlers.length;
        }
        return stats;
    }
}
exports.FinanceEventSubscriber = FinanceEventSubscriber;
// ===== FACTORY FUNCTIONS =====
function createEventPublisher(config) {
    return new FinanceEventPublisher(config);
}
function createOutboxEventPublisher(config, outboxRepository) {
    return new OutboxEventPublisher(config, outboxRepository);
}
function createEventSubscriber() {
    return new FinanceEventSubscriber();
}
// ===== MESSAGE BROKER CLIENTS =====
class KafkaClient {
    config;
    constructor(config) {
        this.config = config;
    }
    async publish(topic, message) {
        // Kafka client implementation would go here
        console.log(`[KAFKA CLIENT] Publishing to ${topic}: ${message.length} bytes`);
    }
    async subscribe(topic, handler) {
        // Kafka consumer implementation would go here
        console.log(`[KAFKA CLIENT] Subscribed to ${topic}`);
    }
}
exports.KafkaClient = KafkaClient;
class NATSClient {
    config;
    constructor(config) {
        this.config = config;
    }
    async publish(subject, message) {
        // NATS client implementation would go here
        console.log(`[NATS CLIENT] Publishing to ${subject}: ${message.length} bytes`);
    }
    async subscribe(subject, handler) {
        // NATS subscriber implementation would go here
        console.log(`[NATS CLIENT] Subscribed to ${subject}`);
    }
}
exports.NATSClient = NATSClient;
class RabbitMQClient {
    config;
    constructor(config) {
        this.config = config;
    }
    async publish(exchange, message) {
        // RabbitMQ client implementation would go here
        console.log(`[RABBITMQ CLIENT] Publishing to ${exchange}: ${message.length} bytes`);
    }
    async subscribe(queue, handler) {
        // RabbitMQ consumer implementation would go here
        console.log(`[RABBITMQ CLIENT] Subscribed to ${queue}`);
    }
}
exports.RabbitMQClient = RabbitMQClient;
