export interface EventConsumerConfig {
    natsUrl: string;
    databaseUrl: string;
    maxReconnectAttempts?: number;
    reconnectDelayMs?: number;
}
export interface BusinessEvent {
    eventId: string;
    eventType: string;
    occurredAt: string;
    tenantId: string;
    correlationId?: string;
    causationId?: string;
    payload: any;
}
export declare class EventConsumer {
    private config;
    private connection;
    private subscription;
    private db;
    private pool;
    private isConnected;
    private isProcessing;
    private reconnectAttempts;
    private maxReconnectAttempts;
    private reconnectDelayMs;
    constructor(config: EventConsumerConfig);
    connect(): Promise<void>;
    startConsuming(): Promise<void>;
    private handleEvent;
    private processEvent;
    private processContractEvent;
    private processProductionEvent;
    private processWeighingEvent;
    private processQualityEvent;
    private processRegulatoryEvent;
    private processFinanceEvent;
    private mapEventTypeToFinanceType;
    disconnect(): Promise<void>;
    isHealthy(): boolean;
    getConnectionStatus(): 'connected' | 'disconnected' | 'connecting';
}
export declare function createEventConsumer(config: EventConsumerConfig): EventConsumer;
export declare function getEventConsumer(): EventConsumer;
//# sourceMappingURL=event-consumer.d.ts.map