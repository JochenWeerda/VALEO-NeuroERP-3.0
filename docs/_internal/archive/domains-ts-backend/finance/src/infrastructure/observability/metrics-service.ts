import { register, collectDefaultMetrics, Gauge, Counter, Histogram } from 'prom-client';

export class MetricsService {
  private static instance: MetricsService;

  // Business metrics
  private readonly invoiceProcessingTime: Histogram<string>;
  private readonly journalPostingCount: Counter<string>;
  private readonly reconciliationSuccessRate: Gauge<string>;
  private readonly aiConfidenceScore: Histogram<string>;
  private readonly auditTrailIntegrity: Gauge<string>;

  // Performance metrics
  private readonly databaseQueryDuration: Histogram<string>;
  private readonly cacheHitRate: Gauge<string>;
  private readonly eventProcessingLatency: Histogram<string>;
  private readonly apiResponseTime: Histogram<string>;

  // System metrics
  private readonly activeConnections: Gauge<string>;
  private readonly memoryUsage: Gauge<string>;
  private readonly errorRate: Counter<string>;

  private constructor() {
    // Enable default metrics collection
    collectDefaultMetrics({ prefix: 'finance_' });

    // Business metrics
    this.invoiceProcessingTime = new Histogram({
      name: 'finance_invoice_processing_duration_seconds',
      help: 'Time taken to process invoices',
      labelNames: ['type', 'status'],
      buckets: [0.1, 0.5, 1, 2, 5, 10, 30, 60]
    });

    this.journalPostingCount = new Counter({
      name: 'finance_journal_postings_total',
      help: 'Total number of journal postings',
      labelNames: ['type', 'status']
    });

    this.reconciliationSuccessRate = new Gauge({
      name: 'finance_reconciliation_success_rate',
      help: 'Bank reconciliation success rate',
      labelNames: ['bank_account']
    });

    this.aiConfidenceScore = new Histogram({
      name: 'finance_ai_confidence_score',
      help: 'AI confidence scores for automated processing',
      labelNames: ['operation'],
      buckets: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    });

    this.auditTrailIntegrity = new Gauge({
      name: 'finance_audit_trail_integrity',
      help: 'Audit trail integrity score (1.0 = perfect)',
      labelNames: ['period']
    });

    // Performance metrics
    this.databaseQueryDuration = new Histogram({
      name: 'finance_database_query_duration_seconds',
      help: 'Database query execution time',
      labelNames: ['operation', 'table'],
      buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1, 5]
    });

    this.cacheHitRate = new Gauge({
      name: 'finance_cache_hit_rate',
      help: 'Cache hit rate percentage',
      labelNames: ['cache_type']
    });

    this.eventProcessingLatency = new Histogram({
      name: 'finance_event_processing_latency_seconds',
      help: 'Time to process domain events',
      labelNames: ['event_type'],
      buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
    });

    this.apiResponseTime = new Histogram({
      name: 'finance_api_response_time_seconds',
      help: 'API endpoint response time',
      labelNames: ['method', 'endpoint', 'status_code'],
      buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10]
    });

    // System metrics
    this.activeConnections = new Gauge({
      name: 'finance_active_connections',
      help: 'Number of active connections',
      labelNames: ['type']
    });

    this.memoryUsage = new Gauge({
      name: 'finance_memory_usage_bytes',
      help: 'Memory usage in bytes',
      labelNames: ['type']
    });

    this.errorRate = new Counter({
      name: 'finance_errors_total',
      help: 'Total number of errors',
      labelNames: ['type', 'component']
    });
  }

  public static getInstance(): MetricsService {
    if (!MetricsService.instance) {
      MetricsService.instance = new MetricsService();
    }
    return MetricsService.instance;
  }

  // Business metrics methods
  public recordInvoiceProcessingTime(type: string, status: string, duration: number): void {
    this.invoiceProcessingTime.observe({ type, status }, duration);
  }

  public incrementJournalPosting(type: string, status: string): void {
    this.journalPostingCount.inc({ type, status });
  }

  public setReconciliationSuccessRate(bankAccount: string, rate: number): void {
    this.reconciliationSuccessRate.set({ bank_account: bankAccount }, rate);
  }

  public recordAIConfidenceScore(operation: string, score: number): void {
    this.aiConfidenceScore.observe({ operation }, score);
  }

  public setAuditTrailIntegrity(period: string, integrity: number): void {
    this.auditTrailIntegrity.set({ period }, integrity);
  }

  // Performance metrics methods
  public recordDatabaseQueryDuration(operation: string, table: string, duration: number): void {
    this.databaseQueryDuration.observe({ operation, table }, duration);
  }

  public setCacheHitRate(cacheType: string, rate: number): void {
    this.cacheHitRate.set({ cache_type: cacheType }, rate);
  }

  public recordEventProcessingLatency(eventType: string, latency: number): void {
    this.eventProcessingLatency.observe({ event_type: eventType }, latency);
  }

  public recordApiResponseTime(method: string, endpoint: string, statusCode: number, duration: number): void {
    this.apiResponseTime.observe({ method, endpoint, status_code: statusCode.toString() }, duration);
  }

  // System metrics methods
  public setActiveConnections(type: string, count: number): void {
    this.activeConnections.set({ type }, count);
  }

  public setMemoryUsage(type: string, bytes: number): void {
    this.memoryUsage.set({ type }, bytes);
  }

  public incrementErrorCount(type: string, component: string): void {
    this.errorRate.inc({ type, component });
  }

  // Utility methods
  public async getMetrics(): Promise<string> {
    return register.metrics();
  }

  public async getRegistry(): Promise<string> {
    return JSON.stringify(register.getMetricsAsJSON());
  }

  public reset(): void {
    register.resetMetrics();
  }
}

export default MetricsService;