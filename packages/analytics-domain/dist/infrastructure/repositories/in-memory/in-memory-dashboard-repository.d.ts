import type { DashboardId } from '@valero-neuroerp/data-models';
import { InMemoryRepository } from '@valero-neuroerp/utilities';
import { Dashboard } from '../../../core/entities/dashboard';
import { DashboardRepository } from '../../../core/repositories/dashboard-repository';
export declare class InMemoryDashboardRepository extends InMemoryRepository<Dashboard, 'id', DashboardId> implements DashboardRepository {
    constructor();
    listPublic(tenantId: string): Promise<Dashboard[]>;
    listByTag(tenantId: string, tag: string): Promise<Dashboard[]>;
    listForTenant(tenantId: string): Promise<Dashboard[]>;
}
//# sourceMappingURL=in-memory-dashboard-repository.d.ts.map