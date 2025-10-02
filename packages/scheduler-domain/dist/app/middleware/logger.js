"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requestLoggerMiddleware = requestLoggerMiddleware;
const logger_1 = require("../../infra/telemetry/logger");
const tracer_1 = require("../../infra/telemetry/tracer");
async function requestLoggerMiddleware(request, reply) {
    const logger = (0, logger_1.getLogger)();
    const tracer = (0, tracer_1.getTracingService)();
    const requestId = request.headers['x-request-id'] || generateRequestId();
    request.requestId = requestId;
    request.startTime = Date.now();
    const context = {
        requestId,
        tenantId: request.auth?.tenantId,
        userId: request.auth?.user.sub,
        correlationId: request.auth?.user.sub,
        method: request.method,
        url: request.url,
        ip: request.ip,
        userAgent: request.headers['user-agent'],
    };
    logger.logRequest(request, context);
    const span = tracer.traceHttpRequest(request.method, request.url);
    span.setAttributes({
        'http.method': request.method,
        'http.url': request.url,
        'http.user_agent': request.headers['user-agent'] || '',
        'net.peer.ip': request.ip,
        'tenant.id': request.auth?.tenantId || '',
        'user.id': request.auth?.user.sub || '',
        'request.id': requestId,
    });
    request.span = span;
    reply.raw.on('finish', () => {
        const duration = Date.now() - (request.startTime || 0);
        span.setAttributes({
            'http.status_code': reply.statusCode,
            'http.duration_ms': duration,
        });
        logger.logResponse(reply, duration, {
            ...context,
            statusCode: reply.statusCode,
        });
        span.end();
    });
    reply.raw.on('error', (error) => {
        span.recordException(error);
        span.setStatus({
            code: 2,
            message: error.message,
        });
        span.end();
        logger.error('Request error', error, context);
    });
}
function generateRequestId() {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}
//# sourceMappingURL=logger.js.map