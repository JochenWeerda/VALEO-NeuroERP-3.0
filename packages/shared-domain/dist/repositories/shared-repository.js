"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.sharedRepository = exports.SharedRepository = void 0;
class SharedRepository extends repository_1.Repository {
    constructor() {
        super('users');
    }
    // User Queries
    async getUsersByTenant(tenantId) {
        return this.find({ tenantId });
    }
    async getUsersByRole(role) {
        return this.find({ role });
    }
    async getActiveUsers() {
        return this.find({ isActive: true });
    }
    async getInactiveUsers() {
        return this.find({ isActive: false });
    }
    async getUserByEmail(email) {
        const users = await this.find({ email });
        return users.length > 0 ? users[0] : null;
    }
    async getUsersByLastLogin(dateFrom, dateTo) {
        return this.find({
            lastLoginAt: { $gte: dateFrom, $lte: dateTo }
        });
    }
    async getRecentUsers(limit = 50) {
        const allUsers = await this.findAll();
        return allUsers
            .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
            .slice(0, limit);
    }
    async getUserStatistics() {
        const allUsers = await this.findAll();
        const usersByRole = allUsers.reduce((acc, user) => {
            acc[user.role] = (acc[user.role] || 0) + 1;
            return acc;
        }, {});
        const usersByTenant = allUsers.reduce((acc, user) => {
            acc[user.tenantId] = (acc[user.tenantId] || 0) + 1;
            return acc;
        }, {});
        const recentLogins = allUsers.filter(user => {
            if (!user.lastLoginAt)
                return false;
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
    async getTenants() {
        return this.repository.findAll();
    }
    async getActiveTenants() {
        return this.repository.find({ isActive: true });
    }
    async getInactiveTenants() {
        return this.repository.find({ isActive: false });
    }
    async getTenantByDomain(domain) {
        const tenants = await this.repository.find({ domain });
        return tenants.length > 0 ? tenants[0] : null;
    }
    async getTenantStatistics() {
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
    async getPermissions() {
        return this.repository.findAll();
    }
    async getPermissionsByResource(resource) {
        return this.repository.find({ resource });
    }
    async getPermissionsByAction(action) {
        return this.repository.find({ action });
    }
    async getPermissionStatistics() {
        const allPermissions = await this.getPermissions();
        const permissionsByResource = allPermissions.reduce((acc, permission) => {
            acc[permission.resource] = (acc[permission.resource] || 0) + 1;
            return acc;
        }, {});
        const permissionsByAction = allPermissions.reduce((acc, permission) => {
            acc[permission.action] = (acc[permission.action] || 0) + 1;
            return acc;
        }, {});
        return {
            totalPermissions: allPermissions.length,
            permissionsByResource,
            permissionsByAction
        };
    }
    // Role Queries
    async getRoles() {
        return this.repository.findAll();
    }
    async getRolesByTenant(tenantId) {
        return this.repository.find({ tenantId });
    }
    async getActiveRoles() {
        return this.repository.find({ isActive: true });
    }
    async getRoleStatistics() {
        const allRoles = await this.getRoles();
        const allPermissions = await this.getPermissions();
        const rolesByTenant = allRoles.reduce((acc, role) => {
            acc[role.tenantId] = (acc[role.tenantId] || 0) + 1;
            return acc;
        }, {});
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
    async getAuditLogs() {
        return this.repository.findAll();
    }
    async getAuditLogsByUser(userId) {
        return this.repository.find({ userId });
    }
    async getAuditLogsByTenant(tenantId) {
        return this.repository.find({ tenantId });
    }
    async getAuditLogsByResource(resource) {
        return this.repository.find({ resource });
    }
    async getAuditLogsByDateRange(startDate, endDate) {
        return this.repository.find({
            timestamp: { $gte: startDate, $lte: endDate }
        });
    }
    async getRecentAuditLogs(limit = 100) {
        const allAuditLogs = await this.getAuditLogs();
        return allAuditLogs
            .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
            .slice(0, limit);
    }
    async getAuditLogStatistics() {
        const allAuditLogs = await this.getAuditLogs();
        const auditLogsByAction = allAuditLogs.reduce((acc, log) => {
            acc[log.action] = (acc[log.action] || 0) + 1;
            return acc;
        }, {});
        const auditLogsByResource = allAuditLogs.reduce((acc, log) => {
            acc[log.resource] = (acc[log.resource] || 0) + 1;
            return acc;
        }, {});
        const auditLogsByUser = allAuditLogs.reduce((acc, log) => {
            acc[log.userId] = (acc[log.userId] || 0) + 1;
            return acc;
        }, {});
        const auditLogsByTenant = allAuditLogs.reduce((acc, log) => {
            acc[log.tenantId] = (acc[log.tenantId] || 0) + 1;
            return acc;
        }, {});
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
    async getNotifications() {
        return this.repository.findAll();
    }
    async getNotificationsByUser(userId) {
        return this.repository.find({ userId });
    }
    async getNotificationsByTenant(tenantId) {
        return this.repository.find({ tenantId });
    }
    async getUnreadNotifications(userId) {
        return this.repository.find({ userId, isRead: false });
    }
    async getReadNotifications(userId) {
        return this.repository.find({ userId, isRead: true });
    }
    async getNotificationsByType(type) {
        return this.repository.find({ type });
    }
    async getRecentNotifications(limit = 50) {
        const allNotifications = await this.getNotifications();
        return allNotifications
            .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
            .slice(0, limit);
    }
    async getNotificationStatistics() {
        const allNotifications = await this.getNotifications();
        const notificationsByType = allNotifications.reduce((acc, notification) => {
            acc[notification.type] = (acc[notification.type] || 0) + 1;
            return acc;
        }, {});
        const notificationsByUser = allNotifications.reduce((acc, notification) => {
            acc[notification.userId] = (acc[notification.userId] || 0) + 1;
            return acc;
        }, {});
        const notificationsByTenant = allNotifications.reduce((acc, notification) => {
            acc[notification.tenantId] = (acc[notification.tenantId] || 0) + 1;
            return acc;
        }, {});
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
    async getSystemHealth() {
        const userStats = await this.getUserStatistics();
        const tenantStats = await this.getTenantStatistics();
        const permissionStats = await this.getPermissionStatistics();
        const roleStats = await this.getRoleStatistics();
        const auditStats = await this.getAuditLogStatistics();
        const notificationStats = await this.getNotificationStatistics();
        // Calculate health score based on various metrics
        const healthScore = Math.min(100, Math.max(0, (userStats.activeUsers / Math.max(userStats.totalUsers, 1)) * 25 +
            (tenantStats.activeTenants / Math.max(tenantStats.totalTenants, 1)) * 25 +
            (auditStats.recentActivity > 0 ? 25 : 0) +
            (notificationStats.unreadNotifications < 100 ? 25 : 0)));
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
exports.SharedRepository = SharedRepository;
exports.sharedRepository = new SharedRepository();
//# sourceMappingURL=shared-repository.js.map