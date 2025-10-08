/**
 * Base Domain Event for VALEO NeuroERP 3.0
 * Foundation for all domain events
 */

import type { EntityId, AuditId } from '../value-objects/branded-types.js';

export abstract class BaseDomainEvent {
  public readonly id: string;
  public readonly aggregateId: EntityId;
  public readonly eventType: string;
  public readonly occurredAt: Date;
  public readonly version: number;
  public readonly causationId?: string;
  public readonly correlationId?: string;
  public readonly metadata: Record<string, unknown>;

  constructor(
    aggregateId: EntityId,
    eventType: string,
    version: number = 1,
    causationId?: string,
    correlationId?: string,
    metadata: Record<string, unknown> = {}
  ) {
    this.id = this.generateEventId();
    this.aggregateId = aggregateId;
    this.eventType = eventType;
    this.occurredAt = new Date();
    this.version = version;
    this.causationId = causationId;
    this.correlationId = correlationId;
    this.metadata = { ...metadata };
  }

  private generateEventId(): string {
    return `${this.eventType}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  getEventData(): Record<string, unknown> {
    const data: Record<string, unknown> = {};
    
    // Extract all properties except the base event properties
    const baseProperties = ['id', 'aggregateId', 'eventType', 'occurredAt', 'version', 'causationId', 'correlationId', 'metadata'];
    
    for (const [key, value] of Object.entries(this)) {
      if (!baseProperties.includes(key)) {
        data[key] = value;
      }
    }
    
    return data;
  }

  toString(): string {
    return JSON.stringify({
      id: this.id,
      aggregateId: this.aggregateId,
      eventType: this.eventType,
      occurredAt: this.occurredAt.toISOString(),
      version: this.version,
      causationId: this.causationId,
      correlationId: this.correlationId,
      metadata: this.metadata,
      data: this.getEventData()
    });
  }
}


