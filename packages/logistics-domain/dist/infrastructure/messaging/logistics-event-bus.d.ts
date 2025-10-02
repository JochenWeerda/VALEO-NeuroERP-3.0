import { Subscription } from 'rxjs';
import { LogisticsEvent } from '../../core/domain-events/logistics-domain-events';
export interface LogisticsEventBus {
    publish(event: LogisticsEvent): void;
    subscribe(handler: (event: LogisticsEvent) => void): Subscription;
}
export declare class InMemoryEventBus implements LogisticsEventBus {
    private readonly subject;
    publish(event: LogisticsEvent): void;
    subscribe(handler: (event: LogisticsEvent) => void): Subscription;
}
export declare function buildEvent<TType extends LogisticsEvent['eventType'], TPayload extends LogisticsEvent['payload']>(eventType: TType, tenantId: string, payload: TPayload, metadata?: Record<string, unknown>): LogisticsEvent;
//# sourceMappingURL=logistics-event-bus.d.ts.map