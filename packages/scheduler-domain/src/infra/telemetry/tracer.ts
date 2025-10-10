import { Span, SpanStatusCode, Tracer, trace } from '@opentelemetry/api';

export interface TracingConfig {
  serviceName: string;
  serviceVersion: string;
  enabled?: boolean;
}

export class TracingService {
  private readonly tracer: Tracer;

  constructor(private readonly config: TracingConfig) {
    this.tracer = trace.getTracer(config.serviceName, config.serviceVersion);
  }

  async initialize(): Promise<void> {
    if (!this.config.enabled) {
      return;
    }

    console.log(`Tracing initialized for ${this.config.serviceName}`);
  }

  async shutdown(): Promise<void> {
    // No-op for basic implementation
  }

  startSpan(name: string, options: { attributes?: Record<string, string | number | boolean> } = {}): Span {
    const span = this.tracer.startSpan(name, {
      attributes: options.attributes,
    });
    return span;
  }

  startActiveSpan<T>(
    name: string,
    fn: (span: Span) => Promise<T>,
    options: { attributes?: Record<string, string | number | boolean> } = {}
  ): Promise<T> {
    return this.tracer.startActiveSpan(name, {
      attributes: options.attributes,
    }, async (span) => {
      try {
        const result = await fn(span);
        span.setStatus({ code: SpanStatusCode.OK });
        return result;
      } catch (error) {
        span.recordException(error as Error);
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : 'Unknown error',
        });
        throw error;
      } finally {
        span.end();
      }
    });
  }

  // Specialized tracing methods
  traceScheduleExecution(scheduleId: string, operation: string): Span {
    return this.startSpan(`schedule.${operation}`, {
      attributes: {
        'schedule.id': scheduleId,
        'operation': operation,
      },
    });
  }

  traceDatabaseOperation(operation: string, table: string): Span {
    return this.startSpan(`db.${operation}`, {
      attributes: {
        'db.operation': operation,
        'db.table': table,
      },
    });
  }

  traceHttpRequest(method: string, url: string): Span {
    return this.startSpan('http.request', {
      attributes: {
        'http.method': method,
        'http.url': url,
      },
    });
  }

  traceEventPublishing(eventType: string, topic?: string): Span {
    const attributes: Record<string, string | number | boolean> = {
      'event.type': eventType,
    };
    if (topic) {
      attributes['event.topic'] = topic;
    }
    return this.startSpan('event.publish', { attributes });
  }
}

// Global tracing service instance
let globalTracingService: TracingService | null = null;

export function getTracingService(): TracingService {
  if (!globalTracingService) {
    globalTracingService = new TracingService({
      serviceName: 'scheduler-domain',
      serviceVersion: '1.0.0',
      enabled: process.env.OTEL_ENABLED !== 'false',
    });
  }
  return globalTracingService;
}

export async function initializeTracing(): Promise<void> {
  const tracingService = getTracingService();
  await tracingService.initialize();
}

export async function shutdownTracing(): Promise<void> {
  if (globalTracingService) {
    await globalTracingService.shutdown();
  }
}