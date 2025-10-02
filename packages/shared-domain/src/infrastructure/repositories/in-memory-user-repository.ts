/**
 * In-Memory User Repository Implementation for VALEO NeuroERP 3.0
 * Development and testing repository implementation
 */

import type { UserId, RoleId, TenantId } from '../../domain/value-objects/branded-types.js';
import type { UserRepository } from '../../domain/interfaces/user-repository.js';
import type { User } from '../../domain/entities/user.js';
import type { QueryBuilder, PaginatedResult, PaginationOptions } from '../../domain/interfaces/repository.js';
import { BaseRepository } from './base-repository.js';

export class InMemoryUserRepository extends BaseRepository<User> implements UserRepository {
  private users: Map<string, User> = new Map();
  private usernameIndex: Map<string, UserId> = new Map();
  private emailIndex: Map<string, UserId> = new Map();
  private tenantIndex: Map<string, Set<UserId>> = new Map();
  private roleIndex: Map<string, Set<UserId>> = new Map();

  async findById(id: any): Promise<User | null> {
    return this.users.get(id) || null;
  }

  async findAll(): Promise<User[]> {
    return Array.from(this.users.values());
  }

  async save(user: User): Promise<User> {
    this.users.set(user.id, user);
    this.updateIndexes(user);
    return user;
  }

  async update(user: User): Promise<User> {
    this.users.set(user.id, user);
    this.updateIndexes(user);
    return user;
  }

  async delete(id: any): Promise<void> {
    const user = this.users.get(id);
    if (user) {
      this.removeFromIndexes(user);
      this.users.delete(id);
    }
  }

  // User-specific query methods
  async findByUsername(username: string): Promise<User | null> {
    const userId = this.usernameIndex.get(username.toLowerCase());
    return userId ? this.users.get(userId) || null : null;
  }

  async findByEmail(email: string): Promise<User | null> {
    const userId = this.emailIndex.get(email.toLowerCase());
    return userId ? this.users.get(userId) || null : null;
  }

  async findByTenant(tenantId: TenantId): Promise<User[]> {
    const userIds = this.tenantIndex.get(tenantId) || new Set();
    return Array.from(userIds).map(id => this.users.get(id)).filter(Boolean) as User[];
  }

  async findByRole(roleId: RoleId): Promise<User[]> {
    const userIds = this.roleIndex.get(roleId) || new Set();
    return Array.from(userIds).map(id => this.users.get(id)).filter(Boolean) as User[];
  }

  async findActiveUsers(): Promise<User[]> {
    return Array.from(this.users.values()).filter(user => user.isActive);
  }

  async findInactiveUsers(): Promise<User[]> {
    return Array.from(this.users.values()).filter(user => !user.isActive);
  }

  async findUsersByTenantAndRole(tenantId: TenantId, roleId: RoleId): Promise<User[]> {
    const tenantUsers = await this.findByTenant(tenantId);
    return tenantUsers.filter(user => user.roles.includes(roleId));
  }

  // Search and filtering
  async searchUsers(searchTerm: string): Promise<User[]> {
    const term = searchTerm.toLowerCase();
    return Array.from(this.users.values()).filter(user => 
      user.firstName.toLowerCase().includes(term) ||
      user.lastName.toLowerCase().includes(term) ||
      user.username.toLowerCase().includes(term) ||
      user.email.getValue().toLowerCase().includes(term)
    );
  }

  async findUsersWithQuery(query: QueryBuilder<User>): Promise<User[]> {
    return query.execute();
  }

  async findUsersPaginated(options: PaginationOptions): Promise<PaginatedResult<User>> {
    const allUsers = await this.findAll();
    const totalItems = allUsers.length;
    const totalPages = Math.ceil(totalItems / options.pageSize);
    const startIndex = (options.page - 1) * options.pageSize;
    const endIndex = startIndex + options.pageSize;

    let sortedUsers = allUsers;
    if (options.sortBy) {
      sortedUsers = allUsers.sort((a, b) => {
        const aValue = (a as any)[options.sortBy!];
        const bValue = (b as any)[options.sortBy!];
        
        if (aValue === bValue) return 0;
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
  async activateUser(userId: UserId): Promise<void> {
    const user = await this.findById(userId);
    if (user) {
      user.activate();
      await this.update(user);
    }
  }

  async deactivateUser(userId: UserId): Promise<void> {
    const user = await this.findById(userId);
    if (user) {
      user.deactivate();
      await this.update(user);
    }
  }

  async verifyUserEmail(userId: UserId): Promise<void> {
    const user = await this.findById(userId);
    if (user) {
      user.verifyEmail();
      await this.update(user);
    }
  }

  async updateLastLogin(userId: UserId): Promise<void> {
    const user = await this.findById(userId);
    if (user) {
      user.recordLogin();
      await this.update(user);
    }
  }

  // Role management
  async addRoleToUser(userId: UserId, roleId: RoleId): Promise<void> {
    const user = await this.findById(userId);
    if (user) {
      user.addRole(roleId);
      await this.update(user);
    }
  }

  async removeRoleFromUser(userId: UserId, roleId: RoleId): Promise<void> {
    const user = await this.findById(userId);
    if (user) {
      user.removeRole(roleId);
      await this.update(user);
    }
  }

  async hasRole(userId: UserId, roleId: RoleId): Promise<boolean> {
    const user = await this.findById(userId);
    return user ? user.hasRole(roleId) : false;
  }

  // Statistics and analytics
  async getUserCount(): Promise<number> {
    return this.users.size;
  }

  async getUserCountByTenant(tenantId: TenantId): Promise<number> {
    return (await this.findByTenant(tenantId)).length;
  }

  async getUserCountByRole(roleId: RoleId): Promise<number> {
    return (await this.findByRole(roleId)).length;
  }

  async getActiveUserCount(): Promise<number> {
    return (await this.findActiveUsers()).length;
  }

  async getInactiveUserCount(): Promise<number> {
    return (await this.findInactiveUsers()).length;
  }

  // Bulk operations
  async bulkActivateUsers(userIds: UserId[]): Promise<void> {
    for (const userId of userIds) {
      await this.activateUser(userId);
    }
  }

  async bulkDeactivateUsers(userIds: UserId[]): Promise<void> {
    for (const userId of userIds) {
      await this.deactivateUser(userId);
    }
  }

  async bulkDeleteUsers(userIds: UserId[]): Promise<void> {
    for (const userId of userIds) {
      await this.delete(userId);
    }
  }

  // Tenant operations
  async transferUsersToTenant(userIds: UserId[], newTenantId: TenantId): Promise<void> {
    for (const userId of userIds) {
      const user = await this.findById(userId);
      if (user) {
        user.changeTenant(newTenantId);
        await this.update(user);
      }
    }
  }

  async removeUsersFromTenant(tenantId: TenantId): Promise<void> {
    const users = await this.findByTenant(tenantId);
    for (const user of users) {
      await this.delete(user.id as any);
    }
  }

  // Private helper methods
  private updateIndexes(user: User): void {
    this.usernameIndex.set(user.username.toLowerCase(), user.id as any);
    this.emailIndex.set(user.email.getValue().toLowerCase(), user.id as any);
    
    // Update tenant index
    if (!this.tenantIndex.has(user.tenantId)) {
      this.tenantIndex.set(user.tenantId, new Set());
    }
    this.tenantIndex.get(user.tenantId)!.add(user.id as any);
    
    // Update role index
    for (const roleId of user.roles) {
      if (!this.roleIndex.has(roleId)) {
        this.roleIndex.set(roleId, new Set());
      }
      this.roleIndex.get(roleId)!.add(user.id as any);
    }
  }

  private removeFromIndexes(user: User): void {
    this.usernameIndex.delete(user.username.toLowerCase());
    this.emailIndex.delete(user.email.getValue().toLowerCase());
    
    // Remove from tenant index
    const tenantUsers = this.tenantIndex.get(user.tenantId);
    if (tenantUsers) {
      tenantUsers.delete(user.id as any);
      if (tenantUsers.size === 0) {
        this.tenantIndex.delete(user.tenantId);
      }
    }
    
    // Remove from role index
    for (const roleId of user.roles) {
      const roleUsers = this.roleIndex.get(roleId);
      if (roleUsers) {
        roleUsers.delete(user.id as any);
        if (roleUsers.size === 0) {
          this.roleIndex.delete(roleId);
        }
      }
    }
  }
}
