/**
 * User Use Cases for VALEO NeuroERP 3.0
 * Application-specific business logic
 */
import { User } from '../../domain/entities/user.js';
import { Email, PhoneNumber, Address } from '../../domain/value-objects/common-value-objects.js';
import { UserCreatedEvent, UserUpdatedEvent, UserActivatedEvent, UserDeactivatedEvent, UserRoleAddedEvent, UserRoleRemovedEvent, UserLoggedInEvent, UserEmailVerifiedEvent } from '../../domain/events/user-events.js';
// Use Cases
export class UserUseCases {
    userRepository;
    eventPublisher;
    constructor(userRepository, eventPublisher) {
        this.userRepository = userRepository;
        this.eventPublisher = eventPublisher;
    }
    // Commands
    async createUser(command) {
        // Validate unique username and email
        const existingUserByUsername = await this.userRepository.findByUsername(command.username);
        if (existingUserByUsername) {
            throw new Error(`Username '${command.username}' is already taken`);
        }
        const existingUserByEmail = await this.userRepository.findByEmail(command.email);
        if (existingUserByEmail) {
            throw new Error(`Email '${command.email}' is already registered`);
        }
        // Create user entity
        const user = new User({
            id: this.generateUserId(),
            username: command.username,
            email: new Email(command.email),
            firstName: command.firstName,
            lastName: command.lastName,
            phoneNumber: command.phoneNumber ? new PhoneNumber(command.phoneNumber) : undefined,
            address: command.address ? new Address(command.address.street, command.address.city, command.address.postalCode, command.address.country, command.address.state) : undefined,
            isActive: true,
            isEmailVerified: false,
            roles: command.roles || [],
            tenantId: command.tenantId,
            createdBy: command.createdBy
        });
        // Save user
        const savedUser = await this.userRepository.save(user);
        // Publish domain event
        await this.eventPublisher(new UserCreatedEvent(savedUser.id, {
            username: savedUser.username,
            email: savedUser.email.getValue(),
            firstName: savedUser.firstName,
            lastName: savedUser.lastName,
            tenantId: savedUser.tenantId,
            createdBy: command.createdBy
        }));
        return savedUser;
    }
    async updateUser(command) {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new Error(`User with ID '${command.userId}' not found`);
        }
        // Update user profile
        user.updateProfile(command.firstName || user.firstName, command.lastName || user.lastName, command.phoneNumber ? new PhoneNumber(command.phoneNumber) : user.phoneNumber, command.address ? new Address(command.address.street, command.address.city, command.address.postalCode, command.address.country, command.address.state) : user.address, command.updatedBy);
        // Save updated user
        const updatedUser = await this.userRepository.update(user);
        // Publish domain event
        await this.eventPublisher(new UserUpdatedEvent(updatedUser.id, {
            firstName: command.firstName,
            lastName: command.lastName,
            phoneNumber: command.phoneNumber,
            address: command.address ? JSON.stringify(command.address) : undefined,
            updatedBy: command.updatedBy
        }));
        return updatedUser;
    }
    async activateUser(command) {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new Error(`User with ID '${command.userId}' not found`);
        }
        user.activate(command.activatedBy);
        await this.userRepository.update(user);
        // Publish domain event
        await this.eventPublisher(new UserActivatedEvent(user.id, {
            activatedAt: new Date(),
            activatedBy: command.activatedBy
        }));
    }
    async deactivateUser(command) {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new Error(`User with ID '${command.userId}' not found`);
        }
        user.deactivate(command.deactivatedBy);
        await this.userRepository.update(user);
        // Publish domain event
        await this.eventPublisher(new UserDeactivatedEvent(user.id, {
            deactivatedAt: new Date(),
            deactivatedBy: command.deactivatedBy,
            reason: command.reason
        }));
    }
    async addRoleToUser(command) {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new Error(`User with ID '${command.userId}' not found`);
        }
        user.addRole(command.roleId, command.addedBy);
        await this.userRepository.update(user);
        // Publish domain event
        await this.eventPublisher(new UserRoleAddedEvent(user.id, {
            roleId: command.roleId,
            addedAt: new Date(),
            addedBy: command.addedBy
        }));
    }
    async removeRoleFromUser(command) {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new Error(`User with ID '${command.userId}' not found`);
        }
        user.removeRole(command.roleId, command.removedBy);
        await this.userRepository.update(user);
        // Publish domain event
        await this.eventPublisher(new UserRoleRemovedEvent(user.id, {
            roleId: command.roleId,
            removedAt: new Date(),
            removedBy: command.removedBy
        }));
    }
    async loginUser(command) {
        const user = await this.userRepository.findById(command.userId);
        if (!user) {
            throw new Error(`User with ID '${command.userId}' not found`);
        }
        if (!user.canLogin()) {
            throw new Error('User cannot login (inactive or email not verified)');
        }
        user.recordLogin();
        const updatedUser = await this.userRepository.update(user);
        // Publish domain event
        await this.eventPublisher(new UserLoggedInEvent(user.id, {
            loginAt: new Date(),
            ipAddress: command.ipAddress,
            userAgent: command.userAgent,
            sessionId: command.sessionId
        }));
        return updatedUser;
    }
    async verifyUserEmail(userId) {
        const user = await this.userRepository.findById(userId);
        if (!user) {
            throw new Error(`User with ID '${userId}' not found`);
        }
        user.verifyEmail();
        await this.userRepository.update(user);
        // Publish domain event
        await this.eventPublisher(new UserEmailVerifiedEvent(user.id, {
            verifiedAt: new Date()
        }));
    }
    // Queries
    async getUser(query) {
        return this.userRepository.findById(query.userId);
    }
    async searchUsers(query) {
        const pagination = query.pagination || { page: 1, pageSize: 20, sortDirection: 'ASC' };
        if (query.searchTerm) {
            const users = await this.userRepository.searchUsers(query.searchTerm);
            return {
                users: users.map(user => this.toUserDto(user)),
                pagination: {
                    page: pagination.page,
                    pageSize: pagination.pageSize,
                    totalItems: users.length,
                    totalPages: Math.ceil(users.length / pagination.pageSize),
                    hasNext: pagination.page * pagination.pageSize < users.length,
                    hasPrevious: pagination.page > 1
                }
            };
        }
        if (query.tenantId && query.roleId) {
            const users = await this.userRepository.findUsersByTenantAndRole(query.tenantId, query.roleId);
            return {
                users: users.map(user => this.toUserDto(user)),
                pagination: {
                    page: pagination.page,
                    pageSize: pagination.pageSize,
                    totalItems: users.length,
                    totalPages: Math.ceil(users.length / pagination.pageSize),
                    hasNext: pagination.page * pagination.pageSize < users.length,
                    hasPrevious: pagination.page > 1
                }
            };
        }
        if (query.tenantId) {
            const users = await this.userRepository.findByTenant(query.tenantId);
            return {
                users: users.map(user => this.toUserDto(user)),
                pagination: {
                    page: pagination.page,
                    pageSize: pagination.pageSize,
                    totalItems: users.length,
                    totalPages: Math.ceil(users.length / pagination.pageSize),
                    hasNext: pagination.page * pagination.pageSize < users.length,
                    hasPrevious: pagination.page > 1
                }
            };
        }
        if (query.roleId) {
            const users = await this.userRepository.findByRole(query.roleId);
            return {
                users: users.map(user => this.toUserDto(user)),
                pagination: {
                    page: pagination.page,
                    pageSize: pagination.pageSize,
                    totalItems: users.length,
                    totalPages: Math.ceil(users.length / pagination.pageSize),
                    hasNext: pagination.page * pagination.pageSize < users.length,
                    hasPrevious: pagination.page > 1
                }
            };
        }
        // Default: return all users with pagination
        const result = await this.userRepository.findUsersPaginated(pagination);
        return {
            users: result.data.map(user => this.toUserDto(user)),
            pagination: result.pagination
        };
    }
    async getUserStats(query) {
        const totalUsers = await this.userRepository.getUserCount();
        const activeUsers = await this.userRepository.getActiveUserCount();
        const inactiveUsers = await this.userRepository.getInactiveUserCount();
        // For simplicity, returning empty objects for tenant and role breakdowns
        // In a real implementation, these would be populated from the database
        return {
            totalUsers,
            activeUsers,
            inactiveUsers,
            usersByTenant: {},
            usersByRole: {}
        };
    }
    // Helper methods
    generateUserId() {
        return `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    toUserDto(user) {
        return {
            id: user.id,
            username: user.username,
            email: user.email.getValue(),
            firstName: user.firstName,
            lastName: user.lastName,
            phoneNumber: user.phoneNumber?.getValue(),
            address: user.address ? {
                street: user.address.street,
                city: user.address.city,
                postalCode: user.address.postalCode,
                country: user.address.country,
                state: user.address.state
            } : undefined,
            isActive: user.isActive,
            isEmailVerified: user.isEmailVerified,
            roles: user.roles,
            tenantId: user.tenantId,
            lastLoginAt: user.lastLoginAt?.toISOString(),
            createdAt: user.createdAt.toISOString(),
            updatedAt: user.updatedAt.toISOString(),
            version: user.version
        };
    }
}
//# sourceMappingURL=user-use-cases.js.map