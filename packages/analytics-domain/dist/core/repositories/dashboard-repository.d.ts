import type { DashboardId } from '@valero-neuroerp/data-models';
import { Repository } from '@valero-neuroerp/utilities';
import { Dashboard } from '../entities/dashboard';
export interface DashboardRepository extends Repository<Dashboard, DashboardId> {
    listPublic(tenantId: string): Promise<Dashboard[]>;
    listByTag(tenantId: string, tag: string): Promise<Dashboard[]>;
    listForTenant(tenantId: string): Promise<Dashboard[]>;
}
export declare const dashboardTenantQuery: (tenantId: string) => import("@valero-neuroerp/utilities").QueryDescriptor<Dashboard>;
//# sourceMappingURL=dashboard-repository.d.ts.map