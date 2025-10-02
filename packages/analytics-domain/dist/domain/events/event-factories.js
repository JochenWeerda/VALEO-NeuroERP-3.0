"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createKpiCalculatedEvent = createKpiCalculatedEvent;
exports.createReportGeneratedEvent = createReportGeneratedEvent;
exports.createForecastCreatedEvent = createForecastCreatedEvent;
exports.createMaterializedViewRefreshedEvent = createMaterializedViewRefreshedEvent;
exports.createAggregationCompletedEvent = createAggregationCompletedEvent;
const uuid_1 = require("uuid");
const domain_events_1 = require("./domain-events");
function createKpiCalculatedEvent(kpi, correlationId, causationId) {
    const event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.KPI_CALCULATED,
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
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createReportGeneratedEvent(report, recordCount, correlationId, causationId) {
    const payload = {
        reportId: report.id,
        reportType: report.type,
        format: report.format,
        recordCount,
        generatedAt: report.generatedAt.toISOString(),
    };
    if (report.uri) {
        payload.uri = report.uri;
    }
    const event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.REPORT_GENERATED,
        eventVersion: 1,
        occurredAt: new Date().toISOString(),
        tenantId: report.tenantId,
        payload,
    };
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createForecastCreatedEvent(forecast, correlationId, causationId) {
    const event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.FORECAST_CREATED,
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
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createMaterializedViewRefreshedEvent(viewName, refreshType, recordCount, executionTimeMs, tenantId, correlationId, causationId) {
    const event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.MATERIALIZED_VIEW_REFRESHED,
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
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
function createAggregationCompletedEvent(aggregationName, sourceTables, recordCount, executionTimeMs, tenantId, correlationId, causationId) {
    const event = {
        eventId: (0, uuid_1.v4)(),
        eventType: domain_events_1.DomainEventType.AGGREGATION_COMPLETED,
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
    if (correlationId)
        event.correlationId = correlationId;
    if (causationId)
        event.causationId = causationId;
    return event;
}
//# sourceMappingURL=event-factories.js.map