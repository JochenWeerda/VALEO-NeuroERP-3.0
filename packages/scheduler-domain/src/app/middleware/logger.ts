import { FastifyReply, FastifyRequest } from 'fastify';
import { LogContext, getLogger } from '../../infra/telemetry/logger';
import { getTracingService } from '../../infra/telemetry/tracer';

declare module 'fastify' {
  interface FastifyRequest {
    startTime?: number;
    requestId?: string;
  }
}

export async function requestLoggerMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<void> {
  const logger = getLogger();
  const tracer = getTracingService();

  // Generate request ID if not present
  const requestId = request.headers['x-request-id'] as string || generateRequestId();
  request.requestId = requestId;

  // Start timing
  request.startTime = Date.now();

  // Extract context for logging
  const context: LogContext = {
    requestId,
    tenantId: request.auth?.tenantId,
    userId: request.auth?.user.sub,
    correlationId: request.auth?.user.sub, // Could be enhanced
    method: request.method,
    url: request.url,
    ip: request.ip,
    userAgent: request.headers['user-agent'] as string,
  };

  // Log request
  logger.logRequest(request, context);

  // Start tracing span
  const span = tracer.traceHttpRequest(request.method, request.url);
  span.setAttributes({
    'http.method': request.method,
    'http.url': request.url,
    'http.user_agent': request.headers['user-agent'] as string || '',
    'net.peer.ip': request.ip,
    'tenant.id': request.auth?.tenantId || '',
    'user.id': request.auth?.user.sub || '',
    'request.id': requestId,
  });

  // Add span to request for use in handlers
  (request as any).span = span;

  // Log response when finished
  reply.raw.on('finish', () => {
    const duration = Date.now() - (request.startTime || 0);

    // Set span attributes
    span.setAttributes({
      'http.status_code': reply.statusCode,
      'http.duration_ms': duration,
    });

    // Log response
    logger.logResponse(reply, duration, {
      ...context,
      statusCode: reply.statusCode,
    });

    // End span
    span.end();
  });

  // Handle errors
  reply.raw.on('error', (error) => {
    span.recordException(error);
    span.setStatus({
      code: 2, // ERROR
      message: error.message,
    });
    span.end();

    logger.error('Request error', error, context);
  });
}

function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}