/**
 * Tests for User Use Cases
 */

import { UserUseCases } from '../application/use-cases/user-use-cases.js';
import { InMemoryUserRepository } from '../infrastructure/repositories/in-memory-user-repository.js';
import { createUserId, createRoleId, createTenantId, createAuditId } from '../domain/value-objects/branded-types.js';

describe('UserUseCases', () => {
  let userUseCases: UserUseCases;
  let userRepository: InMemoryUserRepository;
  let eventPublisher: jest.Mock;

  beforeEach(() => {
    userRepository = new InMemoryUserRepository();
    eventPublisher = jest.fn().mockResolvedValue(undefined);
    userUseCases = new UserUseCases(userRepository, eventPublisher);
  });

  describe('Create User', () => {
    it('should create a new user', async () => {
      const command = {
        username: 'john.doe',
        email: 'john@example.com',
        firstName: 'John',
        lastName: 'Doe',
        tenantId: createTenantId('tenant-456'),
        roles: [createRoleId('role-789')],
        createdBy: createAuditId('audit-101')
      };

      const user = await userUseCases.createUser(command);

      expect(user).toBeDefined();
      expect(user.username).toBe('john.doe');
      expect(user.firstName).toBe('John');
      expect(user.lastName).toBe('Doe');
      expect(user.tenantId).toBe(command.tenantId);
      expect(user.roles).toContain(command.roles[0]);

      // Verify event was published
      expect(eventPublisher).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'UserCreated'
        })
      );
    });

    it('should throw error for duplicate username', async () => {
      const command = {
        username: 'john.doe',
        email: 'john@example.com',
        firstName: 'John',
        lastName: 'Doe',
        tenantId: createTenantId('tenant-456')
      };

      await userUseCases.createUser(command);

      // Try to create another user with same username
      const duplicateCommand = {
        ...command,
        email: 'jane@example.com'
      };

      await expect(userUseCases.createUser(duplicateCommand)).rejects.toThrow(
        "Username 'john.doe' is already taken"
      );
    });

    it('should throw error for duplicate email', async () => {
      const command = {
        username: 'john.doe',
        email: 'john@example.com',
        firstName: 'John',
        lastName: 'Doe',
        tenantId: createTenantId('tenant-456')
      };

      await userUseCases.createUser(command);

      // Try to create another user with same email
      const duplicateCommand = {
        ...command,
        username: 'jane.doe'
      };

      await expect(userUseCases.createUser(duplicateCommand)).rejects.toThrow(
        "Email 'john@example.com' is already registered"
      );
    });
  });

  describe('Update User', () => {
    let existingUser: any;

    beforeEach(async () => {
      const createCommand = {
        username: 'john.doe',
        email: 'john@example.com',
        firstName: 'John',
        lastName: 'Doe',
        tenantId: createTenantId('tenant-456')
      };
      existingUser = await userUseCases.createUser(createCommand);
    });

    it('should update user profile', async () => {
      const updateCommand = {
        userId: existingUser.id,
        firstName: 'Jane',
        lastName: 'Smith',
        updatedBy: createAuditId('audit-102')
      };

      const updatedUser = await userUseCases.updateUser(updateCommand);

      expect(updatedUser.firstName).toBe('Jane');
      expect(updatedUser.lastName).toBe('Smith');

      // Verify event was published
      expect(eventPublisher).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'UserUpdated'
        })
      );
    });

    it('should throw error for non-existent user', async () => {
      const updateCommand = {
        userId: createUserId('non-existent'),
        firstName: 'Jane'
      };

      await expect(userUseCases.updateUser(updateCommand)).rejects.toThrow(
        "User with ID 'non-existent' not found"
      );
    });
  });

  describe('User Status Management', () => {
    let existingUser: any;

    beforeEach(async () => {
      const createCommand = {
        username: 'john.doe',
        email: 'john@example.com',
        firstName: 'John',
        lastName: 'Doe',
        tenantId: createTenantId('tenant-456')
      };
      existingUser = await userUseCases.createUser(createCommand);
    });

    it('should activate user', async () => {
      await userUseCases.activateUser({
        userId: existingUser.id,
        activatedBy: createAuditId('audit-103')
      });

      const user = await userUseCases.getUser({ userId: existingUser.id });
      expect(user?.isActive).toBe(true);

      // Verify event was published
      expect(eventPublisher).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'UserActivated'
        })
      );
    });

    it('should deactivate user', async () => {
      await userUseCases.deactivateUser({
        userId: existingUser.id,
        deactivatedBy: createAuditId('audit-104'),
        reason: 'Test deactivation'
      });

      const user = await userUseCases.getUser({ userId: existingUser.id });
      expect(user?.isActive).toBe(false);

      // Verify event was published
      expect(eventPublisher).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'UserDeactivated'
        })
      );
    });

    it('should verify user email', async () => {
      await userUseCases.verifyUserEmail(existingUser.id);

      const user = await userUseCases.getUser({ userId: existingUser.id });
      expect(user?.isEmailVerified).toBe(true);

      // Verify event was published
      expect(eventPublisher).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'UserEmailVerified'
        })
      );
    });
  });

  describe('Role Management', () => {
    let existingUser: any;

    beforeEach(async () => {
      const createCommand = {
        username: 'john.doe',
        email: 'john@example.com',
        firstName: 'John',
        lastName: 'Doe',
        tenantId: createTenantId('tenant-456'),
        roles: [createRoleId('role-789')]
      };
      existingUser = await userUseCases.createUser(createCommand);
    });

    it('should add role to user', async () => {
      const newRoleId = createRoleId('role-999');
      await userUseCases.addRoleToUser({
        userId: existingUser.id,
        roleId: newRoleId,
        addedBy: createAuditId('audit-105')
      });

      const user = await userUseCases.getUser({ userId: existingUser.id });
      expect(user?.hasRole(newRoleId)).toBe(true);

      // Verify event was published
      expect(eventPublisher).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'UserRoleAdded'
        })
      );
    });

    it('should remove role from user', async () => {
      const roleId = createRoleId('role-789');
      await userUseCases.removeRoleFromUser({
        userId: existingUser.id,
        roleId: roleId,
        removedBy: createAuditId('audit-106')
      });

      const user = await userUseCases.getUser({ userId: existingUser.id });
      expect(user?.hasRole(roleId)).toBe(false);

      // Verify event was published
      expect(eventPublisher).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'UserRoleRemoved'
        })
      );
    });
  });

  describe('Login Management', () => {
    let existingUser: any;

    beforeEach(async () => {
      const createCommand = {
        username: 'john.doe',
        email: 'john@example.com',
        firstName: 'John',
        lastName: 'Doe',
        tenantId: createTenantId('tenant-456')
      };
      existingUser = await userUseCases.createUser(createCommand);
    });

    it('should login user', async () => {
      const loginCommand = {
        userId: existingUser.id,
        ipAddress: '192.168.1.1',
        userAgent: 'Mozilla/5.0',
        sessionId: 'session-123'
      };

      const loggedInUser = await userUseCases.loginUser(loginCommand);

      expect(loggedInUser.lastLoginAt).toBeDefined();
      expect(loggedInUser.lastLoginAt).toBeInstanceOf(Date);

      // Verify event was published
      expect(eventPublisher).toHaveBeenCalledWith(
        expect.objectContaining({
          eventType: 'UserLoggedIn'
        })
      );
    });

    it('should throw error for inactive user login', async () => {
      await userUseCases.deactivateUser({
        userId: existingUser.id,
        deactivatedBy: createAuditId('audit-107')
      });

      const loginCommand = {
        userId: existingUser.id,
        ipAddress: '192.168.1.1'
      };

      await expect(userUseCases.loginUser(loginCommand)).rejects.toThrow(
        'User cannot login (inactive or email not verified)'
      );
    });
  });

  describe('Search and Queries', () => {
    beforeEach(async () => {
      // Create multiple users for search testing
      const users = [
        {
          username: 'john.doe',
          email: 'john@example.com',
          firstName: 'John',
          lastName: 'Doe',
          tenantId: createTenantId('tenant-456'),
          roles: [createRoleId('role-789')]
        },
        {
          username: 'jane.smith',
          email: 'jane@example.com',
          firstName: 'Jane',
          lastName: 'Smith',
          tenantId: createTenantId('tenant-456'),
          roles: [createRoleId('role-789')]
        },
        {
          username: 'bob.wilson',
          email: 'bob@example.com',
          firstName: 'Bob',
          lastName: 'Wilson',
          tenantId: createTenantId('tenant-999'),
          roles: [createRoleId('role-888')]
        }
      ];

      for (const userData of users) {
        await userUseCases.createUser(userData);
      }
    });

    it('should search users by search term', async () => {
      const result = await userUseCases.searchUsers({
        searchTerm: 'john',
        pagination: { page: 1, pageSize: 10, sortDirection: 'ASC' }
      });

      expect(result.users).toHaveLength(1);
      expect(result.users[0].firstName).toBe('John');
    });

    it('should search users by tenant', async () => {
      const result = await userUseCases.searchUsers({
        tenantId: createTenantId('tenant-456'),
        pagination: { page: 1, pageSize: 10, sortDirection: 'ASC' }
      });

      expect(result.users).toHaveLength(2);
      expect(result.users.every(user => user.tenantId === 'tenant-456')).toBe(true);
    });

    it('should search users by role', async () => {
      const result = await userUseCases.searchUsers({
        roleId: createRoleId('role-789'),
        pagination: { page: 1, pageSize: 10, sortDirection: 'ASC' }
      });

      expect(result.users).toHaveLength(2);
    });

    it('should get user statistics', async () => {
      const stats = await userUseCases.getUserStats({});

      expect(stats.totalUsers).toBe(3);
      expect(stats.activeUsers).toBe(3);
      expect(stats.inactiveUsers).toBe(0);
    });
  });
});

