export type TrendId = string;

export interface TrendPoint {
  readonly id: TrendId;
  readonly tenantId: string;
  date: string;
  sales: number;
  inventory: number;
  recordedAt: Date;
}

export interface CreateTrendPointInput {
  tenantId: string;
  date: string;
  sales: number;
  inventory: number;
  recordedAt?: Date;
}

export function createTrendPoint(input: CreateTrendPointInput): TrendPoint {
  if (!input.tenantId) {
    throw new Error('tenantId is required');
  }
  if (!input.date) {
    throw new Error('date is required');
  }
  if (!Number.isFinite(input.sales)) {
    throw new Error('sales must be a finite number');
  }
  if (!Number.isFinite(input.inventory)) {
    throw new Error('inventory must be a finite number');
  }

  return {
    id: `trend-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    tenantId: input.tenantId,
    date: input.date,
    sales: input.sales,
    inventory: input.inventory,
    recordedAt: input.recordedAt ? new Date(input.recordedAt) : new Date(),
  };
}