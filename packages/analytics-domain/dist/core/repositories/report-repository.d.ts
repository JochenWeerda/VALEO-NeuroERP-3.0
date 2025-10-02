import type { ReportId } from '@valero-neuroerp/data-models';
import { createQueryBuilder, Repository, RepositoryQuery } from '@valero-neuroerp/utilities';
import { Report, ReportStatus } from '../entities/report';
export interface ReportRepository extends Repository<Report, ReportId> {
    findByName(tenantId: string, name: string): Promise<Report | null>;
    listByStatus(tenantId: string, status: ReportStatus): Promise<Report[]>;
    listForTenant(tenantId: string): Promise<Report[]>;
}
export declare const buildTenantQuery: (tenantId: string, extra?: (query: ReturnType<typeof createQueryBuilder<Report>>) => void) => import("@valero-neuroerp/utilities").QueryDescriptor<Report>;
export type ReportQuery = RepositoryQuery<Report>;
//# sourceMappingURL=report-repository.d.ts.map