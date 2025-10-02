import { v4 as uuidv4 } from 'uuid';
import {
  DomainEventType,
  KpiCalculatedEvent,
  ReportGeneratedEvent,
  ForecastCreatedEvent,
  MaterializedViewRefreshedEvent,
  AggregationCompletedEvent,
} from './domain-events';
import { KPI } from '../entities/kpi';
import { Report } from '../entities/report';
import { Forecast } from '../entities/forecast';

// KPI Event Factories
export function createKpiCalculatedEvent(
  kpi: KPI,
  correlationId?: string,
  causationId?: string
): KpiCalculatedEvent {
  const event: KpiCalculatedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.KPI_CALCULATED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: kpi.tenantId,
    payload: {
      kpiId: kpi.id,
      kpiName: kpi.name,
      value: kpi.value,
      unit: kpi.unit,
      context: kpi.context,
      calculatedAt: kpi.calculatedAt.toISOString(),
    },
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

// Report Event Factories
export function createReportGeneratedEvent(
  report: Report,
  recordCount: number,
  correlationId?: string,
  causationId?: string
): ReportGeneratedEvent {
  const payload: any = {
    reportId: report.id,
    reportType: report.type,
    format: report.format,
    recordCount,
    generatedAt: report.generatedAt.toISOString(),
  };

  if (report.uri) {
    payload.uri = report.uri;
  }

  const event: ReportGeneratedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.REPORT_GENERATED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: report.tenantId,
    payload,
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

// Forecast Event Factories
export function createForecastCreatedEvent(
  forecast: Forecast,
  correlationId?: string,
  causationId?: string
): ForecastCreatedEvent {
  const event: ForecastCreatedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.FORECAST_CREATED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId: forecast.tenantId,
    payload: {
      forecastId: forecast.id,
      metricName: forecast.metricName,
      horizon: forecast.horizon,
      horizonUnit: forecast.horizonUnit,
      model: forecast.model,
      forecastCount: forecast.forecastValues.length,
      createdAt: forecast.createdAt.toISOString(),
    },
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

// Materialized View Event Factories
export function createMaterializedViewRefreshedEvent(
  viewName: string,
  refreshType: 'full' | 'incremental',
  recordCount: number,
  executionTimeMs: number,
  tenantId: string,
  correlationId?: string,
  causationId?: string
): MaterializedViewRefreshedEvent {
  const event: MaterializedViewRefreshedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.MATERIALIZED_VIEW_REFRESHED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    payload: {
      viewName,
      refreshType,
      recordCount,
      executionTimeMs,
      refreshedAt: new Date().toISOString(),
    },
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}

// Aggregation Event Factories
export function createAggregationCompletedEvent(
  aggregationName: string,
  sourceTables: string[],
  recordCount: number,
  executionTimeMs: number,
  tenantId: string,
  correlationId?: string,
  causationId?: string
): AggregationCompletedEvent {
  const event: AggregationCompletedEvent = {
    eventId: uuidv4(),
    eventType: DomainEventType.AGGREGATION_COMPLETED,
    eventVersion: 1,
    occurredAt: new Date().toISOString(),
    tenantId,
    payload: {
      aggregationName,
      sourceTables,
      recordCount,
      executionTimeMs,
      completedAt: new Date().toISOString(),
    },
  };

  if (correlationId) event.correlationId = correlationId;
  if (causationId) event.causationId = causationId;

  return event;
}