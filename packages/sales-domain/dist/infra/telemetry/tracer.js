"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getTracer = getTracer;
exports.createSpan = createSpan;
exports.setupTelemetry = setupTelemetry;
exports.tracingMiddleware = tracingMiddleware;
var api_1 = require("@opentelemetry/api");
var tracer = null;
function getTracer() {
    if (tracer === undefined || tracer === null) {
        tracer = api_1.trace.getTracer('sales-domain', '1.0.0');
    }
    return tracer;
}
function createSpan(name, attributes) {
    var span = getTracer().startSpan(name);
    if (attributes) {
        Object.entries(attributes).forEach(function (_a) {
            var key = _a[0], value = _a[1];
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
        onRequest: function (request, reply, done) {
            var _a;
            var span = createSpan("HTTP ".concat(request.method, " ").concat(request.url), {
                'http.method': request.method,
                'http.url': request.url,
                'http.user_agent': request.headers['user-agent'] || '',
                'tenant.id': (_a = request.tenantId) !== null && _a !== void 0 ? _a : '',
                'request.id': request.id,
            });
            // Store span in request for later use
            request.tracingSpan = span;
            done();
        },
        onResponse: function (request, reply, done) {
            if (request.tracingSpan) {
                var span = request.tracingSpan;
                span.setAttribute('http.status_code', reply.statusCode);
                span.end();
            }
            done();
        },
        onError: function (request, reply, error, done) {
            if (request.tracingSpan) {
                var span = request.tracingSpan;
                span.recordException(error);
                span.setAttribute('error', true);
                span.setAttribute('error.message', error.message);
                span.end();
            }
            done();
        },
    };
}
