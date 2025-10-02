"use strict";
/**
 * VALEO NeuroERP 3.0 - Comprehensive Observability Service
 *
 * Enterprise-grade monitoring, alerting, and observability
 */
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
var __setFunctionName = (this && this.__setFunctionName) || function (f, name, prefix) {
    if (typeof name === "symbol") name = name.description ? "[".concat(name.description, "]") : "";
    return Object.defineProperty(f, "name", { configurable: true, value: prefix ? "".concat(prefix, " ", name) : name });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ObservabilityService = void 0;
const inversify_1 = require("inversify");
const metrics_service_1 = require("./metrics-service");
let ObservabilityService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var ObservabilityService = _classThis = class {
        constructor(eventBus) {
            this.eventBus = eventBus;
            this.metrics = new metrics_service_1.InventoryMetricsService();
            this.alertRules = new Map();
            this.sloDefinitions = new Map();
            this.dashboards = new Map();
            this.config = this.getDefaultConfig();
            this.initializeObservability();
        }
        /**
         * Initialize comprehensive observability
         */
        async initializeObservability() {
            await this.setupMetricsCollection();
            await this.setupDistributedTracing();
            await this.setupLogAggregation();
            await this.setupAlerting();
            await this.setupDashboards();
            await this.setupSLOMonitoring();
        }
        /**
         * Setup advanced metrics collection
         */
        async setupMetricsCollection() {
            // Custom business metrics
            this.metrics.setBusinessMetricsEnabled(true);
            // Performance metrics
            this.metrics.setPerformanceMetricsEnabled(true);
            // System metrics
            this.metrics.setSystemMetricsEnabled(true);
            // Custom application metrics
            this.registerCustomMetrics();
        }
        /**
         * Setup distributed tracing
         */
        async setupDistributedTracing() {
            // Configure Jaeger tracing
            // This would integrate with the existing OTel setup
            console.log('Distributed tracing configured');
        }
        /**
         * Setup log aggregation
         */
        async setupLogAggregation() {
            // Configure Elasticsearch indexing
            // Setup log shipping from all services
            console.log('Log aggregation configured');
        }
        /**
         * Setup alerting system
         */
        async setupAlerting() {
            // Default alert rules
            const defaultRules = this.getDefaultAlertRules();
            for (const rule of defaultRules) {
                await this.createAlertRule(rule);
            }
            // Business-specific alerts
            const businessRules = this.getBusinessAlertRules();
            for (const rule of businessRules) {
                await this.createAlertRule(rule);
            }
        }
        /**
         * Setup dashboards
         */
        async setupDashboards() {
            const dashboards = [
                this.createSystemDashboard(),
                this.createBusinessDashboard(),
                this.createAlertingDashboard()
            ];
            for (const dashboard of dashboards) {
                await this.createDashboard(dashboard);
            }
        }
        /**
         * Setup SLO monitoring
         */
        async setupSLOMonitoring() {
            const slos = this.getDefaultSLOs();
            for (const slo of slos) {
                await this.createSLO(slo);
            }
        }
        /**
         * Register custom metrics
         */
        registerCustomMetrics() {
            // Business KPIs
            this.metrics.registerGauge('inventory_accuracy', 'Inventory accuracy percentage');
            this.metrics.registerGauge('order_fill_rate', 'Order fill rate percentage');
            this.metrics.registerGauge('on_time_delivery', 'On-time delivery percentage');
            // Performance metrics
            this.metrics.registerHistogram('api_request_duration', 'API request duration', ['method', 'endpoint']);
            this.metrics.registerHistogram('database_query_duration', 'Database query duration', ['operation']);
            this.metrics.registerHistogram('business_transaction_duration', 'Business transaction duration', ['type']);
            // Error metrics
            this.metrics.registerCounter('business_errors', 'Business logic errors', ['type', 'component']);
            this.metrics.registerCounter('integration_errors', 'Integration errors', ['system', 'operation']);
        }
        /**
         * Create alert rule
         */
        async createAlertRule(rule) {
            this.alertRules.set(rule.alertName, rule);
            // In production, this would send to AlertManager
            console.log(`Alert rule created: ${rule.alertName}`);
        }
        /**
         * Create SLO definition
         */
        async createSLO(slo) {
            this.sloDefinitions.set(slo.name, slo);
            // Create associated alert rules
            await this.createAlertRule(slo.alerting.fastBurn);
            await this.createAlertRule(slo.alerting.slowBurn);
            console.log(`SLO created: ${slo.name}`);
        }
        /**
         * Create dashboard
         */
        async createDashboard(dashboard) {
            this.dashboards.set(dashboard.title, dashboard);
            // In production, this would create/update Grafana dashboard
            console.log(`Dashboard created: ${dashboard.title}`);
        }
        /**
         * Log structured entry
         */
        async logEntry(entry) {
            // In production, this would send to Elasticsearch
            console.log(`[${entry.level.toUpperCase()}] ${entry.service}:${entry.component} - ${entry.message}`, entry.fields);
        }
        /**
         * Record trace span
         */
        async recordSpan(span) {
            // In production, this would send to Jaeger
            console.log(`Trace span recorded: ${span.operation} (${span.duration}ms)`);
        }
        /**
         * Get system health status
         */
        async getSystemHealth() {
            // Mock health check - in production, this would query actual services
            return {
                overall: 'healthy',
                services: {
                    'inventory-service': { status: 'up', responseTime: 45, lastCheck: new Date() },
                    'finance-service': { status: 'up', responseTime: 32, lastCheck: new Date() },
                    'database': { status: 'up', responseTime: 12, lastCheck: new Date() }
                },
                alerts: {
                    active: 2,
                    critical: 0,
                    warning: 2
                },
                slos: {
                    'api_availability': { objective: 99.9, current: 99.95, status: 'healthy' },
                    'order_processing': { objective: 99.5, current: 99.7, status: 'healthy' }
                }
            };
        }
        /**
         * Get performance metrics
         */
        async getPerformanceMetrics(timeRange) {
            // Mock performance data - in production, this would query Prometheus
            return {
                throughput: {
                    requestsPerSecond: 1250,
                    transactionsPerHour: 4500,
                    ordersPerDay: 850
                },
                latency: {
                    p50: 45,
                    p95: 120,
                    p99: 250
                },
                errorRates: {
                    overall: 0.05,
                    byService: {
                        'inventory': 0.03,
                        'finance': 0.07,
                        'shipping': 0.02
                    }
                },
                resourceUsage: {
                    cpu: 65,
                    memory: 78,
                    disk: 45,
                    network: 32
                }
            };
        }
        /**
         * Get business metrics
         */
        async getBusinessMetrics(timeRange) {
            // Mock business metrics
            return {
                inventory: {
                    accuracy: 99.2,
                    turnover: 12.5,
                    stockoutRate: 2.1,
                    overstockValue: 125000
                },
                orders: {
                    fillRate: 97.8,
                    onTimeDelivery: 96.5,
                    returnRate: 3.2,
                    averageOrderValue: 245
                },
                finance: {
                    dso: 24,
                    dio: 18,
                    dpo: 32,
                    cashConversionCycle: 10
                },
                quality: {
                    defectRate: 0.8,
                    customerSatisfaction: 4.6,
                    auditScore: 98
                }
            };
        }
        // Private helper methods
        getDefaultConfig() {
            return {
                prometheus: {
                    endpoint: process.env.PROMETHEUS_ENDPOINT || 'http://localhost:9090',
                    scrapeInterval: 15,
                    externalLabels: {
                        environment: process.env.NODE_ENV || 'development',
                        region: 'eu-central-1'
                    }
                },
                jaeger: {
                    endpoint: process.env.JAEGER_ENDPOINT || 'http://localhost:14268/api/traces',
                    serviceName: 'valero-neuroerp-inventory',
                    tags: {
                        version: '3.0.0'
                    }
                },
                elasticsearch: {
                    nodes: (process.env.ELASTICSEARCH_NODES || 'http://localhost:9200').split(','),
                    indexPrefix: 'valero-neuroerp',
                    retention: {
                        hot: 7,
                        warm: 30,
                        cold: 365
                    }
                },
                grafana: {
                    endpoint: process.env.GRAFANA_ENDPOINT || 'http://localhost:3000',
                    apiKey: process.env.GRAFANA_API_KEY || '',
                    dashboards: {
                        system: 'system-overview',
                        business: 'business-kpis',
                        alerts: 'alerting-dashboard'
                    }
                },
                alertmanager: {
                    endpoint: process.env.ALERTMANAGER_ENDPOINT || 'http://localhost:9093',
                    defaultReceiver: 'devops-team',
                    routes: []
                }
            };
        }
        getDefaultAlertRules() {
            return [
                {
                    alertName: 'HighErrorRate',
                    condition: 'rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05',
                    duration: '5m',
                    labels: { severity: 'critical', team: 'platform' },
                    annotations: {
                        summary: 'High error rate detected',
                        description: 'Error rate is {{ $value }}% which is above the threshold of 5%'
                    },
                    severity: 'critical',
                    team: 'platform',
                    service: 'api'
                },
                {
                    alertName: 'HighLatency',
                    condition: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2',
                    duration: '5m',
                    labels: { severity: 'warning', team: 'platform' },
                    annotations: {
                        summary: 'High latency detected',
                        description: '95th percentile latency is {{ $value }}s which is above the threshold of 2s'
                    },
                    severity: 'warning',
                    team: 'platform',
                    service: 'api'
                }
            ];
        }
        getBusinessAlertRules() {
            return [
                {
                    alertName: 'LowInventoryAccuracy',
                    condition: 'inventory_accuracy < 95',
                    duration: '15m',
                    labels: { severity: 'warning', team: 'warehouse' },
                    annotations: {
                        summary: 'Low inventory accuracy',
                        description: 'Inventory accuracy dropped to {{ $value }}%'
                    },
                    severity: 'warning',
                    team: 'warehouse',
                    service: 'inventory'
                },
                {
                    alertName: 'HighStockoutRate',
                    condition: 'stockout_rate > 5',
                    duration: '10m',
                    labels: { severity: 'critical', team: 'warehouse' },
                    annotations: {
                        summary: 'High stockout rate',
                        description: 'Stockout rate is {{ $value }}% which may impact customer satisfaction'
                    },
                    severity: 'critical',
                    team: 'warehouse',
                    service: 'inventory'
                }
            ];
        }
        getDefaultSLOs() {
            return [
                {
                    name: 'api_availability',
                    objective: 99.9,
                    window: '30d',
                    indicators: [{
                            name: 'http_availability',
                            query: 'http_requests_total',
                            goodQuery: 'http_requests_total{status!~"5.."}',
                            totalQuery: 'http_requests_total'
                        }],
                    alerting: {
                        fastBurn: {
                            alertName: 'APIAvailabilityFastBurn',
                            condition: 'http_availability_slo_fast_burn > 0',
                            duration: '5m',
                            labels: { severity: 'critical', slo: 'api_availability' },
                            annotations: {
                                summary: 'API availability SLO fast burn',
                                description: 'API availability is burning fast towards breach'
                            },
                            severity: 'critical',
                            team: 'platform',
                            service: 'api'
                        },
                        slowBurn: {
                            alertName: 'APIAvailabilitySlowBurn',
                            condition: 'http_availability_slo_slow_burn > 0',
                            duration: '1h',
                            labels: { severity: 'warning', slo: 'api_availability' },
                            annotations: {
                                summary: 'API availability SLO slow burn',
                                description: 'API availability is burning slowly towards breach'
                            },
                            severity: 'warning',
                            team: 'platform',
                            service: 'api'
                        }
                    }
                }
            ];
        }
        createSystemDashboard() {
            return {
                title: 'System Overview',
                description: 'Comprehensive system monitoring dashboard',
                tags: ['system', 'infrastructure', 'monitoring'],
                panels: [
                    {
                        id: 1,
                        title: 'System Health',
                        type: 'singlestat',
                        targets: [{
                                expr: 'up{job="inventory-service"}',
                                legendFormat: 'Service Status',
                                refId: 'A'
                            }],
                        gridPos: { h: 8, w: 12, x: 0, y: 0 }
                    },
                    {
                        id: 2,
                        title: 'API Response Time',
                        type: 'graph',
                        targets: [{
                                expr: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))',
                                legendFormat: '95th percentile',
                                refId: 'A'
                            }],
                        gridPos: { h: 8, w: 12, x: 12, y: 0 }
                    }
                ],
                variables: [
                    {
                        name: 'service',
                        label: 'Service',
                        type: 'query',
                        query: 'label_values(service)'
                    }
                ],
                timeRange: {
                    from: 'now-1h',
                    to: 'now'
                }
            };
        }
        createBusinessDashboard() {
            return {
                title: 'Business KPIs',
                description: 'Key business performance indicators',
                tags: ['business', 'kpi', 'metrics'],
                panels: [
                    {
                        id: 1,
                        title: 'Inventory Accuracy',
                        type: 'singlestat',
                        targets: [{
                                expr: 'inventory_accuracy',
                                legendFormat: 'Accuracy %',
                                refId: 'A'
                            }],
                        gridPos: { h: 8, w: 8, x: 0, y: 0 }
                    },
                    {
                        id: 2,
                        title: 'Order Fill Rate',
                        type: 'singlestat',
                        targets: [{
                                expr: 'order_fill_rate',
                                legendFormat: 'Fill Rate %',
                                refId: 'A'
                            }],
                        gridPos: { h: 8, w: 8, x: 8, y: 0 }
                    },
                    {
                        id: 3,
                        title: 'On-Time Delivery',
                        type: 'singlestat',
                        targets: [{
                                expr: 'on_time_delivery',
                                legendFormat: 'OTD %',
                                refId: 'A'
                            }],
                        gridPos: { h: 8, w: 8, x: 16, y: 0 }
                    }
                ],
                variables: [],
                timeRange: {
                    from: 'now-24h',
                    to: 'now'
                }
            };
        }
        createAlertingDashboard() {
            return {
                title: 'Alerting Dashboard',
                description: 'Active alerts and alert trends',
                tags: ['alerting', 'monitoring', 'incidents'],
                panels: [
                    {
                        id: 1,
                        title: 'Active Alerts',
                        type: 'table',
                        targets: [{
                                expr: 'ALERTS{alertstate="firing"}',
                                legendFormat: '{{ alertname }}',
                                refId: 'A'
                            }],
                        gridPos: { h: 12, w: 24, x: 0, y: 0 }
                    }
                ],
                variables: [],
                timeRange: {
                    from: 'now-1h',
                    to: 'now'
                }
            };
        }
    };
    __setFunctionName(_classThis, "ObservabilityService");
    (() => {
        const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
        __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
        ObservabilityService = _classThis = _classDescriptor.value;
        if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
        __runInitializers(_classThis, _classExtraInitializers);
    })();
    return ObservabilityService = _classThis;
})();
exports.ObservabilityService = ObservabilityService;
//# sourceMappingURL=observability-service.js.map