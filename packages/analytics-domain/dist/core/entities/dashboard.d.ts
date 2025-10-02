import { DashboardId } from '@valero-neuroerp/data-models';
export interface DashboardWidget {
    id: string;
    type: 'chart' | 'table' | 'metric' | 'text';
    title: string;
    position: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
    definition: Record<string, unknown>;
    refreshIntervalMs?: number;
}
export interface Dashboard {
    readonly id: DashboardId;
    readonly tenantId: string;
    name: string;
    description?: string;
    isPublic: boolean;
    widgets: DashboardWidget[];
    tags: string[];
    readonly createdAt: Date;
    updatedAt: Date;
}
export interface CreateDashboardInput {
    tenantId: string;
    name: string;
    widgets?: DashboardWidget[];
    description?: string;
    isPublic?: boolean;
    tags?: string[];
}
export interface UpdateDashboardInput {
    name?: string;
    description?: string;
    isPublic?: boolean;
    widgets?: DashboardWidget[];
    tags?: string[];
}
export declare function createDashboard(input: CreateDashboardInput): Dashboard;
export declare function applyDashboardUpdate(dashboard: Dashboard, update: UpdateDashboardInput): Dashboard;
//# sourceMappingURL=dashboard.d.ts.map