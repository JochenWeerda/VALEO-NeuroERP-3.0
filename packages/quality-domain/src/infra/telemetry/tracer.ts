import { NodeSDK } from '@opentelemetry/sdk-node';
// @ts-ignore - Optional dependency
import { OTLPTraceExporter } from '@opentelemetry/exporter-otlp-http';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { FastifyRequest, FastifyReply } from 'fastify';
import { trace, context, SpanStatusCode } from '@opentelemetry/api';
import { HttpInstrumentation } from '@opentelemetry/instrumentation-http';
import { PgInstrumentation } from '@opentelemetry/instrumentation-pg';

let sdk: NodeSDK | null = null;

/**
 * Setup OpenTelemetry
 */
export function setupTelemetry(): NodeSDK | null {
  if (process.env.OTEL_ENABLED !== 'true') {
    console.log('OpenTelemetry disabled');
    return null;
  }

  const serviceName = process.env.OTEL_SERVICE_NAME ?? 'quality-domain';
  const otlpEndpoint = process.env.OTEL_EXPORTER_OTLP_ENDPOINT ?? 'http://localhost:4318';

  sdk = new NodeSDK({
    resource: new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: serviceName,
      [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
    }),
    traceExporter: new OTLPTraceExporter({
      url: `${otlpEndpoint}/v1/traces`,
    }),
    instrumentations: [
      new HttpInstrumentation(),
      new PgInstrumentation(),
    ],
  });

  sdk.start();
  console.log(`OpenTelemetry initialized for ${serviceName}`);

  // Handle graceful shutdown
  process.on('SIGTERM', () => {
    sdk?.shutdown()
      .then(() => console.log('OpenTelemetry shutdown complete'))
      .catch((error) => console.error('Error shutting down OpenTelemetry', error));
  });

  return sdk;
}

/**
 * Fastify middleware for tracing
 */
export async function tracingMiddleware(
  request: FastifyRequest,
  reply: FastifyReply
): Promise<void> {
  const tracer = trace.getTracer('quality-domain');
  const span = tracer.startSpan(`${request.method} ${request.url}`);

  span.setAttributes({
    'http.method': request.method,
    'http.url': request.url,
    'http.route': request.routerPath,
    'tenant.id': request.headers['x-tenant-id'] as string ?? 'unknown',
  });

  // Store span in request context
  context.with(trace.setSpan(context.active(), span), () => {
    (reply as any).addHook('onResponse', () => {
      span.setAttributes({
        'http.status_code': reply.statusCode,
      });

      if (reply.statusCode >= 400) {
        span.setStatus({ code: SpanStatusCode.ERROR });
      } else {
        span.setStatus({ code: SpanStatusCode.OK });
      }

      span.end();
    });
  });
}

/**
 * Shutdown telemetry
 */
export async function shutdownTelemetry(): Promise<void> {
  if (sdk) {
    await sdk.shutdown();
    console.log('OpenTelemetry shutdown complete');
  }
}

