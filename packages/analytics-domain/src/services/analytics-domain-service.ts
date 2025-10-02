import { Logger, MetricsRecorder } from '@valero-neuroerp/utilities';
import { Report, createReport, applyReportUpdate, UpdateReportInput, CreateReportInput } from '../core/entities/report';
import { Dashboard, createDashboard, applyDashboardUpdate, CreateDashboardInput, UpdateDashboardInput } from '../core/entities/dashboard';
import { ReportRepository } from '../core/repositories/report-repository';
import { DashboardRepository } from '../core/repositories/dashboard-repository';

export interface AnalyticsDomainServiceOptions {
  logger?: Logger;
  metrics?: MetricsRecorder;
}

const noopLogger: Logger = {
  debug() {},
  info() {},
  warn() {},
  error() {},
};

export class AnalyticsDomainService {
  private readonly logger: Logger;
  private readonly metrics?: MetricsRecorder;

  constructor(
    private readonly reports: ReportRepository,
    private readonly dashboards: DashboardRepository,
    options: AnalyticsDomainServiceOptions = {}
  ) {
    this.logger = options.logger ?? noopLogger;
    this.metrics = options.metrics;
  }

  async createReport(input: CreateReportInput): Promise<Report> {
    this.logger.info('analytics.report.create.start', { tenantId: input.tenantId, name: input.name });
    const report = createReport(input);
    const saved = await this.reports.create(report);
    this.metrics?.incrementCounter('analytics.report.created', { tenantId: input.tenantId });
    return saved;
  }

  async updateReport(id: Report['id'], update: UpdateReportInput): Promise<Report> {
    const existing = await this.reports.findById(id);
    if (!existing) {
      throw new Error(`Report ${String(id)} not found`);
    }
    const next = applyReportUpdate(existing, update);
    const saved = await this.reports.update(id, next);
    this.metrics?.incrementCounter('analytics.report.updated', { tenantId: next.tenantId });
    return saved;
  }

  async listReports(tenantId: string): Promise<Report[]> {
    return this.reports.listForTenant(tenantId);
  }

  async getReport(id: Report['id']): Promise<Report | null> {
    return this.reports.findById(id);
  }

  async createDashboard(input: CreateDashboardInput): Promise<Dashboard> {
    this.logger.info('analytics.dashboard.create.start', { tenantId: input.tenantId, name: input.name });
    const dashboard = createDashboard(input);
    const saved = await this.dashboards.create(dashboard);
    this.metrics?.incrementCounter('analytics.dashboard.created', { tenantId: input.tenantId });
    return saved;
  }

  async updateDashboard(id: Dashboard['id'], update: UpdateDashboardInput): Promise<Dashboard> {
    const existing = await this.dashboards.findById(id);
    if (!existing) {
      throw new Error(`Dashboard ${String(id)} not found`);
    }
    const next = applyDashboardUpdate(existing, update);
    const saved = await this.dashboards.update(id, next);
    this.metrics?.incrementCounter('analytics.dashboard.updated', { tenantId: saved.tenantId });
    return saved;
  }

  async listDashboards(tenantId: string): Promise<Dashboard[]> {
    return this.dashboards.listForTenant(tenantId);
  }

  async listPublicDashboards(tenantId: string): Promise<Dashboard[]> {
    return this.dashboards.listPublic(tenantId);
  }
}
