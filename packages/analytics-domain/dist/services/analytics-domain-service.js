"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AnalyticsDomainService = void 0;
const report_1 = require("../core/entities/report");
const dashboard_1 = require("../core/entities/dashboard");
const noopLogger = {
    debug() { },
    info() { },
    warn() { },
    error() { },
};
class AnalyticsDomainService {
    reports;
    dashboards;
    logger;
    metrics;
    constructor(reports, dashboards, options = {}) {
        this.reports = reports;
        this.dashboards = dashboards;
        this.logger = options.logger ?? noopLogger;
        this.metrics = options.metrics;
    }
    async createReport(input) {
        this.logger.info('analytics.report.create.start', { tenantId: input.tenantId, name: input.name });
        const report = (0, report_1.createReport)(input);
        const saved = await this.reports.create(report);
        this.metrics?.incrementCounter('analytics.report.created', { tenantId: input.tenantId });
        return saved;
    }
    async updateReport(id, update) {
        const existing = await this.reports.findById(id);
        if (!existing) {
            throw new Error(`Report ${String(id)} not found`);
        }
        const next = (0, report_1.applyReportUpdate)(existing, update);
        const saved = await this.reports.update(id, next);
        this.metrics?.incrementCounter('analytics.report.updated', { tenantId: next.tenantId });
        return saved;
    }
    async listReports(tenantId) {
        return this.reports.listForTenant(tenantId);
    }
    async getReport(id) {
        return this.reports.findById(id);
    }
    async createDashboard(input) {
        this.logger.info('analytics.dashboard.create.start', { tenantId: input.tenantId, name: input.name });
        const dashboard = (0, dashboard_1.createDashboard)(input);
        const saved = await this.dashboards.create(dashboard);
        this.metrics?.incrementCounter('analytics.dashboard.created', { tenantId: input.tenantId });
        return saved;
    }
    async updateDashboard(id, update) {
        const existing = await this.dashboards.findById(id);
        if (!existing) {
            throw new Error(`Dashboard ${String(id)} not found`);
        }
        const next = (0, dashboard_1.applyDashboardUpdate)(existing, update);
        const saved = await this.dashboards.update(id, next);
        this.metrics?.incrementCounter('analytics.dashboard.updated', { tenantId: saved.tenantId });
        return saved;
    }
    async listDashboards(tenantId) {
        return this.dashboards.listForTenant(tenantId);
    }
    async listPublicDashboards(tenantId) {
        return this.dashboards.listPublic(tenantId);
    }
}
exports.AnalyticsDomainService = AnalyticsDomainService;
//# sourceMappingURL=analytics-domain-service.js.map