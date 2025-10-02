import { UserContext } from '../types/auth-types';

export interface TenantContext {
  tenantId: string;
  userId?: string;
  roles: string[];
  permissions: string[];
  metadata?: Record<string, any>;
}

export class TenantContextManager {
  private contexts: Map<string, TenantContext> = new Map();

  /**
   * Create or update tenant context for user
   */
  setContext(tenantId: string, userId: string, context: Omit<TenantContext, 'tenantId' | 'userId'>): void {
    const fullContext: TenantContext = {
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
  getContext(tenantId: string, userId: string): TenantContext | undefined {
    const key = `${tenantId}:${userId}`;
    return this.contexts.get(key);
  }

  /**
   * Remove tenant context for user
   */
  removeContext(tenantId: string, userId: string): void {
    const key = `${tenantId}:${userId}`;
    this.contexts.delete(key);
  }

  /**
   * Check if user has access to tenant
   */
  hasTenantAccess(tenantId: string, userId: string): boolean {
    const context = this.getContext(tenantId, userId);
    return context !== undefined;
  }

  /**
   * Get all tenants for a user
   */
  getUserTenants(userId: string): string[] {
    const tenants: string[] = [];

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
  getTenantUsers(tenantId: string): string[] {
    const users: string[] = [];

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
  validateTenantContext(user: UserContext, requestedTenantId?: string): boolean {
    // If no specific tenant requested, use user's default tenant
    const tenantId = requestedTenantId || user.tenantId;

    // Check if user has access to the requested tenant
    return this.hasTenantAccess(tenantId, user.userId);
  }

  /**
   * Create tenant context from JWT payload
   */
  createContextFromJWT(payload: any): TenantContext {
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
  clearAllContexts(): void {
    this.contexts.clear();
  }

  /**
   * Get context statistics
   */
  getStats(): { totalContexts: number; tenants: number; users: number } {
    const tenants = new Set<string>();
    const users = new Set<string>();

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