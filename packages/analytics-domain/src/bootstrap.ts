import { Logger, MetricsRecorder, ServiceLocator, metricsService } from '@valero-neuroerp/utilities';
import { InMemoryDashboardRepository } from './infrastructure/repositories/in-memory/in-memory-dashboard-repository';
import { InMemoryReportRepository } from './infrastructure/repositories/in-memory/in-memory-report-repository';
import { AnalyticsDomainService } from './services/analytics-domain-service';
import { AnalyticsApiController } from './presentation/controllers/analytics-api-controller';
import type { DashboardRepository } from './core/repositories/dashboard-repository';
import type { ReportRepository } from './core/repositories/report-repository';

const TOKENS = {
  reportRepository: 'analytics.reportRepository',
  dashboardRepository: 'analytics.dashboardRepository',
  domainService: 'analytics.domainService',
  controller: 'analytics.controller',
} as const;

const defaultLogger: Logger = {
  debug(message: string, context?: Record<string, unknown>) {
    // eslint-disable-next-line no-console
    console.debug('[analytics]', message, context);
  },
  info(message: string, context?: Record<string, unknown>) {
    // eslint-disable-next-line no-console
    console.info('[analytics]', message, context);
  },
  warn(message: string, context?: Record<string, unknown>) {
    // eslint-disable-next-line no-console
    console.warn('[analytics]', message, context);
  },
  error(message: string, context?: Record<string, unknown>) {
    // eslint-disable-next-line no-console
    console.error('[analytics]', message, context);
  },
};

export interface AnalyticsBootstrapOptions {
  locator?: ServiceLocator;
  logger?: Logger;
  metrics?: MetricsRecorder;
  reportRepository?: ReportRepository;
  dashboardRepository?: DashboardRepository;
}

export function registerAnalyticsDomain(options: AnalyticsBootstrapOptions = {}): ServiceLocator {
  const locator = options.locator ?? ServiceLocator.getInstance();

  const reportRepository = options.reportRepository ?? new InMemoryReportRepository();
  if (locator.has(TOKENS.reportRepository)) {
    locator.unregister(TOKENS.reportRepository);
  }
  locator.registerInstance<ReportRepository>(TOKENS.reportRepository, reportRepository);

  const dashboardRepository = options.dashboardRepository ?? new InMemoryDashboardRepository();
  if (locator.has(TOKENS.dashboardRepository)) {
    locator.unregister(TOKENS.dashboardRepository);
  }
  locator.registerInstance<DashboardRepository>(TOKENS.dashboardRepository, dashboardRepository);

  if (locator.has(TOKENS.domainService)) {
    locator.unregister(TOKENS.domainService);
  }
  locator.registerFactory(
    TOKENS.domainService,
    () =>
      new AnalyticsDomainService(
        locator.resolve<ReportRepository>(TOKENS.reportRepository),
        locator.resolve<DashboardRepository>(TOKENS.dashboardRepository),
        {
          logger: options.logger ?? defaultLogger,
          metrics: options.metrics ?? metricsService,
        }
      )
  );

  if (locator.has(TOKENS.controller)) {
    locator.unregister(TOKENS.controller);
  }
  locator.registerFactory(
    TOKENS.controller,
    () => new AnalyticsApiController(locator.resolve<AnalyticsDomainService>(TOKENS.domainService))
  );

  return locator;
}

export function resolveAnalyticsDomainService(locator: ServiceLocator = ServiceLocator.getInstance()): AnalyticsDomainService {
  return locator.resolve<AnalyticsDomainService>(TOKENS.domainService);
}

export function resolveAnalyticsController(locator: ServiceLocator = ServiceLocator.getInstance()): AnalyticsApiController {
  return locator.resolve<AnalyticsApiController>(TOKENS.controller);
}
