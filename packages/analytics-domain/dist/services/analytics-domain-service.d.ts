import { Logger, MetricsRecorder } from '@valero-neuroerp/utilities';
import { Report, UpdateReportInput, CreateReportInput } from '../core/entities/report';
import { Dashboard, CreateDashboardInput, UpdateDashboardInput } from '../core/entities/dashboard';
import { ReportRepository } from '../core/repositories/report-repository';
import { DashboardRepository } from '../core/repositories/dashboard-repository';
export interface AnalyticsDomainServiceOptions {
    logger?: Logger;
    metrics?: MetricsRecorder;
}
export declare class AnalyticsDomainService {
    private readonly reports;
    private readonly dashboards;
    private readonly logger;
    private readonly metrics?;
    constructor(reports: ReportRepository, dashboards: DashboardRepository, options?: AnalyticsDomainServiceOptions);
    createReport(input: CreateReportInput): Promise<Report>;
    updateReport(id: Report['id'], update: UpdateReportInput): Promise<Report>;
    listReports(tenantId: string): Promise<Report[]>;
    getReport(id: Report['id']): Promise<Report | null>;
    createDashboard(input: CreateDashboardInput): Promise<Dashboard>;
    updateDashboard(id: Dashboard['id'], update: UpdateDashboardInput): Promise<Dashboard>;
    listDashboards(tenantId: string): Promise<Dashboard[]>;
    listPublicDashboards(tenantId: string): Promise<Dashboard[]>;
}
//# sourceMappingURL=analytics-domain-service.d.ts.map