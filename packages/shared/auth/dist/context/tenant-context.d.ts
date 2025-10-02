import { UserContext } from '../types/auth-types';
export interface TenantContext {
    tenantId: string;
    userId?: string;
    roles: string[];
    permissions: string[];
    metadata?: Record<string, any>;
}
export declare class TenantContextManager {
    private contexts;
    /**
     * Create or update tenant context for user
     */
    setContext(tenantId: string, userId: string, context: Omit<TenantContext, 'tenantId' | 'userId'>): void;
    /**
     * Get tenant context for user
     */
    getContext(tenantId: string, userId: string): TenantContext | undefined;
    /**
     * Remove tenant context for user
     */
    removeContext(tenantId: string, userId: string): void;
    /**
     * Check if user has access to tenant
     */
    hasTenantAccess(tenantId: string, userId: string): boolean;
    /**
     * Get all tenants for a user
     */
    getUserTenants(userId: string): string[];
    /**
     * Get all users for a tenant
     */
    getTenantUsers(tenantId: string): string[];
    /**
     * Validate tenant context from JWT payload
     */
    validateTenantContext(user: UserContext, requestedTenantId?: string): boolean;
    /**
     * Create tenant context from JWT payload
     */
    createContextFromJWT(payload: any): TenantContext;
    /**
     * Clear all contexts (for testing or cleanup)
     */
    clearAllContexts(): void;
    /**
     * Get context statistics
     */
    getStats(): {
        totalContexts: number;
        tenants: number;
        users: number;
    };
}
//# sourceMappingURL=tenant-context.d.ts.map