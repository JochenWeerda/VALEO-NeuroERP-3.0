/**
 * VALEO NeuroERP 3.0 - Comprehensive Observability Service
 *
 * Enterprise-grade monitoring, alerting, and observability
 */

import { injectable } from 'inversify';
import { InventoryMetricsService } from './metrics-service';
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
      hot: number; // days
      warm: number; // days
      cold: number; // days
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
  objective: number; // percentage (e.g., 99.9)
  window: string; // e.g., '30d'
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

@injectable()
export class ObservabilityService {
  private readonly metrics = new InventoryMetricsService();
  private config: ObservabilityConfig;
  private alertRules: Map<string, AlertRule> = new Map();
  private sloDefinitions: Map<string, SLODefinition> = new Map();
  private dashboards: Map<string, DashboardDefinition> = new Map();

  constructor(
    private readonly eventBus: EventBus
  ) {
    this.config = this.getDefaultConfig();
    this.initializeObservability();
  }

  /**
   * Initialize comprehensive observability
   */
  private async initializeObservability(): Promise<void> {
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
  private async setupMetricsCollection(): Promise<void> {
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
  private async setupDistributedTracing(): Promise<void> {
    // Configure Jaeger tracing
    // This would integrate with the existing OTel setup
    console.log('Distributed tracing configured');
  }

  /**
   * Setup log aggregation
   */
  private async setupLogAggregation(): Promise<void> {
    // Configure Elasticsearch indexing
    // Setup log shipping from all services
    console.log('Log aggregation configured');
  }

  /**
   * Setup alerting system
   */
  private async setupAlerting(): Promise<void> {
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
  private async setupDashboards(): Promise<void> {
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
  private async setupSLOMonitoring(): Promise<void> {
    const slos = this.getDefaultSLOs();
    for (const slo of slos) {
      await this.createSLO(slo);
    }
  }

  /**
   * Register custom metrics
   */
  private registerCustomMetrics(): void {
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
  async createAlertRule(rule: AlertRule): Promise<void> {
    this.alertRules.set(rule.alertName, rule);

    // In production, this would send to AlertManager
    console.log(`Alert rule created: ${rule.alertName}`);
  }

  /**
   * Create SLO definition
   */
  async createSLO(slo: SLODefinition): Promise<void> {
    this.sloDefinitions.set(slo.name, slo);

    // Create associated alert rules
    await this.createAlertRule(slo.alerting.fastBurn);
    await this.createAlertRule(slo.alerting.slowBurn);

    console.log(`SLO created: ${slo.name}`);
  }

  /**
   * Create dashboard
   */
  async createDashboard(dashboard: DashboardDefinition): Promise<void> {
    this.dashboards.set(dashboard.title, dashboard);

    // In production, this would create/update Grafana dashboard
    console.log(`Dashboard created: ${dashboard.title}`);
  }

  /**
   * Log structured entry
   */
  async logEntry(entry: LogEntry): Promise<void> {
    // In production, this would send to Elasticsearch
    console.log(`[${entry.level.toUpperCase()}] ${entry.service}:${entry.component} - ${entry.message}`, entry.fields);
  }

  /**
   * Record trace span
   */
  async recordSpan(span: TraceSpan): Promise<void> {
    // In production, this would send to Jaeger
    console.log(`Trace span recorded: ${span.operation} (${span.duration}ms)`);
  }

  /**
   * Get system health status
   */
  async getSystemHealth(): Promise<{
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
  }> {
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
  async getPerformanceMetrics(timeRange: { start: Date; end: Date }): Promise<{
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
  }> {
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
  async getBusinessMetrics(timeRange: { start: Date; end: Date }): Promise<{
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
      dso: number; // Days Sales Outstanding
      dio: number; // Days Inventory Outstanding
      dpo: number; // Days Payable Outstanding
      cashConversionCycle: number;
    };
    quality: {
      defectRate: number;
      customerSatisfaction: number;
      auditScore: number;
    };
  }> {
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

  private getDefaultConfig(): ObservabilityConfig {
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

  private getDefaultAlertRules(): AlertRule[] {
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

  private getBusinessAlertRules(): AlertRule[] {
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

  private getDefaultSLOs(): SLODefinition[] {
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

  private createSystemDashboard(): DashboardDefinition {
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

  private createBusinessDashboard(): DashboardDefinition {
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

  private createAlertingDashboard(): DashboardDefinition {
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
}