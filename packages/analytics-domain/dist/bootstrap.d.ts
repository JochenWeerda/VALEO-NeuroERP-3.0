import { Logger, MetricsRecorder, ServiceLocator } from '@valero-neuroerp/utilities';
import { AnalyticsDomainService } from './services/analytics-domain-service';
import { AnalyticsApiController } from './presentation/controllers/analytics-api-controller';
import type { DashboardRepository } from './core/repositories/dashboard-repository';
import type { ReportRepository } from './core/repositories/report-repository';
export interface AnalyticsBootstrapOptions {
    locator?: ServiceLocator;
    logger?: Logger;
    metrics?: MetricsRecorder;
    reportRepository?: ReportRepository;
    dashboardRepository?: DashboardRepository;
}
export declare function registerAnalyticsDomain(options?: AnalyticsBootstrapOptions): ServiceLocator;
export declare function resolveAnalyticsDomainService(locator?: ServiceLocator): AnalyticsDomainService;
export declare function resolveAnalyticsController(locator?: ServiceLocator): AnalyticsApiController;
//# sourceMappingURL=bootstrap.d.ts.map