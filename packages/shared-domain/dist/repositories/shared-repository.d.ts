import { User, UserId, Tenant, TenantId, Permission, Role, AuditLog, Notification } from '../services/shared-domain-service';
export declare class SharedRepository extends Repository<User, UserId> {
    constructor();
    getUsersByTenant(tenantId: TenantId): Promise<User[]>;
    getUsersByRole(role: string): Promise<User[]>;
    getActiveUsers(): Promise<User[]>;
    getInactiveUsers(): Promise<User[]>;
    getUserByEmail(email: string): Promise<User | null>;
    getUsersByLastLogin(dateFrom: Date, dateTo: Date): Promise<User[]>;
    getRecentUsers(limit?: number): Promise<User[]>;
    getUserStatistics(): Promise<{
        totalUsers: number;
        activeUsers: number;
        inactiveUsers: number;
        usersByRole: Record<string, number>;
        usersByTenant: Record<string, number>;
        recentLogins: number;
    }>;
    getTenants(): Promise<Tenant[]>;
    getActiveTenants(): Promise<Tenant[]>;
    getInactiveTenants(): Promise<Tenant[]>;
    getTenantByDomain(domain: string): Promise<Tenant | null>;
    getTenantStatistics(): Promise<{
        totalTenants: number;
        activeTenants: number;
        inactiveTenants: number;
        averageUsersPerTenant: number;
    }>;
    getPermissions(): Promise<Permission[]>;
    getPermissionsByResource(resource: string): Promise<Permission[]>;
    getPermissionsByAction(action: string): Promise<Permission[]>;
    getPermissionStatistics(): Promise<{
        totalPermissions: number;
        permissionsByResource: Record<string, number>;
        permissionsByAction: Record<string, number>;
    }>;
    getRoles(): Promise<Role[]>;
    getRolesByTenant(tenantId: TenantId): Promise<Role[]>;
    getActiveRoles(): Promise<Role[]>;
    getRoleStatistics(): Promise<{
        totalRoles: number;
        activeRoles: number;
        inactiveRoles: number;
        rolesByTenant: Record<string, number>;
        averagePermissionsPerRole: number;
    }>;
    getAuditLogs(): Promise<AuditLog[]>;
    getAuditLogsByUser(userId: UserId): Promise<AuditLog[]>;
    getAuditLogsByTenant(tenantId: TenantId): Promise<AuditLog[]>;
    getAuditLogsByResource(resource: string): Promise<AuditLog[]>;
    getAuditLogsByDateRange(startDate: Date, endDate: Date): Promise<AuditLog[]>;
    getRecentAuditLogs(limit?: number): Promise<AuditLog[]>;
    getAuditLogStatistics(): Promise<{
        totalAuditLogs: number;
        auditLogsByAction: Record<string, number>;
        auditLogsByResource: Record<string, number>;
        auditLogsByUser: Record<string, number>;
        auditLogsByTenant: Record<string, number>;
        recentActivity: number;
    }>;
    getNotifications(): Promise<Notification[]>;
    getNotificationsByUser(userId: UserId): Promise<Notification[]>;
    getNotificationsByTenant(tenantId: TenantId): Promise<Notification[]>;
    getUnreadNotifications(userId: UserId): Promise<Notification[]>;
    getReadNotifications(userId: UserId): Promise<Notification[]>;
    getNotificationsByType(type: string): Promise<Notification[]>;
    getRecentNotifications(limit?: number): Promise<Notification[]>;
    getNotificationStatistics(): Promise<{
        totalNotifications: number;
        unreadNotifications: number;
        readNotifications: number;
        notificationsByType: Record<string, number>;
        notificationsByUser: Record<string, number>;
        notificationsByTenant: Record<string, number>;
    }>;
    getSystemHealth(): Promise<{
        totalUsers: number;
        totalTenants: number;
        totalPermissions: number;
        totalRoles: number;
        totalAuditLogs: number;
        totalNotifications: number;
        activeUsers: number;
        activeTenants: number;
        recentActivity: number;
        unreadNotifications: number;
        healthScore: number;
    }>;
}
export declare const sharedRepository: SharedRepository;
//# sourceMappingURL=shared-repository.d.ts.map