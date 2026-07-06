import type { DashboardId } from '@packages/data-models';
import { createQueryBuilder, Repository } from '@packages/utilities';
import { Dashboard } from '../entities/dashboard';

export interface DashboardRepository extends Repository<Dashboard, DashboardId> {
  listPublic(tenantId: string): Promise<Dashboard[]>;
  listByTag(tenantId: string, tag: string): Promise<Dashboard[]>;
  listForTenant(tenantId: string): Promise<Dashboard[]>;
}

export const dashboardTenantQuery = (tenantId: string) =>
  createQueryBuilder<Dashboard>().where('tenantId', 'eq', tenantId).build();
