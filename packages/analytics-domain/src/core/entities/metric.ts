import { createId, MetricId as BrandedMetricId } from '@valero-neuroerp/data-models';

export type MetricId = BrandedMetricId;

export type MetricType = 'counter' | 'gauge' | 'histogram';

export interface Metric {
  readonly id: MetricId;
  readonly tenantId: string;
  name: string;
  value: number;
  type: MetricType;
  unit?: string;
  dimensions: Record<string, string>;
  recordedAt: Date;
}

export interface RecordMetricInput {
  tenantId: string;
  name: string;
  value: number;
  type?: MetricType;
  unit?: string;
  dimensions?: Record<string, string>;
  recordedAt?: Date;
}

export function recordMetric(input: RecordMetricInput): Metric {
  if (!input.tenantId) {
    throw new Error('tenantId is required');
  }
  if (!input.name) {
    throw new Error('name is required');
  }
  if (!Number.isFinite(input.value)) {
    throw new Error('value must be a finite number');
  }

  return {
    id: createId('MetricId') as MetricId,
    tenantId: input.tenantId,
    name: input.name,
    value: input.value,
    type: input.type ?? 'gauge',
    unit: input.unit,
    dimensions: input.dimensions ? { ...input.dimensions } : {},
    recordedAt: input.recordedAt ? new Date(input.recordedAt) : new Date(),
  };
}
