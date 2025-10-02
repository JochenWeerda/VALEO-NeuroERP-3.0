import { trace, Span, Tracer } from '@opentelemetry/api';

let tracer: Tracer | null = null;

export function getTracer(): Tracer {
  if (!tracer) {
    tracer = trace.getTracer('sales-domain', '1.0.0');
  }
  return tracer;
}

export function createSpan(name: string, attributes?: Record<string, string | number | boolean>): Span {
  const span = getTracer().startSpan(name);

  if (attributes) {
    Object.entries(attributes).forEach(([key, value]) => {
      span.setAttribute(key, value);
    });
  }

  return span;
}

export function setupTelemetry() {
  // Basic telemetry setup - can be extended with full OpenTelemetry SDK
  console.log('Telemetry initialized (basic mode)');
}

// Middleware for tracing requests
export function tracingMiddleware() {
  return {
    onRequest: (request: any, reply: any, done: () => void) => {
      const span = createSpan(`HTTP ${request.method} ${request.url}`, {
        'http.method': request.method,
        'http.url': request.url,
        'http.user_agent': request.headers['user-agent'] || '',
        'tenant.id': request.tenantId || '',
        'request.id': request.id,
      });

      // Store span in request for later use
      request.tracingSpan = span;

      done();
    },

    onResponse: (request: any, reply: any, done: () => void) => {
      if (request.tracingSpan) {
        const span = request.tracingSpan as Span;
        span.setAttribute('http.status_code', reply.statusCode);
        span.end();
      }
      done();
    },

    onError: (request: any, reply: any, error: any, done: () => void) => {
      if (request.tracingSpan) {
        const span = request.tracingSpan as Span;
        span.recordException(error);
        span.setAttribute('error', true);
        span.setAttribute('error.message', error.message);
        span.end();
      }
      done();
    },
  };
}