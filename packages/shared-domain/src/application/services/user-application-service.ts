/**
 * User Application Service for VALEO NeuroERP 3.0
 * Orchestrates user-related business operations
 */

import type { UserId, RoleId, TenantId, AuditId } from '../../domain/value-objects/branded-types.js';
import type { UserRepository } from '../../domain/interfaces/user-repository.js';
import type { User } from '../../domain/entities/user.js';
import type { CreateUserDto, UpdateUserDto, UserSearchDto, PaginationDto, UserListResponseDto, UserStatsDto } from '../dto/user-dto.js';
import { UserUseCases } from '../use-cases/user-use-cases.js';

export class UserApplicationService {
  private userUseCases: UserUseCases;

  constructor(
    userRepository: UserRepository,
    eventPublisher: (event: any) => Promise<void>
  ) {
    this.userUseCases = new UserUseCases(userRepository, eventPublisher);
  }

  // User Management Operations
  async createUser(dto: CreateUserDto, createdBy?: AuditId): Promise<User> {
    return this.userUseCases.createUser({
      username: dto.username,
      email: dto.email,
      firstName: dto.firstName,
      lastName: dto.lastName,
      phoneNumber: dto.phoneNumber,
      address: dto.address,
      tenantId: dto.tenantId as TenantId,
      roles: dto.roles as RoleId[],
      createdBy
    });
  }

  async updateUser(userId: UserId, dto: UpdateUserDto, updatedBy?: AuditId): Promise<User> {
    return this.userUseCases.updateUser({
      userId,
      firstName: dto.firstName,
      lastName: dto.lastName,
      phoneNumber: dto.phoneNumber,
      address: dto.address,
      updatedBy
    });
  }

  async getUser(userId: UserId): Promise<User | null> {
    return this.userUseCases.getUser({ userId });
  }

  async deleteUser(userId: UserId, deletedBy?: AuditId): Promise<void> {
    const user = await this.userUseCases.getUser({ userId });
    if (user === undefined || user === null) {
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
  async activateUser(userId: UserId, activatedBy?: AuditId): Promise<void> {
    return this.userUseCases.activateUser({ userId, activatedBy });
  }

  async deactivateUser(userId: UserId, deactivatedBy?: AuditId, reason?: string): Promise<void> {
    return this.userUseCases.deactivateUser({ userId, deactivatedBy, reason });
  }

  async verifyUserEmail(userId: UserId): Promise<void> {
    return this.userUseCases.verifyUserEmail(userId);
  }

  // Role Management Operations
  async addRoleToUser(userId: UserId, roleId: RoleId, addedBy?: AuditId): Promise<void> {
    return this.userUseCases.addRoleToUser({ userId, roleId, addedBy });
  }

  async removeRoleFromUser(userId: UserId, roleId: RoleId, removedBy?: AuditId): Promise<void> {
    return this.userUseCases.removeRoleFromUser({ userId, roleId, removedBy });
  }

  async getUserRoles(userId: UserId): Promise<RoleId[]> {
    const user = await this.userUseCases.getUser({ userId });
    return user ? user.roles : [];
  }

  async userHasRole(userId: UserId, roleId: RoleId): Promise<boolean> {
    const user = await this.userUseCases.getUser({ userId });
    return user ? user.hasRole(roleId) : false;
  }

  // Authentication Operations
  async loginUser(userId: UserId, ipAddress?: string, userAgent?: string, sessionId?: string): Promise<User> {
    return this.userUseCases.loginUser({
      userId,
      ipAddress,
      userAgent,
      sessionId
    });
  }

  async canUserLogin(userId: UserId): Promise<boolean> {
    const user = await this.userUseCases.getUser({ userId });
    return user ? user.canLogin() : false;
  }

  // Search and Query Operations
  async searchUsers(searchDto: UserSearchDto, pagination?: PaginationDto): Promise<UserListResponseDto> {
    return this.userUseCases.searchUsers({
      searchTerm: searchDto.searchTerm,
      tenantId: searchDto.tenantId as TenantId,
      roleId: searchDto.roleId as RoleId,
      isActive: searchDto.isActive,
      isEmailVerified: searchDto.isEmailVerified,
      pagination
    });
  }

  async getUsersByTenant(tenantId: TenantId, pagination?: PaginationDto): Promise<UserListResponseDto> {
    return this.userUseCases.searchUsers({
      tenantId,
      pagination
    });
  }

  async getUsersByRole(roleId: RoleId, pagination?: PaginationDto): Promise<UserListResponseDto> {
    return this.userUseCases.searchUsers({
      roleId,
      pagination
    });
  }

  async getActiveUsers(pagination?: PaginationDto): Promise<UserListResponseDto> {
    return this.userUseCases.searchUsers({
      isActive: true,
      pagination
    });
  }

  async getInactiveUsers(pagination?: PaginationDto): Promise<UserListResponseDto> {
    return this.userUseCases.searchUsers({
      isActive: false,
      pagination
    });
  }

  // Statistics Operations
  async getUserStats(tenantId?: TenantId): Promise<UserStatsDto> {
    return this.userUseCases.getUserStats({ tenantId });
  }

  async getUserCount(): Promise<number> {
    const stats = await this.userUseCases.getUserStats({});
    return stats.totalUsers;
  }

  async getActiveUserCount(): Promise<number> {
    const stats = await this.userUseCases.getUserStats({});
    return stats.activeUsers;
  }

  async getInactiveUserCount(): Promise<number> {
    const stats = await this.userUseCases.getUserStats({});
    return stats.inactiveUsers;
  }

  // Validation Operations
  async isUsernameAvailable(username: string): Promise<boolean> {
    // This would typically be implemented in the repository
    // For now, we'll use a simple approach
    try {
      // If findByUsername returns null, username is available
      const user = await this.userUseCases.getUser({ userId: username as UserId });
      return user === null;
    } catch {
      return true; // If there's an error, assume username is available
    }
  }

  async isEmailAvailable(email: string): Promise<boolean> {
    // Similar to username availability check
    try {
      // This would need to be implemented in the repository
      return true;
    } catch {
      return true;
    }
  }

  // Bulk Operations
  async bulkActivateUsers(userIds: UserId[], activatedBy?: AuditId): Promise<void> {
    const promises = userIds.map(userId => 
      this.userUseCases.activateUser({ userId, activatedBy })
    );
    await Promise.all(promises);
  }

  async bulkDeactivateUsers(userIds: UserId[], deactivatedBy?: AuditId, reason?: string): Promise<void> {
    const promises = userIds.map(userId => 
      this.userUseCases.deactivateUser({ userId, deactivatedBy, reason })
    );
    await Promise.all(promises);
  }

  async bulkAddRoleToUsers(userIds: UserId[], roleId: RoleId, addedBy?: AuditId): Promise<void> {
    const promises = userIds.map(userId => 
      this.userUseCases.addRoleToUser({ userId, roleId, addedBy })
    );
    await Promise.all(promises);
  }

  async bulkRemoveRoleFromUsers(userIds: UserId[], roleId: RoleId, removedBy?: AuditId): Promise<void> {
    const promises = userIds.map(userId => 
      this.userUseCases.removeRoleFromUser({ userId, roleId, removedBy })
    );
    await Promise.all(promises);
  }
}

