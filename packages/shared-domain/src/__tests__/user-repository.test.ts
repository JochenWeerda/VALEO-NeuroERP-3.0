/**
 * Tests for User Repository
 */

import { InMemoryUserRepository } from '../infrastructure/repositories/in-memory-user-repository.js';
import { User } from '../domain/entities/user.js';
import { Email, PhoneNumber, Address } from '../domain/value-objects/common-value-objects.js';
import { createUserId, createRoleId, createTenantId, createAuditId } from '../domain/value-objects/branded-types.js';

describe('InMemoryUserRepository', () => {
  let repository: InMemoryUserRepository;
  let user: User;

  beforeEach(() => {
    repository = new InMemoryUserRepository();
    user = new User({
      id: createUserId('user-123'),
      username: 'john.doe',
      email: new Email('john@example.com'),
      firstName: 'John',
      lastName: 'Doe',
      phoneNumber: new PhoneNumber('+1234567890'),
      address: new Address('123 Main St', 'City', '12345', 'Country'),
      isActive: true,
      isEmailVerified: true,
      roles: [createRoleId('role-789')],
      tenantId: createTenantId('tenant-456'),
      createdBy: createAuditId('audit-101')
    });
  });

  describe('Basic CRUD Operations', () => {
    it('should save and find user by id', async () => {
      await repository.save(user);
      const foundUser = await repository.findById(user.id as any);
      
      expect(foundUser).not.toBeNull();
      expect(foundUser?.id).toBe(user.id);
      expect(foundUser?.username).toBe('john.doe');
    });

    it('should return null for non-existent user', async () => {
      const foundUser = await repository.findById(createUserId('non-existent'));
      expect(foundUser).toBeNull();
    });

    it('should update user', async () => {
      await repository.save(user);
      
      user.updateProfile('Jane', 'Smith', undefined, undefined);
      const updatedUser = await repository.update(user);
      
      expect(updatedUser.firstName).toBe('Jane');
      expect(updatedUser.lastName).toBe('Smith');
    });

    it('should delete user', async () => {
      await repository.save(user);
      expect(await repository.exists(user.id)).toBe(true);
      
      await repository.delete(user.id);
      expect(await repository.exists(user.id)).toBe(false);
    });

    it('should find all users', async () => {
      await repository.save(user);
      const users = await repository.findAll();
      
      expect(users).toHaveLength(1);
      expect(users[0].id).toBe(user.id);
    });
  });

  describe('User-Specific Queries', () => {
    beforeEach(async () => {
      await repository.save(user);
    });

    it('should find user by username', async () => {
      const foundUser = await repository.findByUsername('john.doe');
      
      expect(foundUser).not.toBeNull();
      expect(foundUser?.id).toBe(user.id);
    });

    it('should find user by email', async () => {
      const foundUser = await repository.findByEmail('john@example.com');
      
      expect(foundUser).not.toBeNull();
      expect(foundUser?.id).toBe(user.id);
    });

    it('should find users by tenant', async () => {
      const users = await repository.findByTenant(user.tenantId);
      
      expect(users).toHaveLength(1);
      expect(users[0].id).toBe(user.id);
    });

    it('should find users by role', async () => {
      const users = await repository.findByRole(createRoleId('role-789'));
      
      expect(users).toHaveLength(1);
      expect(users[0].id).toBe(user.id);
    });

    it('should find active users', async () => {
      const activeUsers = await repository.findActiveUsers();
      
      expect(activeUsers).toHaveLength(1);
      expect(activeUsers[0].id).toBe(user.id);
    });

    it('should find inactive users', async () => {
      const inactiveUsers = await repository.findInactiveUsers();
      
      expect(inactiveUsers).toHaveLength(0);
    });

    it('should search users', async () => {
      const users = await repository.searchUsers('john');
      
      expect(users).toHaveLength(1);
      expect(users[0].id).toBe(user.id);
    });
  });

  describe('User Management Operations', () => {
    beforeEach(async () => {
      await repository.save(user);
    });

    it('should activate user', async () => {
      user.deactivate();
      await repository.update(user);
      
      await repository.activateUser(user.id as any);
      const activatedUser = await repository.findById(user.id as any);
      
      expect(activatedUser?.isActive).toBe(true);
    });

    it('should deactivate user', async () => {
      await repository.deactivateUser(user.id as any);
      const deactivatedUser = await repository.findById(user.id as any);
      
      expect(deactivatedUser?.isActive).toBe(false);
    });

    it('should verify user email', async () => {
      user.verifyEmail();
      await repository.update(user);
      
      await repository.verifyUserEmail(user.id as any);
      const verifiedUser = await repository.findById(user.id as any);
      
      expect(verifiedUser?.isEmailVerified).toBe(true);
    });

    it('should update last login', async () => {
      const beforeLogin = user.lastLoginAt;
      await repository.updateLastLogin(user.id as any);
      const updatedUser = await repository.findById(user.id as any);
      
      expect(updatedUser?.lastLoginAt).not.toBe(beforeLogin);
      expect(updatedUser?.lastLoginAt).toBeInstanceOf(Date);
    });
  });

  describe('Role Management', () => {
    beforeEach(async () => {
      await repository.save(user);
    });

    it('should add role to user', async () => {
      const newRoleId = createRoleId('role-999');
      await repository.addRoleToUser(user.id as any, newRoleId);
      
      const updatedUser = await repository.findById(user.id as any);
      expect(updatedUser?.hasRole(newRoleId)).toBe(true);
    });

    it('should remove role from user', async () => {
      const roleId = createRoleId('role-789');
      await repository.removeRoleFromUser(user.id as any, roleId);
      
      const updatedUser = await repository.findById(user.id as any);
      expect(updatedUser?.hasRole(roleId)).toBe(false);
    });

    it('should check if user has role', async () => {
      const roleId = createRoleId('role-789');
      const hasRole = await repository.hasRole(user.id as any, roleId);
      
      expect(hasRole).toBe(true);
    });
  });

  describe('Statistics', () => {
    beforeEach(async () => {
      await repository.save(user);
    });

    it('should get user count', async () => {
      const count = await repository.getUserCount();
      expect(count).toBe(1);
    });

    it('should get user count by tenant', async () => {
      const count = await repository.getUserCountByTenant(user.tenantId);
      expect(count).toBe(1);
    });

    it('should get user count by role', async () => {
      const roleId = createRoleId('role-789');
      const count = await repository.getUserCountByRole(roleId);
      expect(count).toBe(1);
    });

    it('should get active user count', async () => {
      const count = await repository.getActiveUserCount();
      expect(count).toBe(1);
    });

    it('should get inactive user count', async () => {
      const count = await repository.getInactiveUserCount();
      expect(count).toBe(0);
    });
  });

  describe('Bulk Operations', () => {
    let user2: User;

    beforeEach(async () => {
      await repository.save(user);
      
      user2 = new User({
        id: createUserId('user-456'),
        username: 'jane.doe',
        email: new Email('jane@example.com'),
        firstName: 'Jane',
        lastName: 'Doe',
        isActive: true,
        isEmailVerified: true,
        roles: [createRoleId('role-789')],
        tenantId: user.tenantId
      });
      await repository.save(user2);
    });

    it('should bulk activate users', async () => {
      user.deactivate();
      user2.deactivate();
      await repository.update(user);
      await repository.update(user2);
      
      await repository.bulkActivateUsers([user.id as any, user2.id as any]);
      
      const activatedUser1 = await repository.findById(user.id as any);
      const activatedUser2 = await repository.findById(user2.id);
      
      expect(activatedUser1?.isActive).toBe(true);
      expect(activatedUser2?.isActive).toBe(true);
    });

    it('should bulk deactivate users', async () => {
      await repository.bulkDeactivateUsers([user.id as any, user2.id as any]);
      
      const deactivatedUser1 = await repository.findById(user.id as any);
      const deactivatedUser2 = await repository.findById(user2.id);
      
      expect(deactivatedUser1?.isActive).toBe(false);
      expect(deactivatedUser2?.isActive).toBe(false);
    });

    it('should bulk delete users', async () => {
      await repository.bulkDeleteUsers([user.id as any, user2.id as any]);
      
      const deletedUser1 = await repository.findById(user.id as any);
      const deletedUser2 = await repository.findById(user2.id);
      
      expect(deletedUser1).toBeNull();
      expect(deletedUser2).toBeNull();
    });
  });

  describe('Pagination', () => {
    beforeEach(async () => {
      // Create multiple users for pagination testing
      for (let i = 1; i <= 5; i++) {
        const testUser = new User({
          id: createUserId(`user-${i}`),
          username: `user${i}`,
          email: new Email(`user${i}@example.com`),
          firstName: `User${i}`,
          lastName: 'Test',
          isActive: true,
          isEmailVerified: true,
          roles: [],
          tenantId: createTenantId('tenant-456')
        });
        await repository.save(testUser);
      }
    });

    it('should paginate users', async () => {
      const result = await repository.findUsersPaginated({
        page: 1,
        pageSize: 2,
        sortBy: 'firstName',
        sortDirection: 'ASC'
      });
      
      expect(result.data).toHaveLength(2);
      expect(result.pagination.page).toBe(1);
      expect(result.pagination.pageSize).toBe(2);
      expect(result.pagination.totalItems).toBe(5);
      expect(result.pagination.totalPages).toBe(3);
      expect(result.pagination.hasNext).toBe(true);
      expect(result.pagination.hasPrevious).toBe(false);
    });
  });
});
