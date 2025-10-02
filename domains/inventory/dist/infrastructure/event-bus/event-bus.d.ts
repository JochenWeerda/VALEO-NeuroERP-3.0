/**
 * VALEO NeuroERP 3.0 - Inventory Event Bus
 *
 * Event bus implementation for inventory domain events.
 */
export interface DomainEvent {
    type: string;
    occurredAt: Date;
    aggregateId: string;
    aggregateVersion: number;
    tenantId?: string;
    metadata?: Record<string, unknown>;
}
export interface EventBus {
    publish(event: DomainEvent): Promise<void>;
    subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void;
}
export declare class InventoryEventBus implements EventBus {
    private eventHandlers;
    publish(event: DomainEvent): Promise<void>;
    subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void;
}
export type EventBusType = 'in-memory' | 'rabbitmq' | 'kafka';
export declare class EventBusFactory {
    static create(type: EventBusType): EventBus;
    static createEventBus(type: EventBusType): EventBus;
}
//# sourceMappingURL=event-bus.d.ts.map