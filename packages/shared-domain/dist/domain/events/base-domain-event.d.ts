/**
 * Base Domain Event for VALEO NeuroERP 3.0
 * Foundation for all domain events
 */
import type { EntityId } from '../value-objects/branded-types.js';
export declare abstract class BaseDomainEvent {
    readonly id: string;
    readonly aggregateId: EntityId;
    readonly eventType: string;
    readonly occurredAt: Date;
    readonly version: number;
    readonly causationId?: string;
    readonly correlationId?: string;
    readonly metadata: Record<string, unknown>;
    constructor(aggregateId: EntityId, eventType: string, version?: number, causationId?: string, correlationId?: string, metadata?: Record<string, unknown>);
    private generateEventId;
    getEventData(): Record<string, unknown>;
    toString(): string;
}
//# sourceMappingURL=base-domain-event.d.ts.map