import { ReportId, createReportId } from '@valero-neuroerp/data-models';

export type ReportStatus = 'draft' | 'running' | 'completed' | 'failed';

export interface ReportDefinition {
  metrics: string[];
  filters?: Record<string, unknown>;
  groupBy?: string[];
  timeframe?: {
    start: Date;
    end: Date;
  };
}

export interface Report {
  readonly id: ReportId;
  readonly tenantId: string;
  name: string;
  status: ReportStatus;
  definition: ReportDefinition;
  readonly createdAt: Date;
  updatedAt: Date;
  lastRunAt?: Date;
  lastDurationMs?: number;
}

export interface CreateReportInput {
  tenantId: string;
  name: string;
  definition: ReportDefinition;
}

export interface UpdateReportInput {
  name?: string;
  status?: ReportStatus;
  definition?: Partial<ReportDefinition>;
  lastRunAt?: Date;
  lastDurationMs?: number;
}

export function createReport(input: CreateReportInput): Report {
  if (!input.tenantId) {
    throw new Error('tenantId is required');
  }
  if (!input.name) {
    throw new Error('name is required');
  }
  if (!input.definition.metrics || input.definition.metrics.length === 0) {
    throw new Error('definition.metrics must contain at least one metric');
  }

  const now = new Date();

  return {
    id: createReportId(globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`),
    tenantId: input.tenantId,
    name: input.name.trim(),
    status: 'draft',
    definition: normalizeDefinition(input.definition),
    createdAt: now,
    updatedAt: now,
  };
}

export function applyReportUpdate(report: Report, update: UpdateReportInput): Report {
  const definition = update.definition
    ? normalizeDefinition({ ...report.definition, ...update.definition })
    : report.definition;

  const next: Report = {
    ...report,
    name: update.name ? update.name.trim() : report.name,
    status: update.status ?? report.status,
    definition,
    lastRunAt: update.lastRunAt ?? report.lastRunAt,
    lastDurationMs: update.lastDurationMs ?? report.lastDurationMs,
    updatedAt: new Date(),
  };

  return next;
}

function normalizeDefinition(definition: ReportDefinition): ReportDefinition {
  return {
    metrics: [...new Set(definition.metrics.map((metric) => metric.trim()))],
    filters: definition.filters ? { ...definition.filters } : undefined,
    groupBy: definition.groupBy ? [...new Set(definition.groupBy)] : undefined,
    timeframe: definition.timeframe
      ? {
          start: new Date(definition.timeframe.start),
          end: new Date(definition.timeframe.end),
        }
      : undefined,
  };
}
