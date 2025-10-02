/**
 * Monitoring Service - MSOA Implementation nach Clean Architecture
 * Infrastructure Layer Service migrated to VALEO-NeuroERP-3.0
 * External monitoring and health check orchestration
 */
import { Brand } from '@valero-neuroerp/data-models/src/branded-types';
export type MonitorId = Brand<string, 'MonitorId'>;
export type ServiceId = Brand<string, 'ServiceId'>;
export type AlertId = Brand<string, 'AlertId'>;
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
export declare class MonitoringService {
    private readonly monitors;
    private readonly alerts;
    private readonly healthHistory;
    private readonly startedMonitoring;
    constructor();
    /**
     * Initialize Monitoring Service
     */
    private initializeMonitoringService;
    /**
     * Setup Default Monitors nach System Requirements
     */
    private setupDefaultMonitors;
    /**
     * Create Health Monitor
     */
    private createHealthMonitor;
    /**
     * Create Performance Monitor
     */
    private createPerformanceMonitor;
    /**
     * Create Resource Monitor
     */
    private createResourceMonitor;
    /**
     * Start Monitoring Process
     */
    private startMonitoringProcess;
    /**
     * Run Health Checks
     */
    private runHealthChecks;
    /**
     * Check Service Health
     */
    private checkServiceHealth;
    /**
     * Process Alerts
     */
    private processAlerts;
    /**
     * Create Alert
     */
    private createAlert;
    /**
     * Evaluate Threshold
     */
    private evaluateThreshold;
    /**
     * Get Monitoring Statistics
     */
    getStatistics(): Promise<{
        totalMonitors: number;
        activeAlerts: number;
        serviceHealthStatus: Record<string, string>;
        alertBreakdown: Record<string, number>;
    }>;
    /**
     * Health check
     */
    healthCheck(): Promise<boolean>;
    private generateAlertId;
}
/**
 * Register Monitoring Service in DI Container
 */
export declare function registerMonitoringService(): void;
//# sourceMappingURL=monitoring-service.d.ts.map