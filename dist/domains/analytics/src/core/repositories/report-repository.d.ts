import type { ReportId } from '@packages/data-models';
import { createQueryBuilder, Repository, RepositoryQuery } from '@packages/utilities';
import { Report, ReportStatus } from '../entities/report';
export interface ReportRepository extends Repository<Report, ReportId> {
    findByName(tenantId: string, name: string): Promise<Report | null>;
    listByStatus(tenantId: string, status: ReportStatus): Promise<Report[]>;
    listForTenant(tenantId: string): Promise<Report[]>;
}
export declare const buildTenantQuery: (tenantId: string, extra?: (query: ReturnType<typeof createQueryBuilder<Report>>) => void) => any;
export type ReportQuery = RepositoryQuery<Report>;
//***REMOVED*** sourceMappingURL=report-repository.d.ts.map