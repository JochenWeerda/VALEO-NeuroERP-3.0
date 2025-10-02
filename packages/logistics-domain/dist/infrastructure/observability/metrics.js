"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LogisticsMetrics = void 0;
const prom_client_1 = require("prom-client");
class LogisticsMetrics {
    constructor() {
        this.registry = new prom_client_1.Registry();
        (0, prom_client_1.collectDefaultMetrics)({ register: this.registry });
        this.shipmentsCounter = new prom_client_1.Counter({
            name: 'logistics_shipments_total',
            help: 'Count of shipments orchestrated',
            registers: [this.registry],
            labelNames: ['tenant', 'status'],
        });
        this.dispatchGauge = new prom_client_1.Gauge({
            name: 'logistics_dispatch_active_assignments',
            help: 'Active dispatch assignments per tenant',
            registers: [this.registry],
            labelNames: ['tenant'],
        });
        this.etaDeviationHistogram = new prom_client_1.Histogram({
            name: 'logistics_eta_deviation_minutes',
            help: 'ETA deviation distribution',
            registers: [this.registry],
            labelNames: ['tenant'],
            buckets: [1, 5, 10, 15, 30, 60],
        });
    }
    metrics() {
        return this.registry.metrics();
    }
}
exports.LogisticsMetrics = LogisticsMetrics;
//# sourceMappingURL=metrics.js.map