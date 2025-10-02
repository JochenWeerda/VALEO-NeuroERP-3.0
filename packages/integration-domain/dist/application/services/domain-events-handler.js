/**
 * Domain Events Handler for Event-Driven Architecture
 */
/**
 * In-Memory Event Bus for Testing
 */
export class InMemoryEventBus {
    handlers = new Map();
    async publish(event) {
        const eventHandlers = this.handlers.get(event.eventType);
        if (!eventHandlers) {
            console.log(`No handlers registered for event type: ${event.eventType}`);
            return;
        }
        console.log(`Publishing event: ${event.eventType}`, event.toJSON());
        // Execute all handlers for this event type
        const promises = Array.from(eventHandlers).map(handler => handler.handle(event).catch(error => {
            console.error(`Error handling event ${event.eventType}:`, error);
        }));
        await Promise.allSettled(promises);
    }
    subscribe(eventType, handler) {
        if (!this.handlers.has(eventType)) {
            this.handlers.set(eventType, new Set());
        }
        this.handlers.get(eventType).add(handler);
    }
    unsubscribe(eventType, handler) {
        const eventHandlers = this.handlers.get(eventType);
        if (eventHandlers) {
            eventHandlers.delete(handler);
            if (eventHandlers.size === 0) {
                this.handlers.delete(eventType);
            }
        }
    }
    clear() {
        this.handlers.clear();
    }
    getHandlerCount(eventType) {
        return this.handlers.get(eventType)?.size || 0;
    }
}
/**
 * Integration Event Handlers
 */
export class IntegrationCreatedEventHandler {
    async handle(event) {
        console.log(`Integration created: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Send notifications
        // - Update search indexes
        // - Trigger other domain events
        // - Log to audit system
    }
}
export class IntegrationUpdatedEventHandler {
    async handle(event) {
        console.log(`Integration updated: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Update search indexes
        // - Invalidate caches
        // - Send notifications about changes
        // - Log to audit system
    }
}
export class IntegrationDeletedEventHandler {
    async handle(event) {
        console.log(`Integration deleted: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Clean up related data
        // - Remove from search indexes
        // - Send notifications
        // - Log to audit system
    }
}
/**
 * Webhook Event Handlers
 */
export class WebhookCreatedEventHandler {
    async handle(event) {
        console.log(`Webhook created: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Register webhook with external systems
        // - Set up monitoring
        // - Update webhook registry
    }
}
export class WebhookTriggeredEventHandler {
    async handle(event) {
        console.log(`Webhook triggered: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Update webhook statistics
        // - Send monitoring metrics
        // - Log webhook execution
    }
}
export class WebhookFailedEventHandler {
    async handle(event) {
        console.log(`Webhook failed: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Send alerts
        // - Update failure statistics
        // - Trigger retry logic
        // - Log error details
    }
}
/**
 * Sync Job Event Handlers
 */
export class SyncJobCreatedEventHandler {
    async handle(event) {
        console.log(`Sync job created: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Schedule the job
        // - Set up monitoring
        // - Update job registry
    }
}
export class SyncJobStartedEventHandler {
    async handle(event) {
        console.log(`Sync job started: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Update job status in external systems
        // - Send monitoring metrics
        // - Log job start
    }
}
export class SyncJobCompletedEventHandler {
    async handle(event) {
        console.log(`Sync job completed: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Update job statistics
        // - Send success notifications
        // - Schedule next run if applicable
        // - Update monitoring dashboards
    }
}
export class SyncJobFailedEventHandler {
    async handle(event) {
        console.log(`Sync job failed: ${event.aggregateId}`, event.getData());
        // In a real implementation, you might:
        // - Send alerts
        // - Update failure statistics
        // - Trigger retry logic
        // - Log error details
    }
}
/**
 * Event Handler Registry
 */
export class EventHandlerRegistry {
    eventBus;
    constructor(eventBus) {
        this.eventBus = eventBus;
    }
    registerAllHandlers() {
        // Register integration event handlers
        this.eventBus.subscribe('integration.created', new IntegrationCreatedEventHandler());
        this.eventBus.subscribe('integration.updated', new IntegrationUpdatedEventHandler());
        this.eventBus.subscribe('integration.deleted', new IntegrationDeletedEventHandler());
        // Register webhook event handlers
        this.eventBus.subscribe('webhook.created', new WebhookCreatedEventHandler());
        this.eventBus.subscribe('webhook.triggered', new WebhookTriggeredEventHandler());
        this.eventBus.subscribe('webhook.failed', new WebhookFailedEventHandler());
        // Register sync job event handlers
        this.eventBus.subscribe('syncjob.created', new SyncJobCreatedEventHandler());
        this.eventBus.subscribe('syncjob.started', new SyncJobStartedEventHandler());
        this.eventBus.subscribe('syncjob.completed', new SyncJobCompletedEventHandler());
        this.eventBus.subscribe('syncjob.failed', new SyncJobFailedEventHandler());
        console.log('All domain event handlers registered');
    }
    unregisterAllHandlers() {
        // Note: In a real implementation, you would need to keep references to handlers
        // to properly unsubscribe them. For simplicity, we'll clear the entire event bus.
        if (this.eventBus instanceof InMemoryEventBus) {
            this.eventBus.clear();
        }
    }
}
/**
 * Event Publisher Service
 */
export class EventPublisherService {
    eventBus;
    constructor(eventBus) {
        this.eventBus = eventBus;
    }
    async publishDomainEvents(events) {
        const promises = events.map(event => this.eventBus.publish(event));
        await Promise.allSettled(promises);
    }
    async publishEvent(event) {
        await this.eventBus.publish(event);
    }
}
//# sourceMappingURL=domain-events-handler.js.map