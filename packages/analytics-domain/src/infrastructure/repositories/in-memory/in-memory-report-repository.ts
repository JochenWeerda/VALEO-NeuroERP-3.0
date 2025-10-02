import type { ReportId } from '@valero-neuroerp/data-models';
import { createQueryBuilder, InMemoryRepository } from '@valero-neuroerp/utilities';
import { Report, ReportStatus } from '../../../core/entities/report';
import { ReportRepository } from '../../../core/repositories/report-repository';

export class InMemoryReportRepository
  extends InMemoryRepository<Report, 'id', ReportId>
  implements ReportRepository {
  constructor() {
    super('id');
  }

  async findByName(tenantId: string, name: string): Promise<Report | null> {
    const query = createQueryBuilder<Report>()
      .where('tenantId', 'eq', tenantId)
      .where('name', 'ilike', name)
      .build();
    return this.findOne(query);
  }

  async listByStatus(tenantId: string, status: ReportStatus): Promise<Report[]> {
    const query = createQueryBuilder<Report>()
      .where('tenantId', 'eq', tenantId)
      .where('status', 'eq', status)
      .build();
    return this.findMany(query);
  }

  async listForTenant(tenantId: string): Promise<Report[]> {
    const query = createQueryBuilder<Report>().where('tenantId', 'eq', tenantId).build();
    return this.findMany(query);
  }
}
