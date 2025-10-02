"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TracingService = void 0;
exports.getTracingService = getTracingService;
exports.initializeTracing = initializeTracing;
exports.shutdownTracing = shutdownTracing;
const api_1 = require("@opentelemetry/api");
class TracingService {
    config;
    tracer;
    constructor(config) {
        this.config = config;
        this.tracer = api_1.trace.getTracer(config.serviceName, config.serviceVersion);
    }
    async initialize() {
        if (!this.config.enabled) {
            return;
        }
        console.log(`Tracing initialized for ${this.config.serviceName}`);
    }
    async shutdown() {
    }
    startSpan(name, options = {}) {
        const span = this.tracer.startSpan(name, {
            attributes: options.attributes,
        });
        return span;
    }
    startActiveSpan(name, fn, options = {}) {
        return this.tracer.startActiveSpan(name, {
            attributes: options.attributes,
        }, async (span) => {
            try {
                const result = await fn(span);
                span.setStatus({ code: api_1.SpanStatusCode.OK });
                return result;
            }
            catch (error) {
                span.recordException(error);
                span.setStatus({
                    code: api_1.SpanStatusCode.ERROR,
                    message: error instanceof Error ? error.message : 'Unknown error',
                });
                throw error;
            }
            finally {
                span.end();
            }
        });
    }
    traceScheduleExecution(scheduleId, operation) {
        return this.startSpan(`schedule.${operation}`, {
            attributes: {
                'schedule.id': scheduleId,
                'operation': operation,
            },
        });
    }
    traceDatabaseOperation(operation, table) {
        return this.startSpan(`db.${operation}`, {
            attributes: {
                'db.operation': operation,
                'db.table': table,
            },
        });
    }
    traceHttpRequest(method, url) {
        return this.startSpan('http.request', {
            attributes: {
                'http.method': method,
                'http.url': url,
            },
        });
    }
    traceEventPublishing(eventType, topic) {
        const attributes = {
            'event.type': eventType,
        };
        if (topic) {
            attributes['event.topic'] = topic;
        }
        return this.startSpan('event.publish', { attributes });
    }
}
exports.TracingService = TracingService;
let globalTracingService = null;
function getTracingService() {
    if (!globalTracingService) {
        globalTracingService = new TracingService({
            serviceName: 'scheduler-domain',
            serviceVersion: '1.0.0',
            enabled: process.env.OTEL_ENABLED !== 'false',
        });
    }
    return globalTracingService;
}
async function initializeTracing() {
    const tracingService = getTracingService();
    await tracingService.initialize();
}
async function shutdownTracing() {
    if (globalTracingService) {
        await globalTracingService.shutdown();
    }
}
//# sourceMappingURL=tracer.js.map