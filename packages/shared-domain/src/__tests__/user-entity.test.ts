/**
 * Tests for User Entity
 */

import { User } from '../domain/entities/user.js';
import { Email, PhoneNumber, Address } from '../domain/value-objects/common-value-objects.js';
import { createUserId, createRoleId, createTenantId, createAuditId } from '../domain/value-objects/branded-types.js';

describe('User Entity', () => {
  let user: User;
  const userId = createUserId('user-123');
  const tenantId = createTenantId('tenant-456');
  const roleId = createRoleId('role-789');
  const auditId = createAuditId('audit-101');

  beforeEach(() => {
    user = new User({
      id: userId,
      username: 'john.doe',
      email: new Email('john@example.com'),
      firstName: 'John',
      lastName: 'Doe',
      phoneNumber: new PhoneNumber('+1234567890'),
      address: new Address('123 Main St', 'City', '12345', 'Country'),
      isActive: true,
      isEmailVerified: true,
      roles: [roleId],
      tenantId: tenantId,
      createdBy: auditId
    });
  });

  describe('Basic Properties', () => {
    it('should have correct basic properties', () => {
      expect(user.id).toBe(userId);
      expect(user.username).toBe('john.doe');
      expect(user.firstName).toBe('John');
      expect(user.lastName).toBe('Doe');
      expect(user.fullName).toBe('John Doe');
      expect(user.isActive).toBe(true);
      expect(user.isEmailVerified).toBe(true);
      expect(user.tenantId).toBe(tenantId);
    });

    it('should have email and phone number', () => {
      expect(user.email.getValue()).toBe('john@example.com');
      expect(user.phoneNumber?.getValue()).toBe('+1234567890');
    });

    it('should have address', () => {
      expect(user.address?.street).toBe('123 Main St');
      expect(user.address?.city).toBe('City');
      expect(user.address?.postalCode).toBe('12345');
      expect(user.address?.country).toBe('Country');
    });
  });

  describe('Role Management', () => {
    it('should have initial roles', () => {
      expect(user.roles).toEqual([roleId]);
      expect(user.hasRole(roleId)).toBe(true);
    });

    it('should add role', () => {
      const newRoleId = createRoleId('role-999');
      user.addRole(newRoleId, auditId);
      
      expect(user.roles).toContain(newRoleId);
      expect(user.hasRole(newRoleId)).toBe(true);
    });

    it('should remove role', () => {
      user.removeRole(roleId, auditId);
      
      expect(user.roles).not.toContain(roleId);
      expect(user.hasRole(roleId)).toBe(false);
    });

    it('should not add duplicate role', () => {
      const initialRoles = [...user.roles];
      user.addRole(roleId, auditId);
      
      expect(user.roles).toEqual(initialRoles);
    });
  });

  describe('Profile Updates', () => {
    it('should update profile', () => {
      const newPhone = new PhoneNumber('+9876543210');
      const newAddress = new Address('456 Oak St', 'NewCity', '67890', 'NewCountry');
      
      user.updateProfile('Jane', 'Smith', newPhone, newAddress, auditId);
      
      expect(user.firstName).toBe('Jane');
      expect(user.lastName).toBe('Smith');
      expect(user.fullName).toBe('Jane Smith');
      expect(user.phoneNumber).toBe(newPhone);
      expect(user.address).toBe(newAddress);
    });

    it('should update email', () => {
      const newEmail = new Email('jane@example.com');
      user.updateEmail(newEmail, auditId);
      
      expect(user.email).toBe(newEmail);
      expect(user.isEmailVerified).toBe(false);
    });

    it('should verify email', () => {
      user.verifyEmail(auditId);
      expect(user.isEmailVerified).toBe(true);
    });
  });

  describe('User Status', () => {
    it('should activate user', () => {
      user.deactivate(auditId);
      expect(user.isActive).toBe(false);
      
      user.activate(auditId);
      expect(user.isActive).toBe(true);
    });

    it('should deactivate user', () => {
      user.deactivate(auditId);
      expect(user.isActive).toBe(false);
    });

    it('should check if user can login', () => {
      expect(user.canLogin()).toBe(true);
      
      user.deactivate(auditId);
      expect(user.canLogin()).toBe(false);
      
      user.activate(auditId);
      user.verifyEmail(auditId);
      expect(user.canLogin()).toBe(true);
    });
  });

  describe('Tenant Management', () => {
    it('should check tenant membership', () => {
      expect(user.isInTenant(tenantId)).toBe(true);
      
      const otherTenantId = createTenantId('tenant-999');
      expect(user.isInTenant(otherTenantId)).toBe(false);
    });

    it('should change tenant', () => {
      const newTenantId = createTenantId('tenant-999');
      user.changeTenant(newTenantId, auditId);
      
      expect(user.tenantId).toBe(newTenantId);
    });
  });

  describe('Login Tracking', () => {
    it('should record login', () => {
      const beforeLogin = user.lastLoginAt;
      user.recordLogin(auditId);
      
      expect(user.lastLoginAt).not.toBe(beforeLogin);
      expect(user.lastLoginAt).toBeInstanceOf(Date);
    });
  });

  describe('Audit Trail', () => {
    it('should track creation and updates', () => {
      expect(user.createdBy).toBe(auditId);
      
      user.updateProfile('Jane', 'Smith', undefined, undefined, auditId);
      expect(user.updatedBy).toBe(auditId);
      expect(user.version).toBeGreaterThan(1);
    });
  });
});

