/**
 * VALEO NeuroERP 3.0 - Inventory Metrics Service
 *
 * Metrics service for inventory domain observability.
 */
export interface MetricsService {
    incrementCounter(name: string, labels?: Record<string, string>): void;
    recordGauge(name: string, value: number, labels?: Record<string, string>): void;
    recordHistogram(name: string, value: number, labels?: Record<string, string>): void;
    recordApiResponseTime(name: string, duration: number, labels?: Record<string, string>): void;
    incrementErrorCount(name: string, labels?: Record<string, string>): void;
    recordInvoiceProcessingTime(name: string, duration: number, labels?: Record<string, string>): void;
    recordPutawayTime(name: string, duration: number, labels?: Record<string, string>): void;
    incrementPutawayTasks(name: string, labels?: Record<string, string>): void;
    recordDatabaseQueryDuration(name: string, duration: number, labels?: Record<string, string>): void;
    incrementPickTasks(name: string, labels?: Record<string, string>): void;
    incrementPackTasks(name: string, labels?: Record<string, string>): void;
    incrementReturns(name: string, labels?: Record<string, string>): void;
    incrementQuarantines(name: string, labels?: Record<string, string>): void;
    incrementRoboticsTasks(name: string, labels?: Record<string, string>): void;
    incrementAnomaliesDetected(name: string, labels?: Record<string, string>): void;
    incrementCycleCounts(name: string, labels?: Record<string, string>): void;
    incrementTraceabilityEvents(name: string, labels?: Record<string, string>): void;
    incrementAIRecommendations(name: string, labels?: Record<string, string>): void;
    incrementEDITransactions(name: string, labels?: Record<string, string>): void;
    setBusinessMetricsEnabled(enabled: boolean): void;
    setPerformanceMetricsEnabled(enabled: boolean): void;
    setSystemMetricsEnabled(enabled: boolean): void;
    registerGauge(name: string, value: number, labels?: Record<string, string>): void;
    registerHistogram(name: string, value: number, labels?: Record<string, string>): void;
    registerCounter(name: string, value: number, labels?: Record<string, string>): void;
    getMetrics(): string;
}
export declare class InventoryMetricsService implements MetricsService {
    private counters;
    private gauges;
    private histograms;
    incrementCounter(name: string, labels?: Record<string, string>): void;
    recordGauge(name: string, value: number, labels?: Record<string, string>): void;
    recordHistogram(name: string, value: number, labels?: Record<string, string>): void;
    recordApiResponseTime(name: string, duration: number, labels?: Record<string, string>): void;
    incrementErrorCount(name: string, labels?: Record<string, string>): void;
    recordInvoiceProcessingTime(name: string, duration: number, labels?: Record<string, string>): void;
    recordPutawayTime(name: string, duration: number, labels?: Record<string, string>): void;
    incrementPutawayTasks(name: string, labels?: Record<string, string>): void;
    recordDatabaseQueryDuration(name: string, duration: number, labels?: Record<string, string>): void;
    incrementPickTasks(name: string, labels?: Record<string, string>): void;
    incrementPackTasks(name: string, labels?: Record<string, string>): void;
    incrementReturns(name: string, labels?: Record<string, string>): void;
    incrementQuarantines(name: string, labels?: Record<string, string>): void;
    incrementRoboticsTasks(name: string, labels?: Record<string, string>): void;
    incrementAnomaliesDetected(name: string, labels?: Record<string, string>): void;
    incrementCycleCounts(name: string, labels?: Record<string, string>): void;
    incrementTraceabilityEvents(name: string, labels?: Record<string, string>): void;
    incrementAIRecommendations(name: string, labels?: Record<string, string>): void;
    incrementEDITransactions(name: string, labels?: Record<string, string>): void;
    setBusinessMetricsEnabled(enabled: boolean): void;
    setPerformanceMetricsEnabled(enabled: boolean): void;
    setSystemMetricsEnabled(enabled: boolean): void;
    registerGauge(name: string, value: number, labels?: Record<string, string>): void;
    registerHistogram(name: string, value: number, labels?: Record<string, string>): void;
    registerCounter(name: string, value: number, labels?: Record<string, string>): void;
    getMetrics(): string;
    private getKey;
}
export default InventoryMetricsService;
//# sourceMappingURL=metrics-service.d.ts.map