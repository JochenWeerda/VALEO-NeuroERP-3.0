"use strict";
/**
 * Monitoring Service - MSOA Implementation nach Clean Architecture
 * Infrastructure Layer Service migrated to VALEO-NeuroERP-3.0
 * External monitoring and health check orchestration
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.MonitoringService = void 0;
exports.registerMonitoringService = registerMonitoringService;
const di_container_1 = require("@valero-neuroerp/utilities/src/di-container");
// ===== MONITORING SERVICE nach Clean Architecture =====
class MonitoringService {
    monitors = new Map();
    alerts = new Map();
    healthHistory = new Map();
    startedMonitoring = false;
    constructor() {
        console.log('[MONITORING SERVICE] Initializing Monitoring Service nach Clean Architecture...');
        this.initializeMonitoringService();
    }
    /**
     * Initialize Monitoring Service
     */
    initializeMonitoringService() {
        console.log('[MONITORING INIT] Monitoring service initialization nach infrastructure requirements...');
        try {
            this.setupDefaultMonitors();
            this.startMonitoringProcess();
            console.log('[MONITORING INIT] ✓ Monitoring service initialized nach Clean Architecture');
        }
        catch (error) {
            console.error('[MONITORING INIT] Monitoring service initialization failed:', error);
            throw new Error(`Monitoring service configuration failed: ${error}`);
        }
    }
    /**
     * Setup Default Monitors nach System Requirements
     */
    setupDefaultMonitors() {
        console.log('[MONITORING SETUP] Setting up default monitors nach infrastructure architecture...');
        // Architecture: System Health Monitor
        this.createHealthMonitor();
        // Architecture: Performance Monitor
        this.createPerformanceMonitor();
        // Architecture: Resource Monitor
        this.createResourceMonitor();
        console.log('[MONITORING SETUP] ✓ Default monitors configured nach infrastructure model');
    }
    /**
     * Create Health Monitor
     */
    createHealthMonitor() {
        const healthMonitor = {
            id: 'health_monitor_001',
            name: 'System Health Monitor',
            type: 'HEALTH',
            target: '/health',
            status: 'ACTIVE',
            intervalSeconds: 30,
            lastCheck: new Date(),
            metrics: [
                {
                    name: 'service_available',
                    expression: 'up',
                    unit: 'boolean',
                    description: 'Service availability status'
                }
            ],
            thresholds: [
                {
                    metric: 'service_available',
                    condition: 'LESS_THAN',
                    value: 1,
                    severity: 'CRITICAL'
                }
            ]
        };
        this.monitors.set('health_monitor_001', healthMonitor);
        console.log('[MONITORING] ✓ Health monitor created nach infrastructure architecture');
    }
    /**
     * Create Performance Monitor
     */
    createPerformanceMonitor() {
        const perfMonitor = {
            id: 'performance_monitor_001',
            name: 'Performance Monitor',
            type: 'PERFORMANCE',
            target: '/metrics',
            status: 'ACTIVE',
            intervalSeconds: 60,
            lastCheck: new Date(),
            metrics: [
                {
                    name: 'request_duration',
                    expression: 'http_request_duration_seconds',
                    unit: 'seconds',
                    description: 'HTTP request duration'
                },
                {
                    name: 'request_rate',
                    expression: 'rate(http_requests_total[1m])',
                    unit: 'req/sec',
                    description: 'Request rate'
                }
            ],
            thresholds: [
                {
                    metric: 'request_duration',
                    condition: 'GREATER_THAN',
                    value: 5,
                    severity: 'WARNING'
                }
            ]
        };
        this.monitors.set('performance_monitor_001', perfMonitor);
        console.log('[MONITORING] ✓ Performance monitor created nach infrastructure architecture');
    }
    /**
     * Create Resource Monitor
     */
    createResourceMonitor() {
        const resourceMonitor = {
            id: 'resource_monitor_001',
            name: 'Resource Monitor',
            type: 'RESOURCE',
            target: '/system/metrics',
            status: 'ACTIVE',
            intervalSeconds: 120,
            lastCheck: new Date(),
            metrics: [
                {
                    name: 'cpu_usage',
                    expression: 'cpu_usage_percent',
                    unit: 'percent',
                    description: 'CPU usage percentage'
                },
                {
                    name: 'memory_usage',
                    expression: 'memory_usage_percent',
                    unit: 'percent',
                    description: 'Memory usage percentage'
                }
            ],
            thresholds: [
                {
                    metric: 'cpu_usage',
                    condition: 'GREATER_THAN',
                    value: 80,
                    severity: 'WARNING'
                },
                {
                    metric: 'memory_usage',
                    condition: 'GREATER_THAN',
                    value: 90,
                    severity: 'CRITICAL'
                }
            ]
        };
        this.monitors.set('resource_monitor_001', resourceMonitor);
        console.log('[MONITORING] ✓ Resource monitor created nach infrastructure architecture');
    }
    /**
     * Start Monitoring Process
     */
    startMonitoringProcess() {
        console.log('[MONITORING START] Starting monitoring process nach infrastructure architecture...');
        if (this.startedMonitoring) {
            console.log('[MONITORING START] ✓ Monitoring already running');
            return;
        }
        // Architecture: Start periodic monitoring
        setInterval(async () => {
            await this.runHealthChecks();
        }, 10000); // Every 10 seconds
        console.log('[MONITORING START] ✓ Monitoring process started nach infrastructure architecture');
    }
    /**
     * Run Health Checks
     */
    async runHealthChecks() {
        console.log('[MONITORING CHECKS] Running health checks nach infrastructure monitoring...');
        for (const [monitorId, monitor] of this.monitors.entries()) {
            try {
                const healthResult = await this.checkServiceHealth(monitor);
                const serviceId = monitor.target;
                // Store health check result
                const existingHistory = this.healthHistory.get(serviceId) || [];
                const newHistory = [healthResult, ...existingHistory].slice(0, 100); // Keep last 100
                this.healthHistory.set(serviceId, newHistory);
                // Check for alerts
                await this.processAlerts(monitor, healthResult);
                console.log(`[MONITORING CHECK] ✓ Service ${serviceId} health: ${healthResult.status}`);
            }
            catch (error) {
                console.error(`[MONITORING CHECK] Error checking ${monitorId}:`, error);
            }
        }
    }
    /**
     * Check Service Health
     */
    async checkServiceHealth(monitor) {
        const startTime = Date.now();
        try {
            // Architecture: Mock health check (in production: actual health check calls)
            const mockMetrics = {
                service_available: Math.random() > 0.1 ? 1 : 0,
                request_duration: Math.random() * 5,
                cpu_usage: Math.random() * 100,
                memory_usage: Math.random() * 100
            };
            const responseTime = Date.now() - startTime;
            const status = mockMetrics.service_available > 0 ?
                (mockMetrics.cpu_usage > 90 || mockMetrics.memory_usage > 90 ? 'DEGRADED' : 'HEALTHY') :
                'UNHEALTHY';
            return {
                serviceId: monitor.target,
                status: status,
                metrics: mockMetrics,
                timestamp: new Date(),
                responseTime
            };
        }
        catch (error) {
            console.error('[MONITORING HEALTH] Service health check failed:', error);
            return {
                serviceId: monitor.target,
                status: 'UNHEALTHY',
                metrics: {},
                timestamp: new Date(),
                responseTime: Date.now() - startTime
            };
        }
    }
    /**
     * Process Alerts
     */
    async processAlerts(monitor, healthResult) {
        for (const threshold of monitor.thresholds) {
            const metricValue = healthResult.metrics[threshold.metric];
            if (metricValue === undefined)
                continue;
            const shouldAlert = this.evaluateThreshold(metricValue, threshold);
            if (shouldAlert) {
                await this.createAlert(monitor, threshold, metricValue, healthResult);
            }
        }
    }
    /**
     * Create Alert
     */
    async createAlert(monitor, threshold, metricValue, healthResult) {
        const alertId = this.generateAlertId();
        const alert = {
            id: alertId,
            title: `${monitor.name} - ${threshold.severity} Alert`,
            description: `Metric ${threshold.metric} value ${metricValue} violates threshold ${threshold.value}`,
            severity: threshold.severity,
            service: monitor.target,
            metric: threshold.metric,
            value: metricValue,
            threshold: threshold.value,
            timestamp: new Date(),
            acknowledged: false
        };
        this.alerts.set(alertId, alert);
        console.log(`[MONITORING ALERT] ${threshold.severity} alert created nach infrastructure architecture: ${alertId}`);
    }
    /**
     * Evaluate Threshold
     */
    evaluateThreshold(value, threshold) {
        switch (threshold.condition) {
            case 'GREATER_THAN':
                return value > threshold.value;
            case 'LESS_THAN':
                return value < threshold.value;
            case 'EQUAL':
                return value === threshold.value;
            default:
                return false;
        }
    }
    /**
     * Get Monitoring Statistics
     */
    async getStatistics() {
        const activeAlerts = Array.from(this.alerts.values()).filter(alert => !alert.acknowledged);
        const serviceHealthStatus = {};
        for (const [serviceId, healthHistory] of this.healthHistory.entries()) {
            const latestHealth = healthHistory[0];
            serviceHealthStatus[serviceId] = latestHealth?.status || 'UNKNOWN';
        }
        const alertBreakdown = Array.from(this.alerts.values()).reduce((acc, alert) => {
            acc[alert.severity] = (acc[alert.severity] || 0) + 1;
            return acc;
        }, {});
        return {
            totalMonitors: this.monitors.size,
            activeAlerts: activeAlerts.length,
            serviceHealthStatus,
            alertBreakdown
        };
    }
    /**
     * Health check
     */
    async healthCheck() {
        try {
            console.log('[MONITORING HEALTH] Checking monitoring service health nach infrastructure architecture...');
            const monitorsCount = this.monitors.size;
            const isHealthy = monitorsCount > 0;
            if (!isHealthy) {
                console.error('[MONITORING HEALTH] No monitors configured');
                return false;
            }
            console.log(`[MONITORING HEALTH] ✓ Monitoring service health validated nach infrastructure architecture (${monitorsCount} monitors)`);
            return true;
        }
        catch (error) {
            console.error('[MONITORING HEALTH] Monitoring service health check failed:', error);
            return false;
        }
    }
    // Helper methods
    generateAlertId() {
        const id = 'alert_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id;
    }
}
exports.MonitoringService = MonitoringService;
/**
 * Register Monitoring Service in DI Container
 */
function registerMonitoringService() {
    console.log('[MONITORING REGISTRATION] Registering Monitoring Service nach infrastructure architecture...');
    di_container_1.DIContainer.register('MonitoringService', new MonitoringService(), {
        singleton: true,
        dependencies: []
    });
    console.log('[MONITORING REGISTRATION] ✅ Monitoring Service registered successfully nach infrastructure architecture');
}
//# sourceMappingURL=monitoring-service.js.map