/**
 * User Application Service for VALEO NeuroERP 3.0
 * Orchestrates user-related business operations
 */
import { UserUseCases } from '../use-cases/user-use-cases.js';
export class UserApplicationService {
    userUseCases;
    constructor(userRepository, eventPublisher) {
        this.userUseCases = new UserUseCases(userRepository, eventPublisher);
    }
    // User Management Operations
    async createUser(dto, createdBy) {
        return this.userUseCases.createUser({
            username: dto.username,
            email: dto.email,
            firstName: dto.firstName,
            lastName: dto.lastName,
            phoneNumber: dto.phoneNumber,
            address: dto.address,
            tenantId: dto.tenantId,
            roles: dto.roles,
            createdBy
        });
    }
    async updateUser(userId, dto, updatedBy) {
        return this.userUseCases.updateUser({
            userId,
            firstName: dto.firstName,
            lastName: dto.lastName,
            phoneNumber: dto.phoneNumber,
            address: dto.address,
            updatedBy
        });
    }
    async getUser(userId) {
        return this.userUseCases.getUser({ userId });
    }
    async deleteUser(userId, deletedBy) {
        const user = await this.userUseCases.getUser({ userId });
        if (!user) {
            throw new Error(`User with ID '${userId}' not found`);
        }
        // Soft delete by deactivating the user
        await this.userUseCases.deactivateUser({
            userId,
            deactivatedBy: deletedBy,
            reason: 'User deleted'
        });
    }
    // User Status Operations
    async activateUser(userId, activatedBy) {
        return this.userUseCases.activateUser({ userId, activatedBy });
    }
    async deactivateUser(userId, deactivatedBy, reason) {
        return this.userUseCases.deactivateUser({ userId, deactivatedBy, reason });
    }
    async verifyUserEmail(userId) {
        return this.userUseCases.verifyUserEmail(userId);
    }
    // Role Management Operations
    async addRoleToUser(userId, roleId, addedBy) {
        return this.userUseCases.addRoleToUser({ userId, roleId, addedBy });
    }
    async removeRoleFromUser(userId, roleId, removedBy) {
        return this.userUseCases.removeRoleFromUser({ userId, roleId, removedBy });
    }
    async getUserRoles(userId) {
        const user = await this.userUseCases.getUser({ userId });
        return user ? user.roles : [];
    }
    async userHasRole(userId, roleId) {
        const user = await this.userUseCases.getUser({ userId });
        return user ? user.hasRole(roleId) : false;
    }
    // Authentication Operations
    async loginUser(userId, ipAddress, userAgent, sessionId) {
        return this.userUseCases.loginUser({
            userId,
            ipAddress,
            userAgent,
            sessionId
        });
    }
    async canUserLogin(userId) {
        const user = await this.userUseCases.getUser({ userId });
        return user ? user.canLogin() : false;
    }
    // Search and Query Operations
    async searchUsers(searchDto, pagination) {
        return this.userUseCases.searchUsers({
            searchTerm: searchDto.searchTerm,
            tenantId: searchDto.tenantId,
            roleId: searchDto.roleId,
            isActive: searchDto.isActive,
            isEmailVerified: searchDto.isEmailVerified,
            pagination
        });
    }
    async getUsersByTenant(tenantId, pagination) {
        return this.userUseCases.searchUsers({
            tenantId,
            pagination
        });
    }
    async getUsersByRole(roleId, pagination) {
        return this.userUseCases.searchUsers({
            roleId,
            pagination
        });
    }
    async getActiveUsers(pagination) {
        return this.userUseCases.searchUsers({
            isActive: true,
            pagination
        });
    }
    async getInactiveUsers(pagination) {
        return this.userUseCases.searchUsers({
            isActive: false,
            pagination
        });
    }
    // Statistics Operations
    async getUserStats(tenantId) {
        return this.userUseCases.getUserStats({ tenantId });
    }
    async getUserCount() {
        const stats = await this.userUseCases.getUserStats({});
        return stats.totalUsers;
    }
    async getActiveUserCount() {
        const stats = await this.userUseCases.getUserStats({});
        return stats.activeUsers;
    }
    async getInactiveUserCount() {
        const stats = await this.userUseCases.getUserStats({});
        return stats.inactiveUsers;
    }
    // Validation Operations
    async isUsernameAvailable(username) {
        // This would typically be implemented in the repository
        // For now, we'll use a simple approach
        try {
            // If findByUsername returns null, username is available
            const user = await this.userUseCases.getUser({ userId: username });
            return user === null;
        }
        catch {
            return true; // If there's an error, assume username is available
        }
    }
    async isEmailAvailable(email) {
        // Similar to username availability check
        try {
            // This would need to be implemented in the repository
            return true;
        }
        catch {
            return true;
        }
    }
    // Bulk Operations
    async bulkActivateUsers(userIds, activatedBy) {
        const promises = userIds.map(userId => this.userUseCases.activateUser({ userId, activatedBy }));
        await Promise.all(promises);
    }
    async bulkDeactivateUsers(userIds, deactivatedBy, reason) {
        const promises = userIds.map(userId => this.userUseCases.deactivateUser({ userId, deactivatedBy, reason }));
        await Promise.all(promises);
    }
    async bulkAddRoleToUsers(userIds, roleId, addedBy) {
        const promises = userIds.map(userId => this.userUseCases.addRoleToUser({ userId, roleId, addedBy }));
        await Promise.all(promises);
    }
    async bulkRemoveRoleFromUsers(userIds, roleId, removedBy) {
        const promises = userIds.map(userId => this.userUseCases.removeRoleFromUser({ userId, roleId, removedBy }));
        await Promise.all(promises);
    }
}
//# sourceMappingURL=user-application-service.js.map