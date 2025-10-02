import type { ReportId } from '@packages/data-models';
import { InMemoryRepository } from '@packages/utilities';
import { Report, ReportStatus } from '../../../core/entities/report';
import { ReportRepository } from '../../../core/repositories/report-repository';
export declare class InMemoryReportRepository extends InMemoryRepository<Report, 'id', ReportId> implements ReportRepository {
    constructor();
    findByName(tenantId: string, name: string): Promise<Report | null>;
    listByStatus(tenantId: string, status: ReportStatus): Promise<Report[]>;
    listForTenant(tenantId: string): Promise<Report[]>;
}
//***REMOVED*** sourceMappingURL=in-memory-report-repository.d.ts.map