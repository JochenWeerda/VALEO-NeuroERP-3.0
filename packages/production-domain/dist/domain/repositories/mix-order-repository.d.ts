/**
 * Mix Order Repository Interface for VALEO NeuroERP 3.0 Production Domain
 * Repository interface for mix order management
 */
import type { MixOrder } from '../entities/mix-order';
export interface MixOrderFilters {
    status?: 'Draft' | 'Staged' | 'Running' | 'Hold' | 'Completed' | 'Aborted';
    type?: 'Plant' | 'Mobile';
    recipeId?: string;
    customerId?: string;
    mobileUnitId?: string;
    dateFrom?: string;
    dateTo?: string;
    search?: string;
}
export interface PaginationOptions {
    page: number;
    pageSize: number;
    filters?: MixOrderFilters;
}
export interface PaginatedResult<T> {
    data: T[];
    pagination: {
        page: number;
        pageSize: number;
        total: number;
        totalPages: number;
    };
}
export interface MixOrderStatistics {
    totalOrders: number;
    activeOrders: number;
    completedOrders: number;
    abortedOrders: number;
    totalMassKg: number;
    averageDurationMinutes: number;
}
export interface MixOrderRepository {
    save(tenantId: string, mixOrder: MixOrder): Promise<MixOrder>;
    findById(tenantId: string, id: string): Promise<MixOrder | null>;
    findByOrderNumber(tenantId: string, orderNumber: string): Promise<MixOrder | null>;
    findAll(tenantId: string, filters?: MixOrderFilters): Promise<MixOrder[]>;
    delete(tenantId: string, id: string): Promise<void>;
    findWithPagination(tenantId: string, options: PaginationOptions): Promise<PaginatedResult<MixOrder>>;
    findByStatus(tenantId: string, status: MixOrder['status']): Promise<MixOrder[]>;
    findByType(tenantId: string, type: MixOrder['type']): Promise<MixOrder[]>;
    findByRecipe(tenantId: string, recipeId: string): Promise<MixOrder[]>;
    findByCustomer(tenantId: string, customerId: string): Promise<MixOrder[]>;
    findByMobileUnit(tenantId: string, mobileUnitId: string): Promise<MixOrder[]>;
    findActiveOrders(tenantId: string): Promise<MixOrder[]>;
    findOrdersInDateRange(tenantId: string, from: string, to: string): Promise<MixOrder[]>;
    findActiveMobileOrders(tenantId: string): Promise<MixOrder[]>;
    findMobileOrdersByLocation(tenantId: string, lat: number, lng: number, radiusKm: number): Promise<MixOrder[]>;
    bulkSave(tenantId: string, mixOrders: MixOrder[]): Promise<MixOrder[]>;
    bulkDelete(tenantId: string, ids: string[]): Promise<void>;
    getStatistics(tenantId: string, filters?: MixOrderFilters): Promise<MixOrderStatistics>;
    getOrderCount(tenantId: string, filters?: MixOrderFilters): Promise<number>;
    getTotalMassProcessed(tenantId: string, filters?: MixOrderFilters): Promise<number>;
    getAverageDuration(tenantId: string, filters?: MixOrderFilters): Promise<number>;
}
//# sourceMappingURL=mix-order-repository.d.ts.map