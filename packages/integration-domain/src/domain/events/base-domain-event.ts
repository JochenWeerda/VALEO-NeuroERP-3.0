/**
 * Base Domain Event
 */

import { generateId } from '@shared/utils/id-generator.js';
import type { Timestamp } from '@shared/types/common.js';

export abstract class BaseDomainEvent {
  public readonly eventId: string;
  public readonly eventType: string;
  public readonly aggregateId: string;
  public readonly version: number;
  public readonly occurredAt: Timestamp;
  public readonly metadata: Record<string, unknown>;

  constructor(
    eventType: string,
    aggregateId: string,
    version = 1,
    metadata: Record<string, unknown> = {}
  ) {
    this.eventId = generateId();
    this.eventType = eventType;
    this.aggregateId = aggregateId;
    this.version = version;
    this.occurredAt = new Date();
    this.metadata = metadata;
  }

  abstract getData(): Record<string, unknown>;

  toJSON(): Record<string, unknown> {
    return {
      eventId: this.eventId,
      eventType: this.eventType,
      aggregateId: this.aggregateId,
      version: this.version,
      occurredAt: this.occurredAt.toISOString(),
      metadata: this.metadata,
      data: this.getData()
    };
  }
}
