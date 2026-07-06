/**
 * Monitoring Service - MSOA Implementation nach Clean Architecture
 * Infrastructure Layer Service migrated to VALEO-NeuroERP-3.0
 * External monitoring and health check orchestration
 */

import { DIContainer } from '@valeo-neuroerp-3.0/packages/utilities/src/di-container';
import { Brand } from '@valeo-neuroerp-3.0/packages/data-models/src/branded-types';

// ===== BRANDED TYPES =====
export type MonitorId = Brand<string, 'MonitorId'>;
export type ServiceId = Brand<string, 'ServiceId'>;
export type AlertId = Brand<string, 'AlertId'>;

// ===== DOMAIN ENTITIES =====
export interface SystemMonitor {
    readonly id: MonitorId;
    readonly name: string;
    readonly type: 'HEALTH' | 'PERFORMANCE' | 'RESOURCE' | 'BUSINESS';
    readonly target: string;
    readonly metrics: MonitorMetric[];
    readonly thresholds: AlertThreshold[];
    readonly status: 'ACTIVE' | 'DISABLED' | 'ERROR';
    readonly intervalSeconds: number;
    readonly lastCheck: Date;
}

export interface MonitorMetric {
    readonly name: string;
    readonly expression: string;
    readonly unit: string;
    readonly description: string;
}

export interface AlertThreshold {
    readonly metric: string;
    readonly condition: 'GREATER_THAN' | 'LESS_THAN' | 'EQUAL';
    readonly value: number;
    readonly severity: 'INFO' | 'WARNING' | 'CRITICAL';
}

export interface HealthCheckResult {
    readonly serviceId: ServiceId;
    readonly status: 'HEALTHY' | 'UNHEALTHY' | 'DEGRADED';
    readonly metrics: Record<string, number>;
    readonly timestamp: Date;
    readonly responseTime: number;
}

export interface SystemAlert {
    readonly id: AlertId;
    readonly title: string;
    readonly description: string;
    readonly severity: 'INFO' | 'WARNING' | 'CRITICAL';
    readonly service: string;
    readonly metric: string;
    readonly value: number;
    readonly threshold: number;
    readonly timestamp: Date;
    readonly acknowledged: boolean;
}

// ===== MONITORING SERVICE nach Clean Architecture =====
export class MonitoringService {
    private readonly monitors: Map<MonitorId, SystemMonitor> = new Map();
    private readonly alerts: Map<AlertId, SystemAlert> = new Map();
    private readonly healthHistory: Map<ServiceId, HealthCheckResult[]> = new Map();
    private readonly startedMonitoring: boolean = false;

    constructor() {
        console.log('[MONITORING SERVICE] Initializing Monitoring Service nach Clean Architecture...');
        this.initializeMonitoringService();
    }

    /**
     * Initialize Monitoring Service
     */
    private initializeMonitoringService(): void {
        console.log('[MONITORING INIT] Monitoring service initialization nach infrastructure requirements...');
        
        try {
            this.setupDefaultMonitors();
            this.startMonitoringProcess();
            console.log('[MONITORING INIT] ✓ Monitoring service initialized nach Clean Architecture');
        } catch (error) {
            console.error('[MONITORING INIT] Monitoring service initialization failed:', error);
            throw new Error(`Monitoring service configuration failed: ${error}`);
        }
    }

    /**
     * Setup Default Monitors nach System Requirements
     */
    private setupDefaultMonitors(): void {
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
    private createHealthMonitor(): void {
        const healthMonitor: SystemMonitor = {
            id: 'health_monitor_001' as MonitorId,
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

        this.monitors.set('health_monitor_001' as MonitorId, healthMonitor);
        console.log('[MONITORING] ✓ Health monitor created nach infrastructure architecture');
    }

    /**
     * Create Performance Monitor
     */
    private createPerformanceMonitor(): void {
        const perfMonitor: SystemMonitor = {
            id: 'performance_monitor_001' as MonitorId,
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

        this.monitors.set('performance_monitor_001' as MonitorId, perfMonitor);
        console.log('[MONITORING] ✓ Performance monitor created nach infrastructure architecture');
    }

    /**
     * Create Resource Monitor
     */
    private createResourceMonitor(): void {
        const resourceMonitor: SystemMonitor = {
            id: 'resource_monitor_001' as MonitorId,
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

        this.monitors.set('resource_monitor_001' as MonitorId, resourceMonitor);
        console.log('[MONITORING] ✓ Resource monitor created nach infrastructure architecture');
    }

    /**
     * Start Monitoring Process
     */
    private startMonitoringProcess(): void {
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
    private async runHealthChecks(): Promise<void> {
        console.log('[MONITORING CHECKS] Running health checks nach infrastructure monitoring...');
        
        for (const [monitorId, monitor] of this.monitors.entries()) {
            try {
                const healthResult = await this.checkServiceHealth(monitor);
                const serviceId = monitor.target as ServiceId;
                
                // Store health check result
                const existingHistory = this.healthHistory.get(serviceId) || [];
                const newHistory = [healthResult, ...existingHistory].slice(0, 100); // Keep last 100
                this.healthHistory.set(serviceId, newHistory);
                
                // Check for alerts
                await this.processAlerts(monitor, healthResult);
                
                console.log(`[MONITORING CHECK] ✓ Service ${serviceId} health: ${healthResult.status}`);
                
            } catch (error) {
                console.error(`[MONITORING CHECK] Error checking ${monitorId}:`, error);
            }
        }
    }

    /**
     * Check Service Health
     */
    private async checkServiceHealth(monitor: SystemMonitor): Promise<HealthCheckResult> {
        const startTime = Date.now();
        
        try {
            // Architecture: Mock health check (in production: actual health check calls)
            const mockMetrics: Record<string, number> = {
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
                serviceId: monitor.target as ServiceId,
                status: status as any,
                metrics: mockMetrics,
                timestamp: new Date(),
                responseTime
            };

        } catch (error) {
            console.error('[MONITORING HEALTH] Service health check failed:', error);
            return {
                serviceId: monitor.target as ServiceId,
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
    private async processAlerts(monitor: SystemMonitor, healthResult: HealthCheckResult): Promise<void> {
        for (const threshold of monitor.thresholds) {
            const metricValue = healthResult.metrics[threshold.metric];
            if (metricValue === undefined) continue;

            const shouldAlert = this.evaluateThreshold(metricValue, threshold);
            if (shouldAlert) {
                await this.createAlert(monitor, threshold, metricValue, healthResult);
            }
        }
    }

    /**
     * Create Alert
     */
    private async createAlert(
        monitor: SystemMonitor, 
        threshold: AlertThreshold, 
        metricValue: number, 
        healthResult: HealthCheckResult
    ): Promise<void> {
        const alertId = this.generateAlertId();
        
        const alert: SystemAlert = {
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
    private evaluateThreshold(value: number, threshold: AlertThreshold): boolean {
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
    async getStatistics(): Promise<{
        totalMonitors: number;
        activeAlerts: number;
        serviceHealthStatus: Record<string, string>;
        alertBreakdown: Record<string, number>;
    }> {
        const activeAlerts = Array.from(this.alerts.values()).filter(alert => !alert.acknowledged);
        
        const serviceHealthStatus: Record<string, string> = {};
        for (const [serviceId, healthHistory] of this.healthHistory.entries()) {
            const latestHealth = healthHistory[0];
            serviceHealthStatus[serviceId] = latestHealth?.status || 'UNKNOWN';
        }

        const alertBreakdown = Array.from(this.alerts.values()).reduce((acc, alert) => {
            acc[alert.severity] = (acc[alert.severity] || 0) + 1;
            return acc;
        }, {} as Record<string, number>);

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
    async healthCheck(): Promise<boolean> {
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
            
        } catch (error) {
            console.error('[MONITORING HEALTH] Monitoring service health check failed:', error);
            return false;
        }
    }

    // Helper methods
    private generateAlertId(): AlertId {
        const id = 'alert_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id as AlertId;
    }
}

/**
 * Register Monitoring Service in DI Container
 */
export function registerMonitoringService(): void {
    console.log('[MONITORING REGISTRATION] Registering Monitoring Service nach infrastructure architecture...');
    
    DIContainer.register('MonitoringService', new MonitoringService(), {
        singleton: true,
        dependencies: []
    });
    
    console.log('[MONITORING REGISTRATION] ✅ Monitoring Service registered successfully nach infrastructure architecture');
}
