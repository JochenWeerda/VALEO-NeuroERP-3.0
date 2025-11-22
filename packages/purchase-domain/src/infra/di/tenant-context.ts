/**
 * Tenant Context Provider
 * Multi-tenant isolation and context management
 * Ensures complete tenant data segregation
 */

import { randomUUID } from 'crypto';

export interface TenantContext {
  tenantId: string;
  tenantName: string;
  organizationId: string;
  subscriptionLevel: 'BASIC' | 'PROFESSIONAL' | 'ENTERPRISE';
  features: string[];
  limits: TenantLimits;
  securityPolicy: TenantSecurityPolicy;
  createdAt: Date;
  lastActiveAt: Date;
  status: 'ACTIVE' | 'SUSPENDED' | 'DEACTIVATED';
  metadata: Record<string, any>;
}

export interface TenantLimits {
  maxUsers: number;
  maxPurchaseOrders: number;
  maxStorageGB: number;
  maxAPICallsPerDay: number;
  allowedDomains: string[];
  dataRetentionDays: number;
}

export interface TenantSecurityPolicy {
  requireMFA: boolean;
  passwordPolicy: {
    minLength: number;
    requireNumbers: boolean;
    requireSpecialChars: boolean;
    requireUppercase: boolean;
    expirationDays: number;
  };
  sessionTimeoutMinutes: number;
  ipWhitelist: string[];
  allowedFileTypes: string[];
  encryptionLevel: 'STANDARD' | 'HIGH' | 'MAXIMUM';
  auditLevel: 'BASIC' | 'DETAILED' | 'COMPREHENSIVE';
}

export interface TenantRequest {
  tenantId: string;
  userId: string;
  requestId: string;
  timestamp: Date;
  ipAddress: string;
  userAgent: string;
  resource: string;
  action: string;
}

export class TenantContextProvider {
  private readonly tenants: Map<string, TenantContext> = new Map();
  private readonly activeContexts: Map<string, TenantContext> = new Map(); // requestId -> TenantContext

  constructor() {
    this.initializeDefaultTenants();
  }

  /**
   * Creates a new tenant context
   */
  public async createTenant(
    tenantId: string,
    tenantName: string,
    organizationId: string,
    subscriptionLevel: 'BASIC' | 'PROFESSIONAL' | 'ENTERPRISE' = 'BASIC'
  ): Promise<TenantContext> {
    if (this.tenants.has(tenantId)) {
      throw new Error(`Tenant '${tenantId}' already exists`);
    }

    const context: TenantContext = {
      tenantId,
      tenantName,
      organizationId,
      subscriptionLevel,
      features: this.getFeaturesForSubscription(subscriptionLevel),
      limits: this.getLimitsForSubscription(subscriptionLevel),
      securityPolicy: this.getSecurityPolicyForSubscription(subscriptionLevel),
      createdAt: new Date(),
      lastActiveAt: new Date(),
      status: 'ACTIVE',
      metadata: {}
    };

    this.tenants.set(tenantId, context);
    return context;
  }

  /**
   * Gets tenant context by ID
   */
  public getTenant(tenantId: string): TenantContext | undefined {
    return this.tenants.get(tenantId);
  }

  /**
   * Validates and retrieves tenant context
   */
  public async validateAndGetTenant(tenantId: string): Promise<TenantContext> {
    const context = this.getTenant(tenantId);
    if (!context) {
      throw new Error(`Tenant '${tenantId}' not found`);
    }

    if (context.status !== 'ACTIVE') {
      throw new Error(`Tenant '${tenantId}' is ${context.status.toLowerCase()}`);
    }

    // Update last active timestamp
    context.lastActiveAt = new Date();
    this.tenants.set(tenantId, context);

    return context;
  }

  /**
   * Creates a tenant-aware request context
   */
  public async createRequestContext(
    tenantId: string,
    userId: string,
    ipAddress: string,
    userAgent: string,
    resource: string,
    action: string
  ): Promise<string> {
    const tenantContext = await this.validateAndGetTenant(tenantId);
    const requestId = randomUUID();

    // Validate IP whitelist if configured
    if (tenantContext.securityPolicy.ipWhitelist.length > 0) {
      if (!tenantContext.securityPolicy.ipWhitelist.includes(ipAddress)) {
        throw new Error(`IP address '${ipAddress}' not allowed for tenant '${tenantId}'`);
      }
    }

    // Create request context
    const request: TenantRequest = {
      tenantId,
      userId,
      requestId,
      timestamp: new Date(),
      ipAddress,
      userAgent,
      resource,
      action
    };

    // Store active context
    this.activeContexts.set(requestId, tenantContext);

    // Log tenant activity
    console.log(`[TENANT] ${tenantId}: ${action} on ${resource} by ${userId}`);

    return requestId;
  }

  /**
   * Gets tenant context for a request
   */
  public getRequestTenantContext(requestId: string): TenantContext | undefined {
    return this.activeContexts.get(requestId);
  }

  /**
   * Clears request context (should be called when request completes)
   */
  public clearRequestContext(requestId: string): void {
    this.activeContexts.delete(requestId);
  }

  /**
   * Checks if tenant has access to a specific feature
   */
  public hasFeature(tenantId: string, feature: string): boolean {
    const context = this.getTenant(tenantId);
    return context?.features.includes(feature) ?? false;
  }

  /**
   * Checks if tenant is within limits for a specific resource
   */
  public checkLimits(tenantId: string, resource: 'users' | 'purchaseOrders' | 'storage' | 'apiCalls', current: number): boolean {
    const context = this.getTenant(tenantId);
    if (!context) return false;

    switch (resource) {
      case 'users':
        return current < context.limits.maxUsers;
      case 'purchaseOrders':
        return current < context.limits.maxPurchaseOrders;
      case 'storage':
        return current < context.limits.maxStorageGB;
      case 'apiCalls':
        return current < context.limits.maxAPICallsPerDay;
      default:
        return false;
    }
  }

  /**
   * Lists all active tenants
   */
  public getActiveTenants(): TenantContext[] {
    return Array.from(this.tenants.values()).filter(t => t.status === 'ACTIVE');
  }

  /**
   * Updates tenant subscription level
   */
  public async updateSubscription(tenantId: string, newLevel: 'BASIC' | 'PROFESSIONAL' | 'ENTERPRISE'): Promise<TenantContext> {
    const context = await this.validateAndGetTenant(tenantId);
    
    context.subscriptionLevel = newLevel;
    context.features = this.getFeaturesForSubscription(newLevel);
    context.limits = this.getLimitsForSubscription(newLevel);
    context.securityPolicy = this.getSecurityPolicyForSubscription(newLevel);
    
    this.tenants.set(tenantId, context);
    return context;
  }

  /**
   * Suspends a tenant
   */
  public async suspendTenant(tenantId: string, reason: string): Promise<void> {
    const context = this.getTenant(tenantId);
    if (context) {
      context.status = 'SUSPENDED';
      context.metadata.suspensionReason = reason;
      context.metadata.suspendedAt = new Date();
      this.tenants.set(tenantId, context);
    }
  }

  /**
   * Reactivates a suspended tenant
   */
  public async reactivateTenant(tenantId: string): Promise<void> {
    const context = this.getTenant(tenantId);
    if (context) {
      context.status = 'ACTIVE';
      delete context.metadata.suspensionReason;
      delete context.metadata.suspendedAt;
      context.metadata.reactivatedAt = new Date();
      this.tenants.set(tenantId, context);
    }
  }

  // Private helper methods

  private initializeDefaultTenants(): void {
    // Create default development tenant
    const defaultTenant: TenantContext = {
      tenantId: 'default-tenant',
      tenantName: 'Default Development Tenant',
      organizationId: 'VALEO-DEV',
      subscriptionLevel: 'ENTERPRISE',
      features: ['purchase_orders', 'sales_orders', 'delivery_tracking', 'advanced_analytics', 'multi_user', 'api_access'],
      limits: {
        maxUsers: 1000,
        maxPurchaseOrders: 100000,
        maxStorageGB: 1000,
        maxAPICallsPerDay: 100000,
        allowedDomains: ['*'],
        dataRetentionDays: 2555 // 7 years
      },
      securityPolicy: {
        requireMFA: false,
        passwordPolicy: {
          minLength: 8,
          requireNumbers: true,
          requireSpecialChars: true,
          requireUppercase: true,
          expirationDays: 90
        },
        sessionTimeoutMinutes: 480,
        ipWhitelist: [],
        allowedFileTypes: ['pdf', 'xlsx', 'docx', 'png', 'jpg'],
        encryptionLevel: 'HIGH',
        auditLevel: 'COMPREHENSIVE'
      },
      createdAt: new Date(),
      lastActiveAt: new Date(),
      status: 'ACTIVE',
      metadata: { environment: 'development' }
    };

    this.tenants.set('default-tenant', defaultTenant);
  }

  private getFeaturesForSubscription(level: string): string[] {
    const features = {
      'BASIC': ['purchase_orders'],
      'PROFESSIONAL': ['purchase_orders', 'sales_orders', 'basic_analytics'],
      'ENTERPRISE': ['purchase_orders', 'sales_orders', 'delivery_tracking', 'advanced_analytics', 'multi_user', 'api_access']
    };
    return features[level] || features['BASIC'];
  }

  private getLimitsForSubscription(level: string): TenantLimits {
    const limits = {
      'BASIC': {
        maxUsers: 5,
        maxPurchaseOrders: 100,
        maxStorageGB: 1,
        maxAPICallsPerDay: 1000,
        allowedDomains: [],
        dataRetentionDays: 365
      },
      'PROFESSIONAL': {
        maxUsers: 25,
        maxPurchaseOrders: 1000,
        maxStorageGB: 10,
        maxAPICallsPerDay: 10000,
        allowedDomains: [],
        dataRetentionDays: 1095 // 3 years
      },
      'ENTERPRISE': {
        maxUsers: 1000,
        maxPurchaseOrders: 100000,
        maxStorageGB: 1000,
        maxAPICallsPerDay: 100000,
        allowedDomains: ['*'],
        dataRetentionDays: 2555 // 7 years
      }
    };
    return limits[level] || limits['BASIC'];
  }

  private getSecurityPolicyForSubscription(level: string): TenantSecurityPolicy {
    const policies = {
      'BASIC': {
        requireMFA: false,
        passwordPolicy: {
          minLength: 6,
          requireNumbers: false,
          requireSpecialChars: false,
          requireUppercase: false,
          expirationDays: 0
        },
        sessionTimeoutMinutes: 60,
        ipWhitelist: [],
        allowedFileTypes: ['pdf'],
        encryptionLevel: 'STANDARD' as const,
        auditLevel: 'BASIC' as const
      },
      'PROFESSIONAL': {
        requireMFA: false,
        passwordPolicy: {
          minLength: 8,
          requireNumbers: true,
          requireSpecialChars: false,
          requireUppercase: true,
          expirationDays: 180
        },
        sessionTimeoutMinutes: 240,
        ipWhitelist: [],
        allowedFileTypes: ['pdf', 'xlsx', 'docx'],
        encryptionLevel: 'HIGH' as const,
        auditLevel: 'DETAILED' as const
      },
      'ENTERPRISE': {
        requireMFA: true,
        passwordPolicy: {
          minLength: 12,
          requireNumbers: true,
          requireSpecialChars: true,
          requireUppercase: true,
          expirationDays: 90
        },
        sessionTimeoutMinutes: 480,
        ipWhitelist: [],
        allowedFileTypes: ['pdf', 'xlsx', 'docx', 'png', 'jpg'],
        encryptionLevel: 'MAXIMUM' as const,
        auditLevel: 'COMPREHENSIVE' as const
      }
    };
    return policies[level] || policies['BASIC'];
  }
}
