"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.MetricsService = void 0;
const prom_client_1 = require("prom-client");
class MetricsService {
    constructor() {
        // Enable default metrics collection
        (0, prom_client_1.collectDefaultMetrics)({ prefix: 'finance_' });
        // Business metrics
        this.invoiceProcessingTime = new prom_client_1.Histogram({
            name: 'finance_invoice_processing_duration_seconds',
            help: 'Time taken to process invoices',
            labelNames: ['type', 'status'],
            buckets: [0.1, 0.5, 1, 2, 5, 10, 30, 60]
        });
        this.journalPostingCount = new prom_client_1.Counter({
            name: 'finance_journal_postings_total',
            help: 'Total number of journal postings',
            labelNames: ['type', 'status']
        });
        this.reconciliationSuccessRate = new prom_client_1.Gauge({
            name: 'finance_reconciliation_success_rate',
            help: 'Bank reconciliation success rate',
            labelNames: ['bank_account']
        });
        this.aiConfidenceScore = new prom_client_1.Histogram({
            name: 'finance_ai_confidence_score',
            help: 'AI confidence scores for automated processing',
            labelNames: ['operation'],
            buckets: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        });
        this.auditTrailIntegrity = new prom_client_1.Gauge({
            name: 'finance_audit_trail_integrity',
            help: 'Audit trail integrity score (1.0 = perfect)',
            labelNames: ['period']
        });
        // Performance metrics
        this.databaseQueryDuration = new prom_client_1.Histogram({
            name: 'finance_database_query_duration_seconds',
            help: 'Database query execution time',
            labelNames: ['operation', 'table'],
            buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5]
        });
        this.cacheHitRate = new prom_client_1.Gauge({
            name: 'finance_cache_hit_rate',
            help: 'Cache hit rate percentage',
            labelNames: ['cache_type']
        });
        this.eventProcessingLatency = new prom_client_1.Histogram({
            name: 'finance_event_processing_latency_seconds',
            help: 'Time to process domain events',
            labelNames: ['event_type'],
            buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
        });
        this.apiResponseTime = new prom_client_1.Histogram({
            name: 'finance_api_response_time_seconds',
            help: 'API endpoint response time',
            labelNames: ['method', 'endpoint', 'status_code'],
            buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]
        });
        // System metrics
        this.activeConnections = new prom_client_1.Gauge({
            name: 'finance_active_connections',
            help: 'Number of active connections',
            labelNames: ['type']
        });
        this.memoryUsage = new prom_client_1.Gauge({
            name: 'finance_memory_usage_bytes',
            help: 'Memory usage in bytes',
            labelNames: ['type']
        });
        this.errorRate = new prom_client_1.Counter({
            name: 'finance_errors_total',
            help: 'Total number of errors',
            labelNames: ['type', 'component']
        });
    }
    static getInstance() {
        if (!MetricsService.instance) {
            MetricsService.instance = new MetricsService();
        }
        return MetricsService.instance;
    }
    // Business metrics methods
    recordInvoiceProcessingTime(type, status, duration) {
        this.invoiceProcessingTime.observe({ type, status }, duration);
    }
    incrementJournalPosting(type, status) {
        this.journalPostingCount.inc({ type, status });
    }
    setReconciliationSuccessRate(bankAccount, rate) {
        this.reconciliationSuccessRate.set({ bank_account: bankAccount }, rate);
    }
    recordAIConfidenceScore(operation, score) {
        this.aiConfidenceScore.observe({ operation }, score);
    }
    setAuditTrailIntegrity(period, integrity) {
        this.auditTrailIntegrity.set({ period }, integrity);
    }
    // Performance metrics methods
    recordDatabaseQueryDuration(operation, table, duration) {
        this.databaseQueryDuration.observe({ operation, table }, duration);
    }
    setCacheHitRate(cacheType, rate) {
        this.cacheHitRate.set({ cache_type: cacheType }, rate);
    }
    recordEventProcessingLatency(eventType, latency) {
        this.eventProcessingLatency.observe({ event_type: eventType }, latency);
    }
    recordApiResponseTime(method, endpoint, statusCode, duration) {
        this.apiResponseTime.observe({ method, endpoint, status_code: statusCode.toString() }, duration);
    }
    // System metrics methods
    setActiveConnections(type, count) {
        this.activeConnections.set({ type }, count);
    }
    setMemoryUsage(type, bytes) {
        this.memoryUsage.set({ type }, bytes);
    }
    incrementErrorCount(type, component) {
        this.errorRate.inc({ type, component });
    }
    // Utility methods
    async getMetrics() {
        return prom_client_1.register.metrics();
    }
    async getRegistry() {
        return JSON.stringify(prom_client_1.register.getMetricsAsJSON());
    }
    reset() {
        prom_client_1.register.resetMetrics();
    }
}
exports.MetricsService = MetricsService;
exports.default = MetricsService;
//# sourceMappingURL=metrics-service.js.map