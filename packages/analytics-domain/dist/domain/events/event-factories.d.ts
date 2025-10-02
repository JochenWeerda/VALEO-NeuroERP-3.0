import { KpiCalculatedEvent, ReportGeneratedEvent, ForecastCreatedEvent, MaterializedViewRefreshedEvent, AggregationCompletedEvent } from './domain-events';
import { KPI } from '../entities/kpi';
import { Report } from '../entities/report';
import { Forecast } from '../entities/forecast';
export declare function createKpiCalculatedEvent(kpi: KPI, correlationId?: string, causationId?: string): KpiCalculatedEvent;
export declare function createReportGeneratedEvent(report: Report, recordCount: number, correlationId?: string, causationId?: string): ReportGeneratedEvent;
export declare function createForecastCreatedEvent(forecast: Forecast, correlationId?: string, causationId?: string): ForecastCreatedEvent;
export declare function createMaterializedViewRefreshedEvent(viewName: string, refreshType: 'full' | 'incremental', recordCount: number, executionTimeMs: number, tenantId: string, correlationId?: string, causationId?: string): MaterializedViewRefreshedEvent;
export declare function createAggregationCompletedEvent(aggregationName: string, sourceTables: string[], recordCount: number, executionTimeMs: number, tenantId: string, correlationId?: string, causationId?: string): AggregationCompletedEvent;
//# sourceMappingURL=event-factories.d.ts.map