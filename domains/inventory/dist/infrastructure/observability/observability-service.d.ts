/**
 * VALEO NeuroERP 3.0 - Comprehensive Observability Service
 *
 * Enterprise-grade monitoring, alerting, and observability
 */
import { EventBus } from '../event-bus/event-bus';
export interface ObservabilityConfig {
    prometheus: {
        endpoint: string;
        scrapeInterval: number;
        externalLabels: Record<string, string>;
    };
    jaeger: {
        endpoint: string;
        serviceName: string;
        tags: Record<string, string>;
    };
    elasticsearch: {
        nodes: string[];
        indexPrefix: string;
        retention: {
            hot: number;
            warm: number;
            cold: number;
        };
    };
    grafana: {
        endpoint: string;
        apiKey: string;
        dashboards: {
            system: string;
            business: string;
            alerts: string;
        };
    };
    alertmanager: {
        endpoint: string;
        defaultReceiver: string;
        routes: AlertRoute[];
    };
}
export interface AlertRule {
    alertName: string;
    condition: string;
    duration: string;
    labels: Record<string, string>;
    annotations: Record<string, string>;
    severity: 'critical' | 'warning' | 'info';
    team: string;
    service: string;
}
export interface AlertRoute {
    matchers: Record<string, string>;
    receiver: string;
    continue?: boolean;
    routes?: AlertRoute[];
}
export interface SLODefinition {
    name: string;
    objective: number;
    window: string;
    indicators: {
        name: string;
        query: string;
        goodQuery: string;
        totalQuery: string;
    }[];
    alerting: {
        fastBurn: AlertRule;
        slowBurn: AlertRule;
    };
}
export interface DashboardDefinition {
    title: string;
    description: string;
    tags: string[];
    panels: DashboardPanel[];
    variables: DashboardVariable[];
    timeRange: {
        from: string;
        to: string;
    };
}
export interface DashboardPanel {
    id: number;
    title: string;
    type: 'graph' | 'singlestat' | 'table' | 'heatmap' | 'bargauge';
    targets: {
        expr: string;
        legendFormat: string;
        refId: string;
    }[];
    gridPos: {
        h: number;
        w: number;
        x: number;
        y: number;
    };
    options?: Record<string, any>;
}
export interface DashboardVariable {
    name: string;
    label: string;
    type: 'query' | 'custom' | 'constant';
    query?: string;
    values?: string[];
    defaultValue?: string;
}
export interface LogEntry {
    timestamp: Date;
    level: 'debug' | 'info' | 'warn' | 'error' | 'fatal';
    service: string;
    component: string;
    message: string;
    fields: Record<string, any>;
    traceId?: string;
    spanId?: string;
    userId?: string;
    sessionId?: string;
    correlationId?: string;
}
export interface TraceSpan {
    traceId: string;
    spanId: string;
    parentSpanId?: string;
    operation: string;
    service: string;
    startTime: Date;
    duration: number;
    tags: Record<string, string>;
    logs: {
        timestamp: Date;
        fields: Record<string, any>;
    }[];
    references: {
        refType: 'child_of' | 'follows_from';
        traceId: string;
        spanId: string;
    }[];
}
export declare class ObservabilityService {
    private readonly eventBus;
    private readonly metrics;
    private config;
    private alertRules;
    private sloDefinitions;
    private dashboards;
    constructor(eventBus: EventBus);
    /**
     * Initialize comprehensive observability
     */
    private initializeObservability;
    /**
     * Setup advanced metrics collection
     */
    private setupMetricsCollection;
    /**
     * Setup distributed tracing
     */
    private setupDistributedTracing;
    /**
     * Setup log aggregation
     */
    private setupLogAggregation;
    /**
     * Setup alerting system
     */
    private setupAlerting;
    /**
     * Setup dashboards
     */
    private setupDashboards;
    /**
     * Setup SLO monitoring
     */
    private setupSLOMonitoring;
    /**
     * Register custom metrics
     */
    private registerCustomMetrics;
    /**
     * Create alert rule
     */
    createAlertRule(rule: AlertRule): Promise<void>;
    /**
     * Create SLO definition
     */
    createSLO(slo: SLODefinition): Promise<void>;
    /**
     * Create dashboard
     */
    createDashboard(dashboard: DashboardDefinition): Promise<void>;
    /**
     * Log structured entry
     */
    logEntry(entry: LogEntry): Promise<void>;
    /**
     * Record trace span
     */
    recordSpan(span: TraceSpan): Promise<void>;
    /**
     * Get system health status
     */
    getSystemHealth(): Promise<{
        overall: 'healthy' | 'degraded' | 'unhealthy';
        services: Record<string, {
            status: 'up' | 'down' | 'degraded';
            responseTime?: number;
            errorRate?: number;
            lastCheck: Date;
        }>;
        alerts: {
            active: number;
            critical: number;
            warning: number;
        };
        slos: Record<string, {
            objective: number;
            current: number;
            status: 'healthy' | 'breach' | 'warning';
        }>;
    }>;
    /**
     * Get performance metrics
     */
    getPerformanceMetrics(timeRange: {
        start: Date;
        end: Date;
    }): Promise<{
        throughput: {
            requestsPerSecond: number;
            transactionsPerHour: number;
            ordersPerDay: number;
        };
        latency: {
            p50: number;
            p95: number;
            p99: number;
        };
        errorRates: {
            overall: number;
            byService: Record<string, number>;
        };
        resourceUsage: {
            cpu: number;
            memory: number;
            disk: number;
            network: number;
        };
    }>;
    /**
     * Get business metrics
     */
    getBusinessMetrics(timeRange: {
        start: Date;
        end: Date;
    }): Promise<{
        inventory: {
            accuracy: number;
            turnover: number;
            stockoutRate: number;
            overstockValue: number;
        };
        orders: {
            fillRate: number;
            onTimeDelivery: number;
            returnRate: number;
            averageOrderValue: number;
        };
        finance: {
            dso: number;
            dio: number;
            dpo: number;
            cashConversionCycle: number;
        };
        quality: {
            defectRate: number;
            customerSatisfaction: number;
            auditScore: number;
        };
    }>;
    private getDefaultConfig;
    private getDefaultAlertRules;
    private getBusinessAlertRules;
    private getDefaultSLOs;
    private createSystemDashboard;
    private createBusinessDashboard;
    private createAlertingDashboard;
}
//# sourceMappingURL=observability-service.d.ts.map