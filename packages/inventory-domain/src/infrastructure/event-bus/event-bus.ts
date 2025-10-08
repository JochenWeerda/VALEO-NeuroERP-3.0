/**
 * VALEO NeuroERP 3.0 - Inventory Event Bus
 *
 * Event bus implementation for inventory domain events.
 */

// import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';

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

export class InventoryEventBus implements EventBus {
  private readonly eventHandlers = new Map<string, ((event: DomainEvent) => Promise<void>)[]>();

  async publish(event: DomainEvent): Promise<void> {
    const handlers = this.eventHandlers.get(event.type) || [];
    await Promise.all(handlers.map(handler => handler(event)));
  }

  subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void {
    if (!this.eventHandlers.has(eventType)) {
      this.eventHandlers.set(eventType, []);
    }
    this.eventHandlers.get(eventType).push(handler);
  }
}

export type EventBusType = 'in-memory' | 'rabbitmq' | 'kafka';

export class EventBusFactory {
  static create(type: EventBusType): EventBus {
    switch (type) {
      case 'in-memory':
        return new InventoryEventBus();
      default:
        return new InventoryEventBus();
    }
  }

  static createEventBus(type: EventBusType): EventBus {
    return this.create(type);
  }
}