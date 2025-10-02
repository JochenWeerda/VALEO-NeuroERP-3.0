"use strict";
/**
 * VALEO NeuroERP 3.0 - Inventory Metrics Service
 *
 * Metrics service for inventory domain observability.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryMetricsService = void 0;
class InventoryMetricsService {
    constructor() {
        this.counters = new Map();
        this.gauges = new Map();
        this.histograms = new Map();
    }
    incrementCounter(name, labels) {
        const key = this.getKey(name, labels);
        this.counters.set(key, (this.counters.get(key) || 0) + 1);
    }
    recordGauge(name, value, labels) {
        const key = this.getKey(name, labels);
        this.gauges.set(key, value);
    }
    recordHistogram(name, value, labels) {
        const key = this.getKey(name, labels);
        const values = this.histograms.get(key) || [];
        values.push(value);
        this.histograms.set(key, values);
    }
    recordApiResponseTime(name, duration, labels) {
        this.recordHistogram(name, duration, labels);
    }
    incrementErrorCount(name, labels) {
        this.incrementCounter(name, labels);
    }
    recordInvoiceProcessingTime(name, duration, labels) {
        this.recordHistogram(name, duration, labels);
    }
    recordPutawayTime(name, duration, labels) {
        this.recordHistogram(name, duration, labels);
    }
    incrementPutawayTasks(name, labels) {
        this.incrementCounter(name, labels);
    }
    recordDatabaseQueryDuration(name, duration, labels) {
        this.recordHistogram(name, duration, labels);
    }
    incrementPickTasks(name, labels) {
        this.incrementCounter(name, labels);
    }
    incrementPackTasks(name, labels) {
        this.incrementCounter(name, labels);
    }
    incrementReturns(name, labels) {
        this.incrementCounter(name, labels);
    }
    incrementQuarantines(name, labels) {
        this.incrementCounter(name, labels);
    }
    incrementRoboticsTasks(name, labels) {
        this.incrementCounter(name, labels);
    }
    incrementAnomaliesDetected(name, labels) {
        this.incrementCounter(name, labels);
    }
    incrementCycleCounts(name, labels) {
        this.incrementCounter(name, labels);
    }
    incrementTraceabilityEvents(name, labels) {
        this.incrementCounter(name, labels);
    }
    incrementAIRecommendations(name, labels) {
        this.incrementCounter(name, labels);
    }
    incrementEDITransactions(name, labels) {
        this.incrementCounter(name, labels);
    }
    setBusinessMetricsEnabled(enabled) {
        // Implementation for business metrics toggle
    }
    setPerformanceMetricsEnabled(enabled) {
        // Implementation for performance metrics toggle
    }
    setSystemMetricsEnabled(enabled) {
        // Implementation for system metrics toggle
    }
    registerGauge(name, value, labels) {
        this.recordGauge(name, value, labels);
    }
    registerHistogram(name, value, labels) {
        this.recordHistogram(name, value, labels);
    }
    registerCounter(name, value, labels) {
        this.incrementCounter(name, labels);
    }
    getMetrics() {
        return JSON.stringify({
            counters: Object.fromEntries(this.counters),
            gauges: Object.fromEntries(this.gauges),
            histograms: Object.fromEntries(this.histograms)
        });
    }
    getKey(name, labels) {
        if (!labels)
            return name;
        const labelStr = Object.entries(labels)
            .map(([k, v]) => `${k}=${v}`)
            .join(',');
        return `${name}{${labelStr}}`;
    }
}
exports.InventoryMetricsService = InventoryMetricsService;
exports.default = InventoryMetricsService;
//# sourceMappingURL=metrics-service.js.map