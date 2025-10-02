import { AnyDomainEvent } from '../../domain/events/domain-events';
export interface PublisherConfig {
    natsUrl: string;
    maxReconnectAttempts?: number;
    reconnectDelayMs?: number;
}
export interface PublishOptions {
    correlationId?: string;
    causationId?: string;
}
export declare class EventPublisher {
    private config;
    private connection;
    private stringCodec;
    private jsonCodec;
    private isConnected;
    private reconnectAttempts;
    private maxReconnectAttempts;
    private reconnectDelayMs;
    constructor(config: PublisherConfig);
    connect(): Promise<void>;
    disconnect(): Promise<void>;
    publish(event: AnyDomainEvent, options?: PublishOptions): Promise<void>;
    publishBatch(events: AnyDomainEvent[], options?: PublishOptions): Promise<void>;
    isHealthy(): boolean;
    getConnectionStatus(): 'connected' | 'disconnected' | 'connecting';
}
export declare function createEventPublisher(config: PublisherConfig): EventPublisher;
export declare function getEventPublisher(): EventPublisher;
//# sourceMappingURL=publisher.d.ts.map