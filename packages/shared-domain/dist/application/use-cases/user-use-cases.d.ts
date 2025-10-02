/**
 * User Use Cases for VALEO NeuroERP 3.0
 * Application-specific business logic
 */
import type { UserId, RoleId, TenantId, AuditId } from '../../domain/value-objects/branded-types.js';
import type { UserRepository } from '../../domain/interfaces/user-repository.js';
import { User } from '../../domain/entities/user.js';
import type { PaginationDto, UserListResponseDto, UserStatsDto } from '../dto/user-dto.js';
export interface CreateUserCommand {
    username: string;
    email: string;
    firstName: string;
    lastName: string;
    phoneNumber?: string;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string;
    };
    tenantId: TenantId;
    roles?: RoleId[];
    createdBy?: AuditId;
}
export interface UpdateUserCommand {
    userId: UserId;
    firstName?: string;
    lastName?: string;
    phoneNumber?: string;
    address?: {
        street: string;
        city: string;
        postalCode: string;
        country: string;
        state?: string;
    };
    updatedBy?: AuditId;
}
export interface ActivateUserCommand {
    userId: UserId;
    activatedBy?: AuditId;
}
export interface DeactivateUserCommand {
    userId: UserId;
    deactivatedBy?: AuditId;
    reason?: string;
}
export interface AddRoleToUserCommand {
    userId: UserId;
    roleId: RoleId;
    addedBy?: AuditId;
}
export interface RemoveRoleFromUserCommand {
    userId: UserId;
    roleId: RoleId;
    removedBy?: AuditId;
}
export interface LoginUserCommand {
    userId: UserId;
    ipAddress?: string;
    userAgent?: string;
    sessionId?: string;
}
export interface GetUserQuery {
    userId: UserId;
}
export interface SearchUsersQuery {
    searchTerm?: string;
    tenantId?: TenantId;
    roleId?: RoleId;
    isActive?: boolean;
    isEmailVerified?: boolean;
    pagination?: PaginationDto;
}
export interface GetUserStatsQuery {
    tenantId?: TenantId;
}
export declare class UserUseCases {
    private userRepository;
    private eventPublisher;
    constructor(userRepository: UserRepository, eventPublisher: (event: any) => Promise<void>);
    createUser(command: CreateUserCommand): Promise<User>;
    updateUser(command: UpdateUserCommand): Promise<User>;
    activateUser(command: ActivateUserCommand): Promise<void>;
    deactivateUser(command: DeactivateUserCommand): Promise<void>;
    addRoleToUser(command: AddRoleToUserCommand): Promise<void>;
    removeRoleFromUser(command: RemoveRoleFromUserCommand): Promise<void>;
    loginUser(command: LoginUserCommand): Promise<User>;
    verifyUserEmail(userId: UserId): Promise<void>;
    getUser(query: GetUserQuery): Promise<User | null>;
    searchUsers(query: SearchUsersQuery): Promise<UserListResponseDto>;
    getUserStats(query: GetUserStatsQuery): Promise<UserStatsDto>;
    private generateUserId;
    private toUserDto;
}
//# sourceMappingURL=user-use-cases.d.ts.map