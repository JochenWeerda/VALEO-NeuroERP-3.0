// Domain Event Types
export const DomainEventType = {
  KPI_CALCULATED: 'analytics.kpi.calculated',
  REPORT_GENERATED: 'analytics.report.generated',
  FORECAST_CREATED: 'analytics.forecast.created',
  MATERIALIZED_VIEW_REFRESHED: 'analytics.materialized_view.refreshed',
  AGGREGATION_COMPLETED: 'analytics.aggregation.completed',
} as const;

export type DomainEventTypeValue = typeof DomainEventType[keyof typeof DomainEventType];

// Base Domain Event Interface
export interface DomainEvent {
  eventId: string;
  eventType: DomainEventTypeValue;
  eventVersion: number;
  occurredAt: string;
  tenantId: string;
  correlationId?: string;
  causationId?: string;
  metadata?: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
}

// KPI Events
export interface KpiCalculatedEvent extends DomainEvent {
  eventType: typeof DomainEventType.KPI_CALCULATED;
  payload: {
    kpiId: string;
    kpiName: string;
    value: number | string | boolean;
    unit: string;
    context: Record<string, any>; // eslint-disable-line @typescript-eslint/no-explicit-any
    calculatedAt: string;
  };
}

// Report Events
export interface ReportGeneratedEvent extends DomainEvent {
  eventType: typeof DomainEventType.REPORT_GENERATED;
  payload: {
    reportId: string;
    reportType: string;
    format: string;
    recordCount: number;
    generatedAt: string;
    uri?: string;
  };
}

// Forecast Events
export interface ForecastCreatedEvent extends DomainEvent {
  eventType: typeof DomainEventType.FORECAST_CREATED;
  payload: {
    forecastId: string;
    metricName: string;
    horizon: number;
    horizonUnit: string;
    model: string;
    forecastCount: number;
    createdAt: string;
  };
}

// Materialized View Events
export interface MaterializedViewRefreshedEvent extends DomainEvent {
  eventType: typeof DomainEventType.MATERIALIZED_VIEW_REFRESHED;
  payload: {
    viewName: string;
    refreshType: 'full' | 'incremental';
    recordCount: number;
    executionTimeMs: number;
    refreshedAt: string;
  };
}

// Aggregation Events
export interface AggregationCompletedEvent extends DomainEvent {
  eventType: typeof DomainEventType.AGGREGATION_COMPLETED;
  payload: {
    aggregationName: string;
    sourceTables: string[];
    recordCount: number;
    executionTimeMs: number;
    completedAt: string;
  };
}

// Union type for all domain events
export type AnyDomainEvent =
  | KpiCalculatedEvent
  | ReportGeneratedEvent
  | ForecastCreatedEvent
  | MaterializedViewRefreshedEvent
  | AggregationCompletedEvent;