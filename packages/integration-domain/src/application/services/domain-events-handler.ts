/**
 * Domain Events Handler for Event-Driven Architecture
 */

import type { 
  IntegrationCreatedEvent,
  IntegrationDeletedEvent,
  IntegrationUpdatedEvent
} from '@domain/events/integration-events.js';
import type {
  WebhookCreatedEvent,
  WebhookFailedEvent,
  WebhookTriggeredEvent
} from '@domain/events/webhook-events.js';
import type {
  SyncJobCompletedEvent,
  SyncJobCreatedEvent,
  SyncJobFailedEvent,
  SyncJobStartedEvent
} from '@domain/events/sync-job-events.js';
import type { BaseDomainEvent } from '@domain/events/base-domain-event.js';

export interface DomainEventHandler<T extends BaseDomainEvent> {
  handle(event: T): Promise<void>;
}

export interface EventBus {
  publish(event: BaseDomainEvent): Promise<void>;
  subscribe<T extends BaseDomainEvent>(
    eventType: string,
    handler: DomainEventHandler<T>
  ): void;
  unsubscribe(eventType: string, handler: DomainEventHandler<any>): void;
}

/**
 * In-Memory Event Bus for Testing
 */
export class InMemoryEventBus implements EventBus {
  private handlers = new Map<string, Set<DomainEventHandler<any>>>();

  async publish(event: BaseDomainEvent): Promise<void> {
    const eventHandlers = this.handlers.get(event.eventType);
    if (!eventHandlers) {
      console.log(`No handlers registered for event type: ${event.eventType}`);
      return;
    }

    console.log(`Publishing event: ${event.eventType}`, event.toJSON());

    // Execute all handlers for this event type
    const promises = Array.from(eventHandlers).map(handler => 
      handler.handle(event).catch(error => {
        console.error(`Error handling event ${event.eventType}:`, error);
      })
    );

    await Promise.allSettled(promises);
  }

  subscribe<T extends BaseDomainEvent>(
    eventType: string,
    handler: DomainEventHandler<T>
  ): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler);
  }

  unsubscribe(eventType: string, handler: DomainEventHandler<any>): void {
    const eventHandlers = this.handlers.get(eventType);
    if (eventHandlers) {
      eventHandlers.delete(handler);
      if (eventHandlers.size === 0) {
        this.handlers.delete(eventType);
      }
    }
  }

  clear(): void {
    this.handlers.clear();
  }

  getHandlerCount(eventType: string): number {
    return this.handlers.get(eventType)?.size || 0;
  }
}

/**
 * Integration Event Handlers
 */
export class IntegrationCreatedEventHandler implements DomainEventHandler<IntegrationCreatedEvent> {
  async handle(event: IntegrationCreatedEvent): Promise<void> {
    console.log(`Integration created: ${event.aggregateId}`, event.getData());
    
    // In a real implementation, you might:
    // - Send notifications
    // - Update search indexes
    // - Trigger other domain events
    // - Log to audit system
  }
}

export class IntegrationUpdatedEventHandler implements DomainEventHandler<IntegrationUpdatedEvent> {
  async handle(event: IntegrationUpdatedEvent): Promise<void> {
    console.log(`Integration updated: ${event.aggregateId}`, event.getData());
    
    // In a real implementation, you might:
    // - Update search indexes
    // - Invalidate caches
    // - Send notifications about changes
    // - Log to audit system
  }
}

export class IntegrationDeletedEventHandler implements DomainEventHandler<IntegrationDeletedEvent> {
  async handle(event: IntegrationDeletedEvent): Promise<void> {
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
export class WebhookCreatedEventHandler implements DomainEventHandler<WebhookCreatedEvent> {
  async handle(event: WebhookCreatedEvent): Promise<void> {
    console.log(`Webhook created: ${event.aggregateId}`, event.getData());
    
    // In a real implementation, you might:
    // - Register webhook with external systems
    // - Set up monitoring
    // - Update webhook registry
  }
}

export class WebhookTriggeredEventHandler implements DomainEventHandler<WebhookTriggeredEvent> {
  async handle(event: WebhookTriggeredEvent): Promise<void> {
    console.log(`Webhook triggered: ${event.aggregateId}`, event.getData());
    
    // In a real implementation, you might:
    // - Update webhook statistics
    // - Send monitoring metrics
    // - Log webhook execution
  }
}

export class WebhookFailedEventHandler implements DomainEventHandler<WebhookFailedEvent> {
  async handle(event: WebhookFailedEvent): Promise<void> {
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
export class SyncJobCreatedEventHandler implements DomainEventHandler<SyncJobCreatedEvent> {
  async handle(event: SyncJobCreatedEvent): Promise<void> {
    console.log(`Sync job created: ${event.aggregateId}`, event.getData());
    
    // In a real implementation, you might:
    // - Schedule the job
    // - Set up monitoring
    // - Update job registry
  }
}

export class SyncJobStartedEventHandler implements DomainEventHandler<SyncJobStartedEvent> {
  async handle(event: SyncJobStartedEvent): Promise<void> {
    console.log(`Sync job started: ${event.aggregateId}`, event.getData());
    
    // In a real implementation, you might:
    // - Update job status in external systems
    // - Send monitoring metrics
    // - Log job start
  }
}

export class SyncJobCompletedEventHandler implements DomainEventHandler<SyncJobCompletedEvent> {
  async handle(event: SyncJobCompletedEvent): Promise<void> {
    console.log(`Sync job completed: ${event.aggregateId}`, event.getData());
    
    // In a real implementation, you might:
    // - Update job statistics
    // - Send success notifications
    // - Schedule next run if applicable
    // - Update monitoring dashboards
  }
}

export class SyncJobFailedEventHandler implements DomainEventHandler<SyncJobFailedEvent> {
  async handle(event: SyncJobFailedEvent): Promise<void> {
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
  constructor(private readonly eventBus: EventBus) {}

  registerAllHandlers(): void {
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

  unregisterAllHandlers(): void {
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
  constructor(private readonly eventBus: EventBus) {}

  async publishDomainEvents(events: BaseDomainEvent[]): Promise<void> {
    const promises = events.map(event => this.eventBus.publish(event));
    await Promise.allSettled(promises);
  }

  async publishEvent(event: BaseDomainEvent): Promise<void> {
    await this.eventBus.publish(event);
  }
}
