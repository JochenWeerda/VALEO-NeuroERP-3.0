export declare const DomainEventType: {
    readonly KPI_CALCULATED: "analytics.kpi.calculated";
    readonly REPORT_GENERATED: "analytics.report.generated";
    readonly FORECAST_CREATED: "analytics.forecast.created";
    readonly MATERIALIZED_VIEW_REFRESHED: "analytics.materialized_view.refreshed";
    readonly AGGREGATION_COMPLETED: "analytics.aggregation.completed";
};
export type DomainEventTypeValue = typeof DomainEventType[keyof typeof DomainEventType];
export interface DomainEvent {
    eventId: string;
    eventType: DomainEventTypeValue;
    eventVersion: number;
    occurredAt: string;
    tenantId: string;
    correlationId?: string;
    causationId?: string;
    metadata?: Record<string, any>;
}
export interface KpiCalculatedEvent extends DomainEvent {
    eventType: typeof DomainEventType.KPI_CALCULATED;
    payload: {
        kpiId: string;
        kpiName: string;
        value: number | string | boolean;
        unit: string;
        context: Record<string, any>;
        calculatedAt: string;
    };
}
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
export type AnyDomainEvent = KpiCalculatedEvent | ReportGeneratedEvent | ForecastCreatedEvent | MaterializedViewRefreshedEvent | AggregationCompletedEvent;
//# sourceMappingURL=domain-events.d.ts.map