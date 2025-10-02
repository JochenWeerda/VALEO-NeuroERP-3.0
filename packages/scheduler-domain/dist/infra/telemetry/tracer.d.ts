import { Span } from '@opentelemetry/api';
export interface TracingConfig {
    serviceName: string;
    serviceVersion: string;
    enabled?: boolean;
}
export declare class TracingService {
    private config;
    private tracer;
    constructor(config: TracingConfig);
    initialize(): Promise<void>;
    shutdown(): Promise<void>;
    startSpan(name: string, options?: {
        attributes?: Record<string, string | number | boolean>;
    }): Span;
    startActiveSpan<T>(name: string, fn: (span: Span) => Promise<T>, options?: {
        attributes?: Record<string, string | number | boolean>;
    }): Promise<T>;
    traceScheduleExecution(scheduleId: string, operation: string): Span;
    traceDatabaseOperation(operation: string, table: string): Span;
    traceHttpRequest(method: string, url: string): Span;
    traceEventPublishing(eventType: string, topic?: string): Span;
}
export declare function getTracingService(): TracingService;
export declare function initializeTracing(): Promise<void>;
export declare function shutdownTracing(): Promise<void>;
//# sourceMappingURL=tracer.d.ts.map