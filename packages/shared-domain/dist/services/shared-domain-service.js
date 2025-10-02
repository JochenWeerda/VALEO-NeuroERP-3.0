"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.sharedDomainService = exports.SharedDomainService = void 0;
// domains/shared/src/services/shared-domain-service.ts
const base_service_1 = require("@valero-neuroerp/utilities/base-service");
const business_logic_orchestrator_1 = require("@valero-neuroerp/business-rules/business-logic-orchestrator");
class SharedDomainService extends base_service_1.BaseService {
    constructor() {
        super();
        this.initializeBusinessRules();
    }
    initializeBusinessRules() {
        business_logic_orchestrator_1.businessLogicOrchestrator.registerRule('Shared', new UserValidationRule());
        business_logic_orchestrator_1.businessLogicOrchestrator.registerRule('Shared', new TenantValidationRule());
        business_logic_orchestrator_1.businessLogicOrchestrator.registerRule('Shared', new PermissionValidationRule());
    }
    // User Management
    async createUser(request) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'create',
            domain: 'Shared',
            metadata: { source: 'shared-service' }
        };
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Shared', request, 'create', context);
        if (!result.success) {
            throw new Error(`User creation failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        const user = {
            id: this.generateUserId(),
            ...result.data,
            isActive: true,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        await this.repository.create(user);
        await this.publishDomainEvent('UserCreated', {
            userId: user.id,
            userEmail: user.email,
            tenantId: user.tenantId,
            timestamp: new Date()
        });
        return user;
    }
    async updateUser(userId, updates) {
        const existingUser = await this.repository.findById(userId);
        if (!existingUser) {
            throw new Error(`User ${userId} not found`);
        }
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'update',
            domain: 'Shared',
            metadata: { source: 'shared-service', userId }
        };
        const updateData = { ...existingUser, ...updates };
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Shared', updateData, 'update', context);
        if (!result.success) {
            throw new Error(`User update failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        const updatedUser = {
            ...result.data,
            updatedAt: new Date()
        };
        await this.repository.update(userId, updatedUser);
        await this.publishDomainEvent('UserUpdated', {
            userId: updatedUser.id,
            changes: updates,
            timestamp: new Date()
        });
        return updatedUser;
    }
    async authenticateUser(email, password) {
        const users = await this.repository.find({ email });
        const user = users.find(u => u.isActive);
        if (!user) {
            return null;
        }
        // In a real implementation, you would verify the password hash
        // For now, we'll just simulate authentication
        const isAuthenticated = password === 'password'; // Simplified for demo
        if (isAuthenticated) {
            await this.updateUser(user.id, { lastLoginAt: new Date() });
            await this.publishDomainEvent('UserAuthenticated', {
                userId: user.id,
                userEmail: user.email,
                timestamp: new Date()
            });
            return user;
        }
        return null;
    }
    // Tenant Management
    async createTenant(name, domain, settings = {}) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'create',
            domain: 'Shared',
            metadata: { source: 'shared-service' }
        };
        const tenantData = { name, domain, settings };
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Shared', tenantData, 'create', context);
        if (!result.success) {
            throw new Error(`Tenant creation failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        const tenant = {
            id: this.generateTenantId(),
            ...result.data,
            isActive: true,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        await this.repository.create(tenant);
        await this.publishDomainEvent('TenantCreated', {
            tenantId: tenant.id,
            tenantName: tenant.name,
            tenantDomain: tenant.domain,
            timestamp: new Date()
        });
        return tenant;
    }
    // Permission Management
    async createPermission(name, resource, action, conditions) {
        const context = {
            userId: this.getCurrentUserId(),
            timestamp: new Date(),
            operation: 'create',
            domain: 'Shared',
            metadata: { source: 'shared-service' }
        };
        const permissionData = { name, resource, action, conditions };
        const result = await business_logic_orchestrator_1.businessLogicOrchestrator.executeBusinessLogic('Shared', permissionData, 'create', context);
        if (!result.success) {
            throw new Error(`Permission creation failed: ${result.errors.map(e => e.message).join(', ')}`);
        }
        const permission = {
            id: this.generatePermissionId(),
            ...result.data,
            createdAt: new Date(),
            updatedAt: new Date()
        };
        await this.repository.create(permission);
        await this.publishDomainEvent('PermissionCreated', {
            permissionId: permission.id,
            permissionName: permission.name,
            resource: permission.resource,
            action: permission.action,
            timestamp: new Date()
        });
        return permission;
    }
    async checkPermission(userId, resource, action) {
        const user = await this.repository.findById(userId);
        if (!user || !user.isActive) {
            return false;
        }
        // In a real implementation, you would check user roles and permissions
        // For now, we'll simulate permission checking
        return true; // Simplified for demo
    }
    // Audit Logging
    async logAuditEvent(userId, tenantId, action, resource, resourceId, changes, ipAddress, userAgent) {
        const auditLog = {
            id: this.generateAuditLogId(),
            userId,
            tenantId,
            action,
            resource,
            resourceId,
            changes,
            ipAddress,
            userAgent,
            timestamp: new Date()
        };
        await this.repository.create(auditLog);
        await this.publishDomainEvent('AuditEventLogged', {
            auditLogId: auditLog.id,
            userId: auditLog.userId,
            action: auditLog.action,
            resource: auditLog.resource,
            timestamp: new Date()
        });
        return auditLog;
    }
    // Notification Management
    async createNotification(userId, tenantId, type, title, message) {
        const notification = {
            id: this.generateNotificationId(),
            userId,
            tenantId,
            type,
            title,
            message,
            isRead: false,
            createdAt: new Date()
        };
        await this.repository.create(notification);
        await this.publishDomainEvent('NotificationCreated', {
            notificationId: notification.id,
            userId: notification.userId,
            type: notification.type,
            title: notification.title,
            timestamp: new Date()
        });
        return notification;
    }
    async markNotificationAsRead(notificationId) {
        const notification = await this.repository.findById(notificationId);
        if (!notification) {
            throw new Error(`Notification ${notificationId} not found`);
        }
        const updatedNotification = {
            ...notification,
            isRead: true,
            readAt: new Date()
        };
        await this.repository.update(notificationId, updatedNotification);
        await this.publishDomainEvent('NotificationRead', {
            notificationId: updatedNotification.id,
            userId: updatedNotification.userId,
            timestamp: new Date()
        });
        return updatedNotification;
    }
    // Helper Methods
    async getUser(userId) {
        return this.repository.findById(userId);
    }
    async getUsers(filters) {
        return this.repository.find(filters);
    }
    async getTenant(tenantId) {
        return this.repository.findById(tenantId);
    }
    async getTenants() {
        return this.repository.findAll();
    }
    async getPermissions() {
        return this.repository.findAll();
    }
    async getAuditLogs(filters) {
        return this.repository.find(filters);
    }
    async getNotifications(userId, isRead) {
        const filters = { userId };
        if (isRead !== undefined) {
            filters.isRead = isRead;
        }
        return this.repository.find(filters);
    }
    generateUserId() {
        return `USER_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    generateTenantId() {
        return `TENANT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    generatePermissionId() {
        return `PERM_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    generateAuditLogId() {
        return `AUDIT_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    generateNotificationId() {
        return `NOTIF_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    getCurrentUserId() {
        return 'system';
    }
    async publishDomainEvent(eventType, data) {
        console.log(`Publishing domain event: ${eventType}`, data);
    }
}
exports.SharedDomainService = SharedDomainService;
// Shared Business Rules
class UserValidationRule {
    name = 'SHARED_USER_VALIDATION';
    description = 'Validates user creation and updates';
    priority = 100;
    domain = 'Shared';
    version = '1.0.0';
    enabled = true;
    async validate(data) {
        const errors = [];
        const warnings = [];
        if (!data.email || data.email.trim().length === 0) {
            errors.push({
                field: 'email',
                message: 'Email is required',
                code: 'SHARED_USER_EMAIL_REQUIRED',
                severity: 'error'
            });
        }
        else if (!this.isValidEmail(data.email)) {
            errors.push({
                field: 'email',
                message: 'Invalid email format',
                code: 'SHARED_USER_INVALID_EMAIL',
                severity: 'error'
            });
        }
        if (!data.firstName || data.firstName.trim().length === 0) {
            errors.push({
                field: 'firstName',
                message: 'First name is required',
                code: 'SHARED_USER_FIRST_NAME_REQUIRED',
                severity: 'error'
            });
        }
        if (!data.lastName || data.lastName.trim().length === 0) {
            errors.push({
                field: 'lastName',
                message: 'Last name is required',
                code: 'SHARED_USER_LAST_NAME_REQUIRED',
                severity: 'error'
            });
        }
        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
}
class TenantValidationRule {
    name = 'SHARED_TENANT_VALIDATION';
    description = 'Validates tenant creation';
    priority = 95;
    domain = 'Shared';
    version = '1.0.0';
    enabled = true;
    async validate(data) {
        const errors = [];
        const warnings = [];
        if (!data.name || data.name.trim().length === 0) {
            errors.push({
                field: 'name',
                message: 'Tenant name is required',
                code: 'SHARED_TENANT_NAME_REQUIRED',
                severity: 'error'
            });
        }
        if (!data.domain || data.domain.trim().length === 0) {
            errors.push({
                field: 'domain',
                message: 'Tenant domain is required',
                code: 'SHARED_TENANT_DOMAIN_REQUIRED',
                severity: 'error'
            });
        }
        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }
}
class PermissionValidationRule {
    name = 'SHARED_PERMISSION_VALIDATION';
    description = 'Validates permission creation';
    priority = 90;
    domain = 'Shared';
    version = '1.0.0';
    enabled = true;
    async validate(data) {
        const errors = [];
        const warnings = [];
        if (!data.name || data.name.trim().length === 0) {
            errors.push({
                field: 'name',
                message: 'Permission name is required',
                code: 'SHARED_PERMISSION_NAME_REQUIRED',
                severity: 'error'
            });
        }
        if (!data.resource || data.resource.trim().length === 0) {
            errors.push({
                field: 'resource',
                message: 'Resource is required',
                code: 'SHARED_PERMISSION_RESOURCE_REQUIRED',
                severity: 'error'
            });
        }
        if (!data.action || data.action.trim().length === 0) {
            errors.push({
                field: 'action',
                message: 'Action is required',
                code: 'SHARED_PERMISSION_ACTION_REQUIRED',
                severity: 'error'
            });
        }
        return {
            isValid: errors.length === 0,
            errors,
            warnings
        };
    }
}
exports.sharedDomainService = new SharedDomainService();
//# sourceMappingURL=shared-domain-service.js.map