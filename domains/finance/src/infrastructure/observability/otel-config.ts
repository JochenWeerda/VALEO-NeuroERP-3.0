import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';
import { PrometheusExporter } from '@opentelemetry/exporter-prometheus';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';
import { diag, DiagConsoleLogger, DiagLogLevel } from '@opentelemetry/api';

// Configure OpenTelemetry logging
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.INFO);

export class OpenTelemetryConfig {
  private static instance: NodeSDK | null = null;

  public static initialize(): void {
    if (this.instance) {
      return;
    }

    const resource = new Resource({
      [SemanticResourceAttributes.SERVICE_NAME]: 'valero-neuroerp-finance',
      [SemanticResourceAttributes.SERVICE_VERSION]: '3.0.0',
      [SemanticResourceAttributes.SERVICE_NAMESPACE]: 'finance-domain',
    });

    // Jaeger exporter for distributed tracing
    const jaegerExporter = new JaegerExporter({
      endpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces',
    });

    // Prometheus exporter for metrics
    const prometheusExporter = new PrometheusExporter({
      port: parseInt(process.env.PROMETHEUS_METRICS_PORT || '9464'),
    });

    this.instance = new NodeSDK({
      resource,
      traceExporter: jaegerExporter,
      // metricReader: prometheusExporter, // Temporarily disabled due to type incompatibility
      instrumentations: [
        getNodeAutoInstrumentations({
          '@opentelemetry/instrumentation-express': {
            enabled: true,
          },
          '@opentelemetry/instrumentation-pg': {
            enabled: true,
          },
          // '@opentelemetry/instrumentation-kafkajs': {
          //   enabled: true,
          // },
        }),
      ],
    });

    this.instance.start();
  }

  public static shutdown(): Promise<void> {
    if (this.instance) {
      return this.instance.shutdown();
    }
    return Promise.resolve();
  }
}

export default OpenTelemetryConfig;