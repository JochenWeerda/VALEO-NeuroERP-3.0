/**
 * User Application Service for VALEO NeuroERP 3.0
 * Orchestrates user-related business operations
 */
import type { UserId, RoleId, TenantId, AuditId } from '../../domain/value-objects/branded-types.js';
import type { UserRepository } from '../../domain/interfaces/user-repository.js';
import type { User } from '../../domain/entities/user.js';
import type { CreateUserDto, UpdateUserDto, UserSearchDto, PaginationDto, UserListResponseDto, UserStatsDto } from '../dto/user-dto.js';
export declare class UserApplicationService {
    private userUseCases;
    constructor(userRepository: UserRepository, eventPublisher: (event: any) => Promise<void>);
    createUser(dto: CreateUserDto, createdBy?: AuditId): Promise<User>;
    updateUser(userId: UserId, dto: UpdateUserDto, updatedBy?: AuditId): Promise<User>;
    getUser(userId: UserId): Promise<User | null>;
    deleteUser(userId: UserId, deletedBy?: AuditId): Promise<void>;
    activateUser(userId: UserId, activatedBy?: AuditId): Promise<void>;
    deactivateUser(userId: UserId, deactivatedBy?: AuditId, reason?: string): Promise<void>;
    verifyUserEmail(userId: UserId): Promise<void>;
    addRoleToUser(userId: UserId, roleId: RoleId, addedBy?: AuditId): Promise<void>;
    removeRoleFromUser(userId: UserId, roleId: RoleId, removedBy?: AuditId): Promise<void>;
    getUserRoles(userId: UserId): Promise<RoleId[]>;
    userHasRole(userId: UserId, roleId: RoleId): Promise<boolean>;
    loginUser(userId: UserId, ipAddress?: string, userAgent?: string, sessionId?: string): Promise<User>;
    canUserLogin(userId: UserId): Promise<boolean>;
    searchUsers(searchDto: UserSearchDto, pagination?: PaginationDto): Promise<UserListResponseDto>;
    getUsersByTenant(tenantId: TenantId, pagination?: PaginationDto): Promise<UserListResponseDto>;
    getUsersByRole(roleId: RoleId, pagination?: PaginationDto): Promise<UserListResponseDto>;
    getActiveUsers(pagination?: PaginationDto): Promise<UserListResponseDto>;
    getInactiveUsers(pagination?: PaginationDto): Promise<UserListResponseDto>;
    getUserStats(tenantId?: TenantId): Promise<UserStatsDto>;
    getUserCount(): Promise<number>;
    getActiveUserCount(): Promise<number>;
    getInactiveUserCount(): Promise<number>;
    isUsernameAvailable(username: string): Promise<boolean>;
    isEmailAvailable(email: string): Promise<boolean>;
    bulkActivateUsers(userIds: UserId[], activatedBy?: AuditId): Promise<void>;
    bulkDeactivateUsers(userIds: UserId[], deactivatedBy?: AuditId, reason?: string): Promise<void>;
    bulkAddRoleToUsers(userIds: UserId[], roleId: RoleId, addedBy?: AuditId): Promise<void>;
    bulkRemoveRoleFromUsers(userIds: UserId[], roleId: RoleId, removedBy?: AuditId): Promise<void>;
}
//# sourceMappingURL=user-application-service.d.ts.map