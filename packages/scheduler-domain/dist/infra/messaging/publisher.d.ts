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
export declare class NoOpEventPublisher implements EventPublisher {
    publish(event: DomainEvent): Promise<void>;
    publishBatch(events: DomainEvent[]): Promise<void>;
    isHealthy(): boolean;
}
//# sourceMappingURL=publisher.d.ts.map