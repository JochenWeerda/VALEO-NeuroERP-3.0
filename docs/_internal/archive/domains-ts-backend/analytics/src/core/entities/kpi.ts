export type KpiId = string;

export interface Kpi {
  readonly id: KpiId;
  readonly tenantId: string;
  name: string;
  value: number;
  delta: number;
  unit?: string;
  recordedAt: Date;
}

export interface CreateKpiInput {
  tenantId: string;
  name: string;
  value: number;
  delta: number;
  unit?: string;
  recordedAt?: Date;
}

export function createKpi(input: CreateKpiInput): Kpi {
  if (!input.tenantId) {
    throw new Error('tenantId is required');
  }
  if (!input.name) {
    throw new Error('name is required');
  }
  if (!Number.isFinite(input.value)) {
    throw new Error('value must be a finite number');
  }
  if (!Number.isFinite(input.delta)) {
    throw new Error('delta must be a finite number');
  }

  return {
    id: `kpi-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    tenantId: input.tenantId,
    name: input.name,
    value: input.value,
    delta: input.delta,
    unit: input.unit,
    recordedAt: input.recordedAt ? new Date(input.recordedAt) : new Date(),
  };
}