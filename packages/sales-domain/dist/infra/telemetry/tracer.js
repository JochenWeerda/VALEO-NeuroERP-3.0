"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getTracer = getTracer;
exports.createSpan = createSpan;
exports.setupTelemetry = setupTelemetry;
exports.tracingMiddleware = tracingMiddleware;
const api_1 = require("@opentelemetry/api");
let tracer = null;
function getTracer() {
    if (tracer === undefined || tracer === null) {
        tracer = api_1.trace.getTracer('sales-domain', '1.0.0');
    }
    return tracer;
}
function createSpan(name, attributes) {
    const span = getTracer().startSpan(name);
    if (attributes) {
        Object.entries(attributes).forEach(([key, value]) => {
            span.setAttribute(key, value);
        });
    }
    return span;
}
function setupTelemetry() {
    // Basic telemetry setup - can be extended with full OpenTelemetry SDK
    console.log('Telemetry initialized (basic mode)');
}
// Middleware for tracing requests
function tracingMiddleware() {
    return {
        onRequest: (request, reply, done) => {
            const span = createSpan(`HTTP ${request.method} ${request.url}`, {
                'http.method': request.method,
                'http.url': request.url,
                'http.user_agent': request.headers['user-agent'] || '',
                'tenant.id': request.tenantId ?? '',
                'request.id': request.id,
            });
            // Store span in request for later use
            request.tracingSpan = span;
            done();
        },
        onResponse: (request, reply, done) => {
            if (request.tracingSpan) {
                const span = request.tracingSpan;
                span.setAttribute('http.status_code', reply.statusCode);
                span.end();
            }
            done();
        },
        onError: (request, reply, error, done) => {
            if (request.tracingSpan) {
                const span = request.tracingSpan;
                span.recordException(error);
                span.setAttribute('error', true);
                span.setAttribute('error.message', error.message);
                span.end();
            }
            done();
        },
    };
}
//# sourceMappingURL=tracer.js.map