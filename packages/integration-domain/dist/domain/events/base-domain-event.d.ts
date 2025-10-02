/**
 * Base Domain Event
 */
import type { Timestamp } from '@shared/types/common.js';
export declare abstract class BaseDomainEvent {
    readonly eventId: string;
    readonly eventType: string;
    readonly aggregateId: string;
    readonly version: number;
    readonly occurredAt: Timestamp;
    readonly metadata: Record<string, unknown>;
    constructor(eventType: string, aggregateId: string, version?: number, metadata?: Record<string, unknown>);
    abstract getData(): Record<string, unknown>;
    toJSON(): Record<string, unknown>;
}
//# sourceMappingURL=base-domain-event.d.ts.map