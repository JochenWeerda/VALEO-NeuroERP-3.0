export interface DomainEvent {
  eventId: string;
  eventType: string;
  eventVersion: number;
  occurredAt: string;
  tenantId: string;
  correlationId?: string;
  causationId?: string;
  payload?: any;
}

export interface EventPublisher {
  publish(event: DomainEvent): Promise<void>;
  publishBatch(events: DomainEvent[]): Promise<void>;
  isHealthy(): boolean;
}

export class NoOpEventPublisher implements EventPublisher {
  async publish(event: DomainEvent): Promise<void> {
    console.log(`Publishing event: ${event.eventType}`, event);
  }

  async publishBatch(events: DomainEvent[]): Promise<void> {
    console.log(`Publishing ${events.length} events`);
    for (const event of events) {
      await this.publish(event);
    }
  }

  isHealthy(): boolean {
    return true;
  }
}