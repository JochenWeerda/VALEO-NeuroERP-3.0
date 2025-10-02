// domains/shared/src/repositories/shared-repository.ts
import { Repository } from '@packages/utilities/repository';
import { User, UserId, Tenant, TenantId, Permission, PermissionId, Role, AuditLog, Notification } from '../services/shared-domain-service';

export class SharedRepository extends Repository<User, UserId> {
  constructor() {
    super('users');
  }

  // User Queries
  async getUsersByTenant(tenantId: TenantId): Promise<User[]> {
    return this.find({ tenantId });
  }

  async getUsersByRole(role: string): Promise<User[]> {
    return this.find({ role });
  }

  async getActiveUsers(): Promise<User[]> {
    return this.find({ isActive: true });
  }

  async getInactiveUsers(): Promise<User[]> {
    return this.find({ isActive: false });
  }

  async getUserByEmail(email: string): Promise<User | null> {
    const users = await this.find({ email });
    return users.length > 0 ? users[0] : null;
  }

  async getUsersByLastLogin(dateFrom: Date, dateTo: Date): Promise<User[]> {
    return this.find({
      lastLoginAt: { $gte: dateFrom, $lte: dateTo }
    });
  }

  async getRecentUsers(limit: number = 50): Promise<User[]> {
    const allUsers = await this.findAll();
    return allUsers
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, limit);
  }

  async getUserStatistics(): Promise<{
    totalUsers: number;
    activeUsers: number;
    inactiveUsers: number;
    usersByRole: Record<string, number>;
    usersByTenant: Record<string, number>;
    recentLogins: number;
  }> {
    const allUsers = await this.findAll();
    
    const usersByRole = allUsers.reduce((acc, user) => {
      acc[user.role] = (acc[user.role] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const usersByTenant = allUsers.reduce((acc, user) => {
      acc[user.tenantId] = (acc[user.tenantId] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const recentLogins = allUsers.filter(user => {
      if (!user.lastLoginAt) return false;
      const daysSinceLogin = Math.floor((Date.now() - user.lastLoginAt.getTime()) / (1000 * 60 * 60 * 24));
      return daysSinceLogin <= 7;
    }).length;

    return {
      totalUsers: allUsers.length,
      activeUsers: allUsers.filter(user => user.isActive).length,
      inactiveUsers: allUsers.filter(user => !user.isActive).length,
      usersByRole,
      usersByTenant,
      recentLogins
    };
  }

  // Tenant Queries
  async getTenants(): Promise<Tenant[]> {
    return this.repository.findAll();
  }

  async getActiveTenants(): Promise<Tenant[]> {
    return this.repository.find({ isActive: true });
  }

  async getInactiveTenants(): Promise<Tenant[]> {
    return this.repository.find({ isActive: false });
  }

  async getTenantByDomain(domain: string): Promise<Tenant | null> {
    const tenants = await this.repository.find({ domain });
    return tenants.length > 0 ? tenants[0] : null;
  }

  async getTenantStatistics(): Promise<{
    totalTenants: number;
    activeTenants: number;
    inactiveTenants: number;
    averageUsersPerTenant: number;
  }> {
    const allTenants = await this.getTenants();
    const allUsers = await this.findAll();
    
    const averageUsersPerTenant = allTenants.length > 0 
      ? allUsers.length / allTenants.length 
      : 0;

    return {
      totalTenants: allTenants.length,
      activeTenants: allTenants.filter(tenant => tenant.isActive).length,
      inactiveTenants: allTenants.filter(tenant => !tenant.isActive).length,
      averageUsersPerTenant
    };
  }

  // Permission Queries
  async getPermissions(): Promise<Permission[]> {
    return this.repository.findAll();
  }

  async getPermissionsByResource(resource: string): Promise<Permission[]> {
    return this.repository.find({ resource });
  }

  async getPermissionsByAction(action: string): Promise<Permission[]> {
    return this.repository.find({ action });
  }

  async getPermissionStatistics(): Promise<{
    totalPermissions: number;
    permissionsByResource: Record<string, number>;
    permissionsByAction: Record<string, number>;
  }> {
    const allPermissions = await this.getPermissions();
    
    const permissionsByResource = allPermissions.reduce((acc, permission) => {
      acc[permission.resource] = (acc[permission.resource] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const permissionsByAction = allPermissions.reduce((acc, permission) => {
      acc[permission.action] = (acc[permission.action] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalPermissions: allPermissions.length,
      permissionsByResource,
      permissionsByAction
    };
  }

  // Role Queries
  async getRoles(): Promise<Role[]> {
    return this.repository.findAll();
  }

  async getRolesByTenant(tenantId: TenantId): Promise<Role[]> {
    return this.repository.find({ tenantId });
  }

  async getActiveRoles(): Promise<Role[]> {
    return this.repository.find({ isActive: true });
  }

  async getRoleStatistics(): Promise<{
    totalRoles: number;
    activeRoles: number;
    inactiveRoles: number;
    rolesByTenant: Record<string, number>;
    averagePermissionsPerRole: number;
  }> {
    const allRoles = await this.getRoles();
    const allPermissions = await this.getPermissions();
    
    const rolesByTenant = allRoles.reduce((acc, role) => {
      acc[role.tenantId] = (acc[role.tenantId] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const totalPermissions = allRoles.reduce((sum, role) => sum + role.permissions.length, 0);
    const averagePermissionsPerRole = allRoles.length > 0 ? totalPermissions / allRoles.length : 0;

    return {
      totalRoles: allRoles.length,
      activeRoles: allRoles.filter(role => role.isActive).length,
      inactiveRoles: allRoles.filter(role => !role.isActive).length,
      rolesByTenant,
      averagePermissionsPerRole
    };
  }

  // Audit Log Queries
  async getAuditLogs(): Promise<AuditLog[]> {
    return this.repository.findAll();
  }

  async getAuditLogsByUser(userId: UserId): Promise<AuditLog[]> {
    return this.repository.find({ userId });
  }

  async getAuditLogsByTenant(tenantId: TenantId): Promise<AuditLog[]> {
    return this.repository.find({ tenantId });
  }

  async getAuditLogsByResource(resource: string): Promise<AuditLog[]> {
    return this.repository.find({ resource });
  }

  async getAuditLogsByDateRange(startDate: Date, endDate: Date): Promise<AuditLog[]> {
    return this.repository.find({
      timestamp: { $gte: startDate, $lte: endDate }
    });
  }

  async getRecentAuditLogs(limit: number = 100): Promise<AuditLog[]> {
    const allAuditLogs = await this.getAuditLogs();
    return allAuditLogs
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
  }

  async getAuditLogStatistics(): Promise<{
    totalAuditLogs: number;
    auditLogsByAction: Record<string, number>;
    auditLogsByResource: Record<string, number>;
    auditLogsByUser: Record<string, number>;
    auditLogsByTenant: Record<string, number>;
    recentActivity: number;
  }> {
    const allAuditLogs = await this.getAuditLogs();
    
    const auditLogsByAction = allAuditLogs.reduce((acc, log) => {
      acc[log.action] = (acc[log.action] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const auditLogsByResource = allAuditLogs.reduce((acc, log) => {
      acc[log.resource] = (acc[log.resource] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const auditLogsByUser = allAuditLogs.reduce((acc, log) => {
      acc[log.userId] = (acc[log.userId] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const auditLogsByTenant = allAuditLogs.reduce((acc, log) => {
      acc[log.tenantId] = (acc[log.tenantId] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const recentActivity = allAuditLogs.filter(log => {
      const daysSinceActivity = Math.floor((Date.now() - log.timestamp.getTime()) / (1000 * 60 * 60 * 24));
      return daysSinceActivity <= 1;
    }).length;

    return {
      totalAuditLogs: allAuditLogs.length,
      auditLogsByAction,
      auditLogsByResource,
      auditLogsByUser,
      auditLogsByTenant,
      recentActivity
    };
  }

  // Notification Queries
  async getNotifications(): Promise<Notification[]> {
    return this.repository.findAll();
  }

  async getNotificationsByUser(userId: UserId): Promise<Notification[]> {
    return this.repository.find({ userId });
  }

  async getNotificationsByTenant(tenantId: TenantId): Promise<Notification[]> {
    return this.repository.find({ tenantId });
  }

  async getUnreadNotifications(userId: UserId): Promise<Notification[]> {
    return this.repository.find({ userId, isRead: false });
  }

  async getReadNotifications(userId: UserId): Promise<Notification[]> {
    return this.repository.find({ userId, isRead: true });
  }

  async getNotificationsByType(type: string): Promise<Notification[]> {
    return this.repository.find({ type });
  }

  async getRecentNotifications(limit: number = 50): Promise<Notification[]> {
    const allNotifications = await this.getNotifications();
    return allNotifications
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, limit);
  }

  async getNotificationStatistics(): Promise<{
    totalNotifications: number;
    unreadNotifications: number;
    readNotifications: number;
    notificationsByType: Record<string, number>;
    notificationsByUser: Record<string, number>;
    notificationsByTenant: Record<string, number>;
  }> {
    const allNotifications = await this.getNotifications();
    
    const notificationsByType = allNotifications.reduce((acc, notification) => {
      acc[notification.type] = (acc[notification.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const notificationsByUser = allNotifications.reduce((acc, notification) => {
      acc[notification.userId] = (acc[notification.userId] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const notificationsByTenant = allNotifications.reduce((acc, notification) => {
      acc[notification.tenantId] = (acc[notification.tenantId] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    return {
      totalNotifications: allNotifications.length,
      unreadNotifications: allNotifications.filter(n => !n.isRead).length,
      readNotifications: allNotifications.filter(n => n.isRead).length,
      notificationsByType,
      notificationsByUser,
      notificationsByTenant
    };
  }

  // System Health Queries
  async getSystemHealth(): Promise<{
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
  }> {
    const userStats = await this.getUserStatistics();
    const tenantStats = await this.getTenantStatistics();
    const permissionStats = await this.getPermissionStatistics();
    const roleStats = await this.getRoleStatistics();
    const auditStats = await this.getAuditLogStatistics();
    const notificationStats = await this.getNotificationStatistics();

    // Calculate health score based on various metrics
    const healthScore = Math.min(100, Math.max(0, 
      (userStats.activeUsers / Math.max(userStats.totalUsers, 1)) * 25 +
      (tenantStats.activeTenants / Math.max(tenantStats.totalTenants, 1)) * 25 +
      (auditStats.recentActivity > 0 ? 25 : 0) +
      (notificationStats.unreadNotifications < 100 ? 25 : 0)
    ));

    return {
      totalUsers: userStats.totalUsers,
      totalTenants: tenantStats.totalTenants,
      totalPermissions: permissionStats.totalPermissions,
      totalRoles: roleStats.totalRoles,
      totalAuditLogs: auditStats.totalAuditLogs,
      totalNotifications: notificationStats.totalNotifications,
      activeUsers: userStats.activeUsers,
      activeTenants: tenantStats.activeTenants,
      recentActivity: auditStats.recentActivity,
      unreadNotifications: notificationStats.unreadNotifications,
      healthScore
    };
  }
}

export const sharedRepository = new SharedRepository();
