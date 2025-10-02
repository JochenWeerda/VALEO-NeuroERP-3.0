import { EventEmitter } from 'events';
export interface DomainEvent {
    eventId: string;
    eventType: string;
    aggregateId: string;
    aggregateType: string;
    eventVersion: number;
    occurredOn: Date;
    eventData: Record<string, any>;
    metadata?: Record<string, any>;
}
export interface EventBus {
    publish(event: DomainEvent): Promise<void>;
    subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void;
    start(): Promise<void>;
    stop(): Promise<void>;
}
export declare enum EventBusType {
    KAFKA = "kafka",
    NATS = "nats",
    RABBITMQ = "rabbitmq",
    IN_MEMORY = "in_memory"
}
export declare class KafkaEventBus implements EventBus {
    private producer?;
    private consumer?;
    private readonly kafka;
    private readonly eventHandlers;
    private readonly metrics;
    constructor();
    start(): Promise<void>;
    publish(event: DomainEvent): Promise<void>;
    subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void;
    stop(): Promise<void>;
}
export declare class NatsEventBus implements EventBus {
    private nc?;
    private readonly sc;
    private readonly eventHandlers;
    private readonly metrics;
    start(): Promise<void>;
    publish(event: DomainEvent): Promise<void>;
    subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void;
    stop(): Promise<void>;
}
export declare class RabbitMQEventBus implements EventBus {
    private connection?;
    private channel?;
    private readonly eventHandlers;
    private readonly metrics;
    start(): Promise<void>;
    publish(event: DomainEvent): Promise<void>;
    subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void;
    stop(): Promise<void>;
}
export declare class InMemoryEventBus extends EventEmitter implements EventBus {
    private readonly eventHandlers;
    private readonly metrics;
    start(): Promise<void>;
    publish(event: DomainEvent): Promise<void>;
    subscribe(eventType: string, handler: (event: DomainEvent) => Promise<void>): void;
    stop(): Promise<void>;
}
export declare class EventBusFactory {
    static createEventBus(type?: EventBusType): EventBus;
}
//# sourceMappingURL=event-bus.d.ts.map