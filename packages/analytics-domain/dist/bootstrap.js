"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerAnalyticsDomain = registerAnalyticsDomain;
exports.resolveAnalyticsDomainService = resolveAnalyticsDomainService;
exports.resolveAnalyticsController = resolveAnalyticsController;
const utilities_1 = require("@valero-neuroerp/utilities");
const in_memory_dashboard_repository_1 = require("./infrastructure/repositories/in-memory/in-memory-dashboard-repository");
const in_memory_report_repository_1 = require("./infrastructure/repositories/in-memory/in-memory-report-repository");
const analytics_domain_service_1 = require("./services/analytics-domain-service");
const analytics_api_controller_1 = require("./presentation/controllers/analytics-api-controller");
const TOKENS = {
    reportRepository: 'analytics.reportRepository',
    dashboardRepository: 'analytics.dashboardRepository',
    domainService: 'analytics.domainService',
    controller: 'analytics.controller',
};
const defaultLogger = {
    debug(message, context) {
        console.debug('[analytics]', message, context);
    },
    info(message, context) {
        console.info('[analytics]', message, context);
    },
    warn(message, context) {
        console.warn('[analytics]', message, context);
    },
    error(message, context) {
        console.error('[analytics]', message, context);
    },
};
function registerAnalyticsDomain(options = {}) {
    const locator = options.locator ?? utilities_1.ServiceLocator.getInstance();
    const reportRepository = options.reportRepository ?? new in_memory_report_repository_1.InMemoryReportRepository();
    if (locator.has(TOKENS.reportRepository)) {
        locator.unregister(TOKENS.reportRepository);
    }
    locator.registerInstance(TOKENS.reportRepository, reportRepository);
    const dashboardRepository = options.dashboardRepository ?? new in_memory_dashboard_repository_1.InMemoryDashboardRepository();
    if (locator.has(TOKENS.dashboardRepository)) {
        locator.unregister(TOKENS.dashboardRepository);
    }
    locator.registerInstance(TOKENS.dashboardRepository, dashboardRepository);
    if (locator.has(TOKENS.domainService)) {
        locator.unregister(TOKENS.domainService);
    }
    locator.registerFactory(TOKENS.domainService, () => new analytics_domain_service_1.AnalyticsDomainService(locator.resolve(TOKENS.reportRepository), locator.resolve(TOKENS.dashboardRepository), {
        logger: options.logger ?? defaultLogger,
        metrics: options.metrics ?? utilities_1.metricsService,
    }));
    if (locator.has(TOKENS.controller)) {
        locator.unregister(TOKENS.controller);
    }
    locator.registerFactory(TOKENS.controller, () => new analytics_api_controller_1.AnalyticsApiController(locator.resolve(TOKENS.domainService)));
    return locator;
}
function resolveAnalyticsDomainService(locator = utilities_1.ServiceLocator.getInstance()) {
    return locator.resolve(TOKENS.domainService);
}
function resolveAnalyticsController(locator = utilities_1.ServiceLocator.getInstance()) {
    return locator.resolve(TOKENS.controller);
}
//# sourceMappingURL=bootstrap.js.map