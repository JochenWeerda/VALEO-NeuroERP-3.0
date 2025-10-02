import { Subject, Subscription } from 'rxjs';
import { LogisticsEvent } from '../../core/domain-events/logistics-domain-events';
import { randomUUID } from 'crypto';

export interface LogisticsEventBus {
  publish(event: LogisticsEvent): void;
  subscribe(handler: (event: LogisticsEvent) => void): Subscription;
}

export class InMemoryEventBus implements LogisticsEventBus {
  private readonly subject = new Subject<LogisticsEvent>();

  publish(event: LogisticsEvent): void {
    this.subject.next(event);
  }

  subscribe(handler: (event: LogisticsEvent) => void): Subscription {
    return this.subject.subscribe(handler);
  }
}

export function buildEvent<TType extends LogisticsEvent['eventType'], TPayload extends LogisticsEvent['payload']>(
  eventType: TType,
  tenantId: string,
  payload: TPayload,
  metadata?: Record<string, unknown>,
): LogisticsEvent {
  return {
    eventId: randomUUID(),
    eventType,
    timestamp: new Date().toISOString(),
    tenantId,
    payload,
    metadata,
  } as LogisticsEvent;
}

