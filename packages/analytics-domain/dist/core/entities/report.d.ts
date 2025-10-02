import { ReportId } from '@valero-neuroerp/data-models';
export type ReportStatus = 'draft' | 'running' | 'completed' | 'failed';
export interface ReportDefinition {
    metrics: string[];
    filters?: Record<string, unknown>;
    groupBy?: string[];
    timeframe?: {
        start: Date;
        end: Date;
    };
}
export interface Report {
    readonly id: ReportId;
    readonly tenantId: string;
    name: string;
    status: ReportStatus;
    definition: ReportDefinition;
    readonly createdAt: Date;
    updatedAt: Date;
    lastRunAt?: Date;
    lastDurationMs?: number;
}
export interface CreateReportInput {
    tenantId: string;
    name: string;
    definition: ReportDefinition;
}
export interface UpdateReportInput {
    name?: string;
    status?: ReportStatus;
    definition?: Partial<ReportDefinition>;
    lastRunAt?: Date;
    lastDurationMs?: number;
}
export declare function createReport(input: CreateReportInput): Report;
export declare function applyReportUpdate(report: Report, update: UpdateReportInput): Report;
//# sourceMappingURL=report.d.ts.map