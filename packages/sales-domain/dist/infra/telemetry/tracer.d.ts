import { Span, Tracer } from '@opentelemetry/api';
export declare function getTracer(): Tracer;
export declare function createSpan(name: string, attributes?: Record<string, string | number | boolean>): Span;
export declare function setupTelemetry(): void;
export declare function tracingMiddleware(): {
    onRequest: (request: any, reply: any, done: () => void) => void;
    onResponse: (request: any, reply: any, done: () => void) => void;
    onError: (request: any, reply: any, error: any, done: () => void) => void;
};
//# sourceMappingURL=tracer.d.ts.map