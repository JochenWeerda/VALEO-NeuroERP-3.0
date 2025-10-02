/**
 * In-Memory User Repository Implementation for VALEO NeuroERP 3.0
 * Development and testing repository implementation
 */
import { BaseRepository } from './base-repository.js';
export class InMemoryUserRepository extends BaseRepository {
    users = new Map();
    usernameIndex = new Map();
    emailIndex = new Map();
    tenantIndex = new Map();
    roleIndex = new Map();
    async findById(id) {
        return this.users.get(id) || null;
    }
    async findAll() {
        return Array.from(this.users.values());
    }
    async save(user) {
        this.users.set(user.id, user);
        this.updateIndexes(user);
        return user;
    }
    async update(user) {
        this.users.set(user.id, user);
        this.updateIndexes(user);
        return user;
    }
    async delete(id) {
        const user = this.users.get(id);
        if (user) {
            this.removeFromIndexes(user);
            this.users.delete(id);
        }
    }
    // User-specific query methods
    async findByUsername(username) {
        const userId = this.usernameIndex.get(username.toLowerCase());
        return userId ? this.users.get(userId) || null : null;
    }
    async findByEmail(email) {
        const userId = this.emailIndex.get(email.toLowerCase());
        return userId ? this.users.get(userId) || null : null;
    }
    async findByTenant(tenantId) {
        const userIds = this.tenantIndex.get(tenantId) || new Set();
        return Array.from(userIds).map(id => this.users.get(id)).filter(Boolean);
    }
    async findByRole(roleId) {
        const userIds = this.roleIndex.get(roleId) || new Set();
        return Array.from(userIds).map(id => this.users.get(id)).filter(Boolean);
    }
    async findActiveUsers() {
        return Array.from(this.users.values()).filter(user => user.isActive);
    }
    async findInactiveUsers() {
        return Array.from(this.users.values()).filter(user => !user.isActive);
    }
    async findUsersByTenantAndRole(tenantId, roleId) {
        const tenantUsers = await this.findByTenant(tenantId);
        return tenantUsers.filter(user => user.roles.includes(roleId));
    }
    // Search and filtering
    async searchUsers(searchTerm) {
        const term = searchTerm.toLowerCase();
        return Array.from(this.users.values()).filter(user => user.firstName.toLowerCase().includes(term) ||
            user.lastName.toLowerCase().includes(term) ||
            user.username.toLowerCase().includes(term) ||
            user.email.getValue().toLowerCase().includes(term));
    }
    async findUsersWithQuery(query) {
        return query.execute();
    }
    async findUsersPaginated(options) {
        const allUsers = await this.findAll();
        const totalItems = allUsers.length;
        const totalPages = Math.ceil(totalItems / options.pageSize);
        const startIndex = (options.page - 1) * options.pageSize;
        const endIndex = startIndex + options.pageSize;
        let sortedUsers = allUsers;
        if (options.sortBy) {
            sortedUsers = allUsers.sort((a, b) => {
                const aValue = a[options.sortBy];
                const bValue = b[options.sortBy];
                if (aValue === bValue)
                    return 0;
                const comparison = aValue < bValue ? -1 : 1;
                return options.sortDirection === 'DESC' ? -comparison : comparison;
            });
        }
        const data = sortedUsers.slice(startIndex, endIndex);
        return {
            data,
            pagination: {
                page: options.page,
                pageSize: options.pageSize,
                totalItems,
                totalPages,
                hasNext: options.page < totalPages,
                hasPrevious: options.page > 1
            }
        };
    }
    // User management operations
    async activateUser(userId) {
        const user = await this.findById(userId);
        if (user) {
            user.activate();
            await this.update(user);
        }
    }
    async deactivateUser(userId) {
        const user = await this.findById(userId);
        if (user) {
            user.deactivate();
            await this.update(user);
        }
    }
    async verifyUserEmail(userId) {
        const user = await this.findById(userId);
        if (user) {
            user.verifyEmail();
            await this.update(user);
        }
    }
    async updateLastLogin(userId) {
        const user = await this.findById(userId);
        if (user) {
            user.recordLogin();
            await this.update(user);
        }
    }
    // Role management
    async addRoleToUser(userId, roleId) {
        const user = await this.findById(userId);
        if (user) {
            user.addRole(roleId);
            await this.update(user);
        }
    }
    async removeRoleFromUser(userId, roleId) {
        const user = await this.findById(userId);
        if (user) {
            user.removeRole(roleId);
            await this.update(user);
        }
    }
    async hasRole(userId, roleId) {
        const user = await this.findById(userId);
        return user ? user.hasRole(roleId) : false;
    }
    // Statistics and analytics
    async getUserCount() {
        return this.users.size;
    }
    async getUserCountByTenant(tenantId) {
        return (await this.findByTenant(tenantId)).length;
    }
    async getUserCountByRole(roleId) {
        return (await this.findByRole(roleId)).length;
    }
    async getActiveUserCount() {
        return (await this.findActiveUsers()).length;
    }
    async getInactiveUserCount() {
        return (await this.findInactiveUsers()).length;
    }
    // Bulk operations
    async bulkActivateUsers(userIds) {
        for (const userId of userIds) {
            await this.activateUser(userId);
        }
    }
    async bulkDeactivateUsers(userIds) {
        for (const userId of userIds) {
            await this.deactivateUser(userId);
        }
    }
    async bulkDeleteUsers(userIds) {
        for (const userId of userIds) {
            await this.delete(userId);
        }
    }
    // Tenant operations
    async transferUsersToTenant(userIds, newTenantId) {
        for (const userId of userIds) {
            const user = await this.findById(userId);
            if (user) {
                user.changeTenant(newTenantId);
                await this.update(user);
            }
        }
    }
    async removeUsersFromTenant(tenantId) {
        const users = await this.findByTenant(tenantId);
        for (const user of users) {
            await this.delete(user.id);
        }
    }
    // Private helper methods
    updateIndexes(user) {
        this.usernameIndex.set(user.username.toLowerCase(), user.id);
        this.emailIndex.set(user.email.getValue().toLowerCase(), user.id);
        // Update tenant index
        if (!this.tenantIndex.has(user.tenantId)) {
            this.tenantIndex.set(user.tenantId, new Set());
        }
        this.tenantIndex.get(user.tenantId).add(user.id);
        // Update role index
        for (const roleId of user.roles) {
            if (!this.roleIndex.has(roleId)) {
                this.roleIndex.set(roleId, new Set());
            }
            this.roleIndex.get(roleId).add(user.id);
        }
    }
    removeFromIndexes(user) {
        this.usernameIndex.delete(user.username.toLowerCase());
        this.emailIndex.delete(user.email.getValue().toLowerCase());
        // Remove from tenant index
        const tenantUsers = this.tenantIndex.get(user.tenantId);
        if (tenantUsers) {
            tenantUsers.delete(user.id);
            if (tenantUsers.size === 0) {
                this.tenantIndex.delete(user.tenantId);
            }
        }
        // Remove from role index
        for (const roleId of user.roles) {
            const roleUsers = this.roleIndex.get(roleId);
            if (roleUsers) {
                roleUsers.delete(user.id);
                if (roleUsers.size === 0) {
                    this.roleIndex.delete(roleId);
                }
            }
        }
    }
}
//# sourceMappingURL=in-memory-user-repository.js.map