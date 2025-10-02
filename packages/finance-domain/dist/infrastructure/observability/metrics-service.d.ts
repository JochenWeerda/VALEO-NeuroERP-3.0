export declare class MetricsService {
    private static instance;
    private readonly invoiceProcessingTime;
    private readonly journalPostingCount;
    private readonly reconciliationSuccessRate;
    private readonly aiConfidenceScore;
    private readonly auditTrailIntegrity;
    private readonly databaseQueryDuration;
    private readonly cacheHitRate;
    private readonly eventProcessingLatency;
    private readonly apiResponseTime;
    private readonly activeConnections;
    private readonly memoryUsage;
    private readonly errorRate;
    private constructor();
    static getInstance(): MetricsService;
    recordInvoiceProcessingTime(type: string, status: string, duration: number): void;
    incrementJournalPosting(type: string, status: string): void;
    setReconciliationSuccessRate(bankAccount: string, rate: number): void;
    recordAIConfidenceScore(operation: string, score: number): void;
    setAuditTrailIntegrity(period: string, integrity: number): void;
    recordDatabaseQueryDuration(operation: string, table: string, duration: number): void;
    setCacheHitRate(cacheType: string, rate: number): void;
    recordEventProcessingLatency(eventType: string, latency: number): void;
    recordApiResponseTime(method: string, endpoint: string, statusCode: number, duration: number): void;
    setActiveConnections(type: string, count: number): void;
    setMemoryUsage(type: string, bytes: number): void;
    incrementErrorCount(type: string, component: string): void;
    getMetrics(): Promise<string>;
    getRegistry(): Promise<string>;
    reset(): void;
}
export default MetricsService;
//# sourceMappingURL=metrics-service.d.ts.map