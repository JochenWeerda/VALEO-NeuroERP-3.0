import { DomainEvent } from '@valero-neuroerp/data-models/domain-events';
import { UserId, TenantId, PermissionId } from '@valero-neuroerp/data-models/branded-types';
export interface UserCreatedEvent extends DomainEvent {
    type: 'UserCreated';
    userId: UserId;
    userEmail: string;
    tenantId: TenantId;
    role: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface UserUpdatedEvent extends DomainEvent {
    type: 'UserUpdated';
    userId: UserId;
    changes: Record<string, any>;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface UserAuthenticatedEvent extends DomainEvent {
    type: 'UserAuthenticated';
    userId: UserId;
    userEmail: string;
    tenantId: TenantId;
    ipAddress?: string;
    userAgent?: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface UserDeactivatedEvent extends DomainEvent {
    type: 'UserDeactivated';
    userId: UserId;
    userEmail: string;
    reason: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface TenantCreatedEvent extends DomainEvent {
    type: 'TenantCreated';
    tenantId: TenantId;
    tenantName: string;
    tenantDomain: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface TenantUpdatedEvent extends DomainEvent {
    type: 'TenantUpdated';
    tenantId: TenantId;
    changes: Record<string, any>;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface TenantDeactivatedEvent extends DomainEvent {
    type: 'TenantDeactivated';
    tenantId: TenantId;
    tenantName: string;
    reason: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface PermissionCreatedEvent extends DomainEvent {
    type: 'PermissionCreated';
    permissionId: PermissionId;
    permissionName: string;
    resource: string;
    action: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface PermissionUpdatedEvent extends DomainEvent {
    type: 'PermissionUpdated';
    permissionId: PermissionId;
    changes: Record<string, any>;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface PermissionRevokedEvent extends DomainEvent {
    type: 'PermissionRevoked';
    permissionId: PermissionId;
    userId: UserId;
    reason: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface RoleCreatedEvent extends DomainEvent {
    type: 'RoleCreated';
    roleId: string;
    roleName: string;
    tenantId: TenantId;
    permissions: PermissionId[];
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface RoleUpdatedEvent extends DomainEvent {
    type: 'RoleUpdated';
    roleId: string;
    changes: Record<string, any>;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface RoleAssignedEvent extends DomainEvent {
    type: 'RoleAssigned';
    roleId: string;
    userId: UserId;
    assignedBy: UserId;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface AuditEventLoggedEvent extends DomainEvent {
    type: 'AuditEventLogged';
    auditLogId: string;
    userId: UserId;
    action: string;
    resource: string;
    resourceId: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface SecurityViolationEvent extends DomainEvent {
    type: 'SecurityViolation';
    userId?: UserId;
    violationType: string;
    description: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    ipAddress?: string;
    userAgent?: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface NotificationCreatedEvent extends DomainEvent {
    type: 'NotificationCreated';
    notificationId: string;
    userId: UserId;
    type: string;
    title: string;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface NotificationReadEvent extends DomainEvent {
    type: 'NotificationRead';
    notificationId: string;
    userId: UserId;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface NotificationDeletedEvent extends DomainEvent {
    type: 'NotificationDeleted';
    notificationId: string;
    userId: UserId;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface SystemHealthCheckEvent extends DomainEvent {
    type: 'SystemHealthCheck';
    healthScore: number;
    totalUsers: number;
    totalTenants: number;
    activeUsers: number;
    activeTenants: number;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export interface SystemMaintenanceEvent extends DomainEvent {
    type: 'SystemMaintenance';
    maintenanceType: 'scheduled' | 'emergency' | 'completed';
    description: string;
    startTime?: Date;
    endTime?: Date;
    timestamp: Date;
    metadata: {
        source: string;
        userId: string;
    };
}
export type SharedDomainEvent = UserCreatedEvent | UserUpdatedEvent | UserAuthenticatedEvent | UserDeactivatedEvent | TenantCreatedEvent | TenantUpdatedEvent | TenantDeactivatedEvent | PermissionCreatedEvent | PermissionUpdatedEvent | PermissionRevokedEvent | RoleCreatedEvent | RoleUpdatedEvent | RoleAssignedEvent | AuditEventLoggedEvent | SecurityViolationEvent | NotificationCreatedEvent | NotificationReadEvent | NotificationDeletedEvent | SystemHealthCheckEvent | SystemMaintenanceEvent;
export declare class SharedDomainEventHandler {
    handleUserCreated(event: UserCreatedEvent): Promise<void>;
    handleUserUpdated(event: UserUpdatedEvent): Promise<void>;
    handleUserAuthenticated(event: UserAuthenticatedEvent): Promise<void>;
    handleUserDeactivated(event: UserDeactivatedEvent): Promise<void>;
    handleTenantCreated(event: TenantCreatedEvent): Promise<void>;
    handleTenantUpdated(event: TenantUpdatedEvent): Promise<void>;
    handleTenantDeactivated(event: TenantDeactivatedEvent): Promise<void>;
    handlePermissionCreated(event: PermissionCreatedEvent): Promise<void>;
    handlePermissionUpdated(event: PermissionUpdatedEvent): Promise<void>;
    handlePermissionRevoked(event: PermissionRevokedEvent): Promise<void>;
    handleRoleCreated(event: RoleCreatedEvent): Promise<void>;
    handleRoleUpdated(event: RoleUpdatedEvent): Promise<void>;
    handleRoleAssigned(event: RoleAssignedEvent): Promise<void>;
    handleAuditEventLogged(event: AuditEventLoggedEvent): Promise<void>;
    handleSecurityViolation(event: SecurityViolationEvent): Promise<void>;
    handleNotificationCreated(event: NotificationCreatedEvent): Promise<void>;
    handleNotificationRead(event: NotificationReadEvent): Promise<void>;
    handleNotificationDeleted(event: NotificationDeletedEvent): Promise<void>;
    handleSystemHealthCheck(event: SystemHealthCheckEvent): Promise<void>;
    handleSystemMaintenance(event: SystemMaintenanceEvent): Promise<void>;
}
export declare const sharedDomainEventHandler: SharedDomainEventHandler;
//# sourceMappingURL=shared-domain-events.d.ts.map