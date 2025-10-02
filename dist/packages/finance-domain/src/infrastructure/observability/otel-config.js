"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OpenTelemetryConfig = void 0;
const sdk_node_1 = require("@opentelemetry/sdk-node");
const auto_instrumentations_node_1 = require("@opentelemetry/auto-instrumentations-node");
const exporter_jaeger_1 = require("@opentelemetry/exporter-jaeger");
const exporter_prometheus_1 = require("@opentelemetry/exporter-prometheus");
const resources_1 = require("@opentelemetry/resources");
const semantic_conventions_1 = require("@opentelemetry/semantic-conventions");
const api_1 = require("@opentelemetry/api");
// Configure OpenTelemetry logging
api_1.diag.setLogger(new api_1.DiagConsoleLogger(), api_1.DiagLogLevel.INFO);
class OpenTelemetryConfig {
    static instance = null;
    static initialize() {
        if (this.instance) {
            return;
        }
        const resource = new resources_1.Resource({
            [semantic_conventions_1.SemanticResourceAttributes.SERVICE_NAME]: 'valero-neuroerp-finance',
            [semantic_conventions_1.SemanticResourceAttributes.SERVICE_VERSION]: '3.0.0',
            [semantic_conventions_1.SemanticResourceAttributes.SERVICE_NAMESPACE]: 'finance-domain',
        });
        // Jaeger exporter for distributed tracing
        const jaegerExporter = new exporter_jaeger_1.JaegerExporter({
            endpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces',
        });
        // Prometheus exporter for metrics
        const prometheusExporter = new exporter_prometheus_1.PrometheusExporter({
            port: parseInt(process.env.PROMETHEUS_METRICS_PORT || '9464'),
        });
        this.instance = new sdk_node_1.NodeSDK({
            resource,
            traceExporter: jaegerExporter,
            // metricReader: prometheusExporter, // Temporarily disabled due to type incompatibility
            instrumentations: [
                (0, auto_instrumentations_node_1.getNodeAutoInstrumentations)({
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
    static shutdown() {
        if (this.instance) {
            return this.instance.shutdown();
        }
        return Promise.resolve();
    }
}
exports.OpenTelemetryConfig = OpenTelemetryConfig;
exports.default = OpenTelemetryConfig;
