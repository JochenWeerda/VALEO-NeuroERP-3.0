import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { PrometheusExporter } from '@opentelemetry/exporter-prometheus';
import { resourceFromAttributes } from '@opentelemetry/resources';
import {
  ATTR_SERVICE_NAME,
  ATTR_SERVICE_NAMESPACE,
  ATTR_SERVICE_VERSION,
} from '@opentelemetry/semantic-conventions';
import { DiagConsoleLogger, DiagLogLevel, diag } from '@opentelemetry/api';

// Configure OpenTelemetry logging
diag.setLogger(new DiagConsoleLogger(), DiagLogLevel.INFO);

export class OpenTelemetryConfig {
  private static instance: NodeSDK | null = null;

  public static initialize(): void {
    if (this.instance) {
      return;
    }

    const resource = resourceFromAttributes({
      [ATTR_SERVICE_NAME]: 'valero-neuroerp-finance',
      [ATTR_SERVICE_VERSION]: '3.0.0',
      [ATTR_SERVICE_NAMESPACE]: 'finance-domain',
    });

    const traceExporter = new OTLPTraceExporter({
      url: process.env.OTEL_EXPORTER_OTLP_TRACES_ENDPOINT || 'http://localhost:4318/v1/traces',
    });

    // Prometheus exporter for metrics
    const prometheusExporter = new PrometheusExporter({
      port: parseInt(process.env.PROMETHEUS_METRICS_PORT || '9464'),
    });

    this.instance = new NodeSDK({
      resource,
      traceExporter,
      metricReader: prometheusExporter,
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
