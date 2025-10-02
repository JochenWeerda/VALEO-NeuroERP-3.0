/**
 * Domain Events Handler for Event-Driven Architecture
 */
import type { IntegrationCreatedEvent, IntegrationUpdatedEvent, IntegrationDeletedEvent } from '@domain/events/integration-events.js';
import type { WebhookCreatedEvent, WebhookTriggeredEvent, WebhookFailedEvent } from '@domain/events/webhook-events.js';
import type { SyncJobCreatedEvent, SyncJobStartedEvent, SyncJobCompletedEvent, SyncJobFailedEvent } from '@domain/events/sync-job-events.js';
import type { BaseDomainEvent } from '@domain/events/base-domain-event.js';
export interface DomainEventHandler<T extends BaseDomainEvent> {
    handle(event: T): Promise<void>;
}
export interface EventBus {
    publish(event: BaseDomainEvent): Promise<void>;
    subscribe<T extends BaseDomainEvent>(eventType: string, handler: DomainEventHandler<T>): void;
    unsubscribe(eventType: string, handler: DomainEventHandler<any>): void;
}
/**
 * In-Memory Event Bus for Testing
 */
export declare class InMemoryEventBus implements EventBus {
    private handlers;
    publish(event: BaseDomainEvent): Promise<void>;
    subscribe<T extends BaseDomainEvent>(eventType: string, handler: DomainEventHandler<T>): void;
    unsubscribe(eventType: string, handler: DomainEventHandler<any>): void;
    clear(): void;
    getHandlerCount(eventType: string): number;
}
/**
 * Integration Event Handlers
 */
export declare class IntegrationCreatedEventHandler implements DomainEventHandler<IntegrationCreatedEvent> {
    handle(event: IntegrationCreatedEvent): Promise<void>;
}
export declare class IntegrationUpdatedEventHandler implements DomainEventHandler<IntegrationUpdatedEvent> {
    handle(event: IntegrationUpdatedEvent): Promise<void>;
}
export declare class IntegrationDeletedEventHandler implements DomainEventHandler<IntegrationDeletedEvent> {
    handle(event: IntegrationDeletedEvent): Promise<void>;
}
/**
 * Webhook Event Handlers
 */
export declare class WebhookCreatedEventHandler implements DomainEventHandler<WebhookCreatedEvent> {
    handle(event: WebhookCreatedEvent): Promise<void>;
}
export declare class WebhookTriggeredEventHandler implements DomainEventHandler<WebhookTriggeredEvent> {
    handle(event: WebhookTriggeredEvent): Promise<void>;
}
export declare class WebhookFailedEventHandler implements DomainEventHandler<WebhookFailedEvent> {
    handle(event: WebhookFailedEvent): Promise<void>;
}
/**
 * Sync Job Event Handlers
 */
export declare class SyncJobCreatedEventHandler implements DomainEventHandler<SyncJobCreatedEvent> {
    handle(event: SyncJobCreatedEvent): Promise<void>;
}
export declare class SyncJobStartedEventHandler implements DomainEventHandler<SyncJobStartedEvent> {
    handle(event: SyncJobStartedEvent): Promise<void>;
}
export declare class SyncJobCompletedEventHandler implements DomainEventHandler<SyncJobCompletedEvent> {
    handle(event: SyncJobCompletedEvent): Promise<void>;
}
export declare class SyncJobFailedEventHandler implements DomainEventHandler<SyncJobFailedEvent> {
    handle(event: SyncJobFailedEvent): Promise<void>;
}
/**
 * Event Handler Registry
 */
export declare class EventHandlerRegistry {
    private eventBus;
    constructor(eventBus: EventBus);
    registerAllHandlers(): void;
    unregisterAllHandlers(): void;
}
/**
 * Event Publisher Service
 */
export declare class EventPublisherService {
    private eventBus;
    constructor(eventBus: EventBus);
    publishDomainEvents(events: BaseDomainEvent[]): Promise<void>;
    publishEvent(event: BaseDomainEvent): Promise<void>;
}
//# sourceMappingURL=domain-events-handler.d.ts.map