/**
 * User Repository Interface for VALEO NeuroERP 3.0
 * Specific repository contract for User entity
 */
import type { UserId, RoleId, TenantId } from '../value-objects/branded-types.js';
import type { Repository, QueryBuilder, PaginatedResult, PaginationOptions } from './repository.js';
import type { User } from '../entities/user.js';
export interface UserRepository extends Repository<User> {
    findByUsername(username: string): Promise<User | null>;
    findByEmail(email: string): Promise<User | null>;
    findByTenant(tenantId: TenantId): Promise<User[]>;
    findByRole(roleId: RoleId): Promise<User[]>;
    findActiveUsers(): Promise<User[]>;
    findInactiveUsers(): Promise<User[]>;
    findUsersByTenantAndRole(tenantId: TenantId, roleId: RoleId): Promise<User[]>;
    searchUsers(searchTerm: string): Promise<User[]>;
    findUsersWithQuery(query: QueryBuilder<User>): Promise<User[]>;
    findUsersPaginated(options: PaginationOptions): Promise<PaginatedResult<User>>;
    activateUser(userId: UserId): Promise<void>;
    deactivateUser(userId: UserId): Promise<void>;
    verifyUserEmail(userId: UserId): Promise<void>;
    updateLastLogin(userId: UserId): Promise<void>;
    addRoleToUser(userId: UserId, roleId: RoleId): Promise<void>;
    removeRoleFromUser(userId: UserId, roleId: RoleId): Promise<void>;
    hasRole(userId: UserId, roleId: RoleId): Promise<boolean>;
    getUserCount(): Promise<number>;
    getUserCountByTenant(tenantId: TenantId): Promise<number>;
    getUserCountByRole(roleId: RoleId): Promise<number>;
    getActiveUserCount(): Promise<number>;
    getInactiveUserCount(): Promise<number>;
    bulkActivateUsers(userIds: UserId[]): Promise<void>;
    bulkDeactivateUsers(userIds: UserId[]): Promise<void>;
    bulkDeleteUsers(userIds: UserId[]): Promise<void>;
    transferUsersToTenant(userIds: UserId[], newTenantId: TenantId): Promise<void>;
    removeUsersFromTenant(tenantId: TenantId): Promise<void>;
}
//# sourceMappingURL=user-repository.d.ts.map