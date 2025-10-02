import type { ReportId } from '@valero-neuroerp/data-models';
import { InMemoryRepository } from '@valero-neuroerp/utilities';
import { Report, ReportStatus } from '../../../core/entities/report';
import { ReportRepository } from '../../../core/repositories/report-repository';
export declare class InMemoryReportRepository extends InMemoryRepository<Report, 'id', ReportId> implements ReportRepository {
    constructor();
    findByName(tenantId: string, name: string): Promise<Report | null>;
    listByStatus(tenantId: string, status: ReportStatus): Promise<Report[]>;
    listForTenant(tenantId: string): Promise<Report[]>;
}
//# sourceMappingURL=in-memory-report-repository.d.ts.map