export interface MockSpan {
    setAttribute: (key: string, value: any) => void;
    setStatus: (status: any) => void;
    recordException: (error: Error) => void;
    end: () => void;
}
export interface MockTracer {
    startSpan: (name: string) => MockSpan;
}
export declare const kpiCalculationDuration: {
    record: () => void;
};
export declare const forecastGenerationDuration: {
    record: () => void;
};
export declare const reportGenerationDuration: {
    record: () => void;
};
export declare const cubeRefreshDuration: {
    record: () => void;
};
export declare const eventProcessingDuration: {
    record: () => void;
};
export declare const activeConnections: {
    add: () => void;
    remove: () => void;
};
export declare const requestsTotal: {
    add: () => void;
};
export declare const errorsTotal: {
    add: () => void;
};
export declare const tracer: MockTracer;
export declare class AnalyticsTracer {
    static startSpan(name: string, attributes?: Record<string, string | number | boolean>): MockSpan;
    static startKpiCalculation(tenantId: string, kpiName: string): MockSpan;
    static startForecastGeneration(tenantId: string, metricName: string, model: string): MockSpan;
    static startReportGeneration(tenantId: string, reportType: string): MockSpan;
    static startCubeRefresh(tenantId: string, cubeName: string): MockSpan;
    static startEventProcessing(eventType: string, tenantId: string): MockSpan;
    static startDatabaseQuery(operation: string, table: string, tenantId?: string): MockSpan;
    static setSpanError(span: MockSpan, error: Error): void;
    static addTenantAttributes(span: MockSpan, tenantId: string): void;
    static addUserAttributes(span: MockSpan, userId: string, userEmail?: string): void;
    static addPerformanceAttributes(span: MockSpan, duration: number, recordCount?: number): void;
}
//# sourceMappingURL=tracer.d.ts.map