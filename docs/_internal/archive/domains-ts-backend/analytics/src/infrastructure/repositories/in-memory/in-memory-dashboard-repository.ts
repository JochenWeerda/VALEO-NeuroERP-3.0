import type { DashboardId } from '@packages/data-models';
import { createQueryBuilder, InMemoryRepository } from '@packages/utilities';
import { Dashboard } from '../../../core/entities/dashboard';
import { DashboardRepository } from '../../../core/repositories/dashboard-repository';

export class InMemoryDashboardRepository
  extends InMemoryRepository<Dashboard, 'id', DashboardId>
  implements DashboardRepository {
  constructor() {
    super('id');
  }

  async listPublic(tenantId: string): Promise<Dashboard[]> {
    const query = createQueryBuilder<Dashboard>()
      .where('tenantId', 'eq', tenantId)
      .where('isPublic', 'eq', true as unknown as Dashboard['isPublic'])
      .build();
    return this.findMany(query);
  }

  async listByTag(tenantId: string, tag: string): Promise<Dashboard[]> {
    const dashboards = await this.listForTenant(tenantId);
    return dashboards.filter((dashboard) => dashboard.tags.includes(tag));
  }

  async listForTenant(tenantId: string): Promise<Dashboard[]> {
    const query = createQueryBuilder<Dashboard>().where('tenantId', 'eq', tenantId).build();
    return this.findMany(query);
  }
}
