import { BaseService } from '@valero-neuroerp/utilities/base-service';
import { UserId, TenantId, PermissionId } from '@valero-neuroerp/data-models/branded-types';
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
export declare class SharedDomainService extends BaseService {
    constructor();
    private initializeBusinessRules;
    createUser(request: UserRequest): Promise<User>;
    updateUser(userId: UserId, updates: Partial<User>): Promise<User>;
    authenticateUser(email: string, password: string): Promise<User | null>;
    createTenant(name: string, domain: string, settings?: Record<string, any>): Promise<Tenant>;
    createPermission(name: string, resource: string, action: string, conditions?: Record<string, any>): Promise<Permission>;
    checkPermission(userId: UserId, resource: string, action: string): Promise<boolean>;
    logAuditEvent(userId: UserId, tenantId: TenantId, action: string, resource: string, resourceId: string, changes?: Record<string, any>, ipAddress?: string, userAgent?: string): Promise<AuditLog>;
    createNotification(userId: UserId, tenantId: TenantId, type: 'info' | 'warning' | 'error' | 'success', title: string, message: string): Promise<Notification>;
    markNotificationAsRead(notificationId: string): Promise<Notification>;
    getUser(userId: UserId): Promise<User | null>;
    getUsers(filters?: {
        tenantId?: TenantId;
        role?: string;
        isActive?: boolean;
    }): Promise<User[]>;
    getTenant(tenantId: TenantId): Promise<Tenant | null>;
    getTenants(): Promise<Tenant[]>;
    getPermissions(): Promise<Permission[]>;
    getAuditLogs(filters?: {
        userId?: UserId;
        tenantId?: TenantId;
        resource?: string;
        dateFrom?: Date;
        dateTo?: Date;
    }): Promise<AuditLog[]>;
    getNotifications(userId: UserId, isRead?: boolean): Promise<Notification[]>;
    private generateUserId;
    private generateTenantId;
    private generatePermissionId;
    private generateAuditLogId;
    private generateNotificationId;
    private getCurrentUserId;
    private publishDomainEvent;
}
export declare const sharedDomainService: SharedDomainService;
//# sourceMappingURL=shared-domain-service.d.ts.map