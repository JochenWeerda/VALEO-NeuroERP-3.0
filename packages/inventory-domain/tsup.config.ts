import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: true,
  splitting: false,
  sourcemap: true,
  clean: true,
  external: [
    'express',
    'cors',
    'helmet',
    'compression',
    'pg',
    'kafkajs',
    'nats',
    'amqplib',
    'winston',
    'zod',
    'dotenv',
    'reflect-metadata',
    'inversify',
    '@opentelemetry/api',
    '@opentelemetry/sdk-node',
    '@opentelemetry/auto-instrumentations-node',
    '@opentelemetry/exporter-jaeger',
    '@opentelemetry/exporter-prometheus',
    'prom-client',
    'response-time',
    '@valero-neuroerp/data-models',
    '@valero-neuroerp/utilities',
    '@valero-neuroerp/business-rules'
  ],
  treeshake: true,
});

