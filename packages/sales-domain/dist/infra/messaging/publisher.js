"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.EventPublisher = void 0;
exports.createEventPublisher = createEventPublisher;
exports.getEventPublisher = getEventPublisher;
const nats_1 = require("nats");
class EventPublisher {
    config;
    connection = null;
    stringCodec = (0, nats_1.StringCodec)();
    jsonCodec = (0, nats_1.JSONCodec)();
    isConnected = false;
    reconnectAttempts = 0;
    maxReconnectAttempts = 5;
    reconnectDelayMs = 1000;
    constructor(config) {
        this.config = config;
        this.maxReconnectAttempts = config.maxReconnectAttempts || 5;
        this.reconnectDelayMs = config.reconnectDelayMs || 1000;
    }
    async connect() {
        try {
            this.connection = await (0, nats_1.connect)({
                servers: this.config.natsUrl,
                reconnect: true,
                maxReconnectAttempts: this.maxReconnectAttempts,
                reconnectTimeWait: this.reconnectDelayMs,
            });
            this.isConnected = true;
            this.reconnectAttempts = 0;
            console.log('Sales domain event publisher connected to NATS');
            // Handle connection events
            this.connection.closed().then(() => {
                this.isConnected = false;
                console.log('NATS connection closed');
            });
        }
        catch (error) {
            console.error('Failed to connect to NATS:', error);
            throw error;
        }
    }
    async disconnect() {
        if (this.connection) {
            await this.connection.close();
            this.connection = null;
            this.isConnected = false;
        }
    }
    async publish(event, options = {}) {
        if (!this.isConnected || !this.connection) {
            throw new Error('Event publisher is not connected to NATS');
        }
        try {
            // Add correlation and causation IDs if provided
            const enrichedEvent = {
                ...event,
                correlationId: options.correlationId || event.correlationId,
                causationId: options.causationId || event.causationId,
            };
            // Publish to the specific event type subject
            const subject = event.eventType;
            const payload = this.jsonCodec.encode(enrichedEvent);
            await this.connection.publish(subject, payload);
            console.log(`Published sales event ${event.eventType} with ID ${event.eventId}`);
        }
        catch (error) {
            console.error(`Failed to publish event ${event.eventType}:`, error);
            throw error;
        }
    }
    async publishBatch(events, options = {}) {
        if (!this.isConnected || !this.connection) {
            throw new Error('Event publisher is not connected to NATS');
        }
        try {
            for (const event of events) {
                const enrichedEvent = {
                    ...event,
                    correlationId: options.correlationId || event.correlationId,
                    causationId: options.causationId || event.causationId,
                };
                const subject = event.eventType;
                const payload = this.jsonCodec.encode(enrichedEvent);
                this.connection.publish(subject, payload);
            }
            // Flush to ensure all messages are sent
            await this.connection.flush();
            console.log(`Published batch of ${events.length} sales events`);
        }
        catch (error) {
            console.error('Failed to publish event batch:', error);
            throw error;
        }
    }
    isHealthy() {
        return this.isConnected && this.connection !== null;
    }
    getConnectionStatus() {
        if (!this.connection)
            return 'disconnected';
        return this.isConnected ? 'connected' : 'disconnected';
    }
}
exports.EventPublisher = EventPublisher;
// Factory function to create event publisher
function createEventPublisher(config) {
    return new EventPublisher(config);
}
// Global publisher instance
let globalPublisher = null;
function getEventPublisher() {
    if (globalPublisher === undefined || globalPublisher === null) {
        const natsUrl = process.env.NATS_URL ?? 'nats://localhost:4222';
        globalPublisher = createEventPublisher({ natsUrl });
    }
    return globalPublisher;
}
//# sourceMappingURL=publisher.js.map