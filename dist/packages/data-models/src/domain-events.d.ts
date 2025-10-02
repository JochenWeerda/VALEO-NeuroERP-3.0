export interface DomainEvent {
    type: string;
    occurredAt: Date;
    payload?: unknown;
    metadata?: Record<string, unknown>;
}
//***REMOVED*** sourceMappingURL=domain-events.d.ts.map