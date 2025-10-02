"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TenantContextManager = void 0;
class TenantContextManager {
    constructor() {
        this.contexts = new Map();
    }
    /**
     * Create or update tenant context for user
     */
    setContext(tenantId, userId, context) {
        const fullContext = {
            tenantId,
            userId,
            ...context
        };
        const key = `${tenantId}:${userId}`;
        this.contexts.set(key, fullContext);
    }
    /**
     * Get tenant context for user
     */
    getContext(tenantId, userId) {
        const key = `${tenantId}:${userId}`;
        return this.contexts.get(key);
    }
    /**
     * Remove tenant context for user
     */
    removeContext(tenantId, userId) {
        const key = `${tenantId}:${userId}`;
        this.contexts.delete(key);
    }
    /**
     * Check if user has access to tenant
     */
    hasTenantAccess(tenantId, userId) {
        const context = this.getContext(tenantId, userId);
        return context !== undefined;
    }
    /**
     * Get all tenants for a user
     */
    getUserTenants(userId) {
        const tenants = [];
        for (const [key, context] of this.contexts.entries()) {
            if (context.userId === userId) {
                tenants.push(context.tenantId);
            }
        }
        return [...new Set(tenants)]; // Remove duplicates
    }
    /**
     * Get all users for a tenant
     */
    getTenantUsers(tenantId) {
        const users = [];
        for (const [key, context] of this.contexts.entries()) {
            if (context.tenantId === tenantId && context.userId) {
                users.push(context.userId);
            }
        }
        return [...new Set(users)]; // Remove duplicates
    }
    /**
     * Validate tenant context from JWT payload
     */
    validateTenantContext(user, requestedTenantId) {
        // If no specific tenant requested, use user's default tenant
        const tenantId = requestedTenantId || user.tenantId;
        // Check if user has access to the requested tenant
        return this.hasTenantAccess(tenantId, user.userId);
    }
    /**
     * Create tenant context from JWT payload
     */
    createContextFromJWT(payload) {
        return {
            tenantId: payload.tenantId,
            userId: payload.sub,
            roles: payload.roles || [],
            permissions: payload.permissions || [],
            metadata: {
                email: payload.email,
                tokenExpiry: payload.exp,
                tokenIssuedAt: payload.iat
            }
        };
    }
    /**
     * Clear all contexts (for testing or cleanup)
     */
    clearAllContexts() {
        this.contexts.clear();
    }
    /**
     * Get context statistics
     */
    getStats() {
        const tenants = new Set();
        const users = new Set();
        for (const context of this.contexts.values()) {
            tenants.add(context.tenantId);
            if (context.userId) {
                users.add(context.userId);
            }
        }
        return {
            totalContexts: this.contexts.size,
            tenants: tenants.size,
            users: users.size
        };
    }
}
exports.TenantContextManager = TenantContextManager;
//# sourceMappingURL=tenant-context.js.map