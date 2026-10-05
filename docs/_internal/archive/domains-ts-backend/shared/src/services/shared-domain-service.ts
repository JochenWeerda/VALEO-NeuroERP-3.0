// domains/shared/src/services/shared-domain-service.ts
import { BaseService } from '@packages/utilities/base-service';
import { UserId, TenantId, PermissionId } from '@packages/data-models/branded-types';
import { businessLogicOrchestrator } from '@packages/business-rules/business-logic-orchestrator';

export interface User {
  id: UserId;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  tenantId: TenantId;
  isActive: boolean;
  lastLoginAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

export interface Tenant {
  id: TenantId;
  name: string;
  domain: string;
  settings: Record<string, any>;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Permission {
  id: PermissionId;
  name: string;
  resource: string;
  action: string;
  conditions?: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: PermissionId[];
  tenantId: TenantId;
  isActive: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface AuditLog {
  id: string;
  userId: UserId;
  tenantId: TenantId;
  action: string;
  resource: string;
  resourceId: string;
  changes?: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
  timestamp: Date;
}

export interface Notification {
  id: string;
  userId: UserId;
  tenantId: TenantId;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  isRead: boolean;
  createdAt: Date;
  readAt?: Date;
}

export interface UserRequest {
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  tenantId: TenantId;
}

export class SharedDomainService extends BaseService {
  constructor() {
    super();
    this.initializeBusinessRules();
  }

  private initializeBusinessRules(): void {
    businessLogicOrchestrator.registerRule('Shared', new UserValidationRule());
    businessLogicOrchestrator.registerRule('Shared', new TenantValidationRule());
    businessLogicOrchestrator.registerRule('Shared', new PermissionValidationRule());
  }

  // User Management
  async createUser(request: UserRequest): Promise<User> {
    const context = {
      userId: this.getCurrentUserId(),
      timestamp: new Date(),
      operation: 'create' as const,
      domain: 'Shared',
      metadata: { source: 'shared-service' }
    };

    const result = await businessLogicOrchestrator.executeBusinessLogic(
      'Shared',
      request,
      'create',
      context
    );

    if (!result.success) {
      throw new Error(`User creation failed: ${result.errors.map(e => e.message).join(', ')}`);
    }

    const user: User = {
      id: this.generateUserId(),
      ...result.data,
      isActive: true,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    await this.repository.create(user);

    await this.publishDomainEvent('UserCreated', {
      userId: user.id,
      userEmail: user.email,
      tenantId: user.tenantId,
      timestamp: new Date()
    });

    return user;
  }

  async updateUser(userId: UserId, updates: Partial<User>): Promise<User> {
    const existingUser = await this.repository.findById(userId);
    if (!existingUser) {
      throw new Error(`User ${userId} not found`);
    }

    const context = {
      userId: this.getCurrentUserId(),
      timestamp: new Date(),
      operation: 'update' as const,
      domain: 'Shared',
      metadata: { source: 'shared-service', userId }
    };

    const updateData = { ...existingUser, ...updates };

    const result = await businessLogicOrchestrator.executeBusinessLogic(
      'Shared',
      updateData,
      'update',
      context
    );

    if (!result.success) {
      throw new Error(`User update failed: ${result.errors.map(e => e.message).join(', ')}`);
    }

    const updatedUser: User = {
      ...result.data,
      updatedAt: new Date()
    };

    await this.repository.update(userId, updatedUser);

    await this.publishDomainEvent('UserUpdated', {
      userId: updatedUser.id,
      changes: updates,
      timestamp: new Date()
    });

    return updatedUser;
  }

  async authenticateUser(email: string, password: string): Promise<User | null> {
    const users = await this.repository.find({ email });
    const user = users.find(u => u.isActive);
    
    if (!user) {
      return null;
    }

    // In a real implementation, you would verify the password hash
    // For now, we'll just simulate authentication
    const isAuthenticated = password === 'password'; // Simplified for demo
    
    if (isAuthenticated) {
      await this.updateUser(user.id, { lastLoginAt: new Date() });
      
      await this.publishDomainEvent('UserAuthenticated', {
        userId: user.id,
        userEmail: user.email,
        timestamp: new Date()
      });
      
      return user;
    }
    
    return null;
  }

  // Tenant Management
  async createTenant(name: string, domain: string, settings: Record<string, any> = {}): Promise<Tenant> {
    const context = {
      userId: this.getCurrentUserId(),
      timestamp: new Date(),
      operation: 'create' as const,
      domain: 'Shared',
      metadata: { source: 'shared-service' }
    };

    const tenantData = { name, domain, settings };

    const result = await businessLogicOrchestrator.executeBusinessLogic(
      'Shared',
      tenantData,
      'create',
      context
    );

    if (!result.success) {
      throw new Error(`Tenant creation failed: ${result.errors.map(e => e.message).join(', ')}`);
    }

    const tenant: Tenant = {
      id: this.generateTenantId(),
      ...result.data,
      isActive: true,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    await this.repository.create(tenant);

    await this.publishDomainEvent('TenantCreated', {
      tenantId: tenant.id,
      tenantName: tenant.name,
      tenantDomain: tenant.domain,
      timestamp: new Date()
    });

    return tenant;
  }

  // Permission Management
  async createPermission(name: string, resource: string, action: string, conditions?: Record<string, any>): Promise<Permission> {
    const context = {
      userId: this.getCurrentUserId(),
      timestamp: new Date(),
      operation: 'create' as const,
      domain: 'Shared',
      metadata: { source: 'shared-service' }
    };

    const permissionData = { name, resource, action, conditions };

    const result = await businessLogicOrchestrator.executeBusinessLogic(
      'Shared',
      permissionData,
      'create',
      context
    );

    if (!result.success) {
      throw new Error(`Permission creation failed: ${result.errors.map(e => e.message).join(', ')}`);
    }

    const permission: Permission = {
      id: this.generatePermissionId(),
      ...result.data,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    await this.repository.create(permission);

    await this.publishDomainEvent('PermissionCreated', {
      permissionId: permission.id,
      permissionName: permission.name,
      resource: permission.resource,
      action: permission.action,
      timestamp: new Date()
    });

    return permission;
  }

  async checkPermission(userId: UserId, resource: string, action: string): Promise<boolean> {
    const user = await this.repository.findById(userId);
    if (!user || !user.isActive) {
      return false;
    }

    // In a real implementation, you would check user roles and permissions
    // For now, we'll simulate permission checking
    return true; // Simplified for demo
  }

  // Audit Logging
  async logAuditEvent(
    userId: UserId,
    tenantId: TenantId,
    action: string,
    resource: string,
    resourceId: string,
    changes?: Record<string, any>,
    ipAddress?: string,
    userAgent?: string
  ): Promise<AuditLog> {
    const auditLog: AuditLog = {
      id: this.generateAuditLogId(),
      userId,
      tenantId,
      action,
      resource,
      resourceId,
      changes,
      ipAddress,
      userAgent,
      timestamp: new Date()
    };

    await this.repository.create(auditLog);

    await this.publishDomainEvent('AuditEventLogged', {
      auditLogId: auditLog.id,
      userId: auditLog.userId,
      action: auditLog.action,
      resource: auditLog.resource,
      timestamp: new Date()
    });

    return auditLog;
  }

  // Notification Management
  async createNotification(
    userId: UserId,
    tenantId: TenantId,
    type: 'info' | 'warning' | 'error' | 'success',
    title: string,
    message: string
  ): Promise<Notification> {
    const notification: Notification = {
      id: this.generateNotificationId(),
      userId,
      tenantId,
      type,
      title,
      message,
      isRead: false,
      createdAt: new Date()
    };

    await this.repository.create(notification);

    await this.publishDomainEvent('NotificationCreated', {
      notificationId: notification.id,
      userId: notification.userId,
      type: notification.type,
      title: notification.title,
      timestamp: new Date()
    });

    return notification;
  }

  async markNotificationAsRead(notificationId: string): Promise<Notification> {
    const notification = await this.repository.findById(notificationId);
    if (!notification) {
      throw new Error(`Notification ${notificationId} not found`);
    }

    const updatedNotification: Notification = {
      ...notification,
      isRead: true,
      readAt: new Date()
    };

    await this.repository.update(notificationId, updatedNotification);

    await this.publishDomainEvent('NotificationRead', {
      notificationId: updatedNotification.id,
      userId: updatedNotification.userId,
      timestamp: new Date()
    });

    return updatedNotification;
  }

  // Helper Methods
  async getUser(userId: UserId): Promise<User | null> {
    return this.repository.findById(userId);
  }

  async getUsers(filters?: {
    tenantId?: TenantId;
    role?: string;
    isActive?: boolean;
  }): Promise<User[]> {
    return this.repository.find(filters);
  }

  async getTenant(tenantId: TenantId): Promise<Tenant | null> {
    return this.repository.findById(tenantId);
  }

  async getTenants(): Promise<Tenant[]> {
    return this.repository.findAll();
  }

  async getPermissions(): Promise<Permission[]> {
    return this.repository.findAll();
  }

  async getAuditLogs(filters?: {
    userId?: UserId;
    tenantId?: TenantId;
    resource?: string;
    dateFrom?: Date;
    dateTo?: Date;
  }): Promise<AuditLog[]> {
    return this.repository.find(filters);
  }

  async getNotifications(userId: UserId, isRead?: boolean): Promise<Notification[]> {
    const filters: any = { userId };
    if (isRead !== undefined) {
      filters.isRead = isRead;
    }
    return this.repository.find(filters);
  }

  private generateUserId(): UserId {
    return `USER_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` as UserId;
  }

  private generateTenantId(): TenantId {
    return `TENANT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` as TenantId;
  }

  private generatePermissionId(): PermissionId {
    return `PERM_${Date.now()}_${Math.random().toString(36).substr(2, 9)}` as PermissionId;
  }

  private generateAuditLogId(): string {
    return `AUDIT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private generateNotificationId(): string {
    return `NOTIF_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getCurrentUserId(): string {
    return 'system';
  }

  private async publishDomainEvent(eventType: string, data: any): Promise<void> {
    console.log(`Publishing domain event: ${eventType}`, data);
  }
}

// Shared Business Rules
class UserValidationRule {
  name = 'SHARED_USER_VALIDATION';
  description = 'Validates user creation and updates';
  priority = 100;
  domain = 'Shared';
  version = '1.0.0';
  enabled = true;

  async validate(data: any): Promise<any> {
    const errors: any[] = [];
    const warnings: any[] = [];

    if (!data.email || data.email.trim().length === 0) {
      errors.push({
        field: 'email',
        message: 'Email is required',
        code: 'SHARED_USER_EMAIL_REQUIRED',
        severity: 'error'
      });
    } else if (!this.isValidEmail(data.email)) {
      errors.push({
        field: 'email',
        message: 'Invalid email format',
        code: 'SHARED_USER_INVALID_EMAIL',
        severity: 'error'
      });
    }

    if (!data.firstName || data.firstName.trim().length === 0) {
      errors.push({
        field: 'firstName',
        message: 'First name is required',
        code: 'SHARED_USER_FIRST_NAME_REQUIRED',
        severity: 'error'
      });
    }

    if (!data.lastName || data.lastName.trim().length === 0) {
      errors.push({
        field: 'lastName',
        message: 'Last name is required',
        code: 'SHARED_USER_LAST_NAME_REQUIRED',
        severity: 'error'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
}

class TenantValidationRule {
  name = 'SHARED_TENANT_VALIDATION';
  description = 'Validates tenant creation';
  priority = 95;
  domain = 'Shared';
  version = '1.0.0';
  enabled = true;

  async validate(data: any): Promise<any> {
    const errors: any[] = [];
    const warnings: any[] = [];

    if (!data.name || data.name.trim().length === 0) {
      errors.push({
        field: 'name',
        message: 'Tenant name is required',
        code: 'SHARED_TENANT_NAME_REQUIRED',
        severity: 'error'
      });
    }

    if (!data.domain || data.domain.trim().length === 0) {
      errors.push({
        field: 'domain',
        message: 'Tenant domain is required',
        code: 'SHARED_TENANT_DOMAIN_REQUIRED',
        severity: 'error'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}

class PermissionValidationRule {
  name = 'SHARED_PERMISSION_VALIDATION';
  description = 'Validates permission creation';
  priority = 90;
  domain = 'Shared';
  version = '1.0.0';
  enabled = true;

  async validate(data: any): Promise<any> {
    const errors: any[] = [];
    const warnings: any[] = [];

    if (!data.name || data.name.trim().length === 0) {
      errors.push({
        field: 'name',
        message: 'Permission name is required',
        code: 'SHARED_PERMISSION_NAME_REQUIRED',
        severity: 'error'
      });
    }

    if (!data.resource || data.resource.trim().length === 0) {
      errors.push({
        field: 'resource',
        message: 'Resource is required',
        code: 'SHARED_PERMISSION_RESOURCE_REQUIRED',
        severity: 'error'
      });
    }

    if (!data.action || data.action.trim().length === 0) {
      errors.push({
        field: 'action',
        message: 'Action is required',
        code: 'SHARED_PERMISSION_ACTION_REQUIRED',
        severity: 'error'
      });
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}

export const sharedDomainService = new SharedDomainService();
