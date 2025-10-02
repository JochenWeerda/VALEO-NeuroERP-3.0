import type { ReportId } from '@packages/data-models';
import { createQueryBuilder, Repository, RepositoryQuery } from '@packages/utilities';
import { Report, ReportStatus } from '../entities/report';

export interface ReportRepository extends Repository<Report, ReportId> {
  findByName(tenantId: string, name: string): Promise<Report | null>;
  listByStatus(tenantId: string, status: ReportStatus): Promise<Report[]>;
  listForTenant(tenantId: string): Promise<Report[]>;
}

export const buildTenantQuery = (tenantId: string, extra?: (query: ReturnType<typeof createQueryBuilder<Report>>) => void) => {
  const builder = createQueryBuilder<Report>().where('tenantId', 'eq', tenantId as unknown as Report['tenantId']);
  if (extra) {
    extra(builder);
  }
  return builder.build();
};

export type ReportQuery = RepositoryQuery<Report>;
