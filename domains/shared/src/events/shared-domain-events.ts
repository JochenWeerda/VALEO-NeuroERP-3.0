// domains/shared/src/events/shared-domain-events.ts
import { DomainEvent } from '@packages/data-models/domain-events';
import { UserId, TenantId, PermissionId } from '@packages/data-models/branded-types';

// User Events
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

// Tenant Events
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

// Permission Events
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

// Role Events
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

// Audit Events
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

// Notification Events
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

// System Events
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

// Union type for all Shared domain events
export type SharedDomainEvent = 
  | UserCreatedEvent
  | UserUpdatedEvent
  | UserAuthenticatedEvent
  | UserDeactivatedEvent
  | TenantCreatedEvent
  | TenantUpdatedEvent
  | TenantDeactivatedEvent
  | PermissionCreatedEvent
  | PermissionUpdatedEvent
  | PermissionRevokedEvent
  | RoleCreatedEvent
  | RoleUpdatedEvent
  | RoleAssignedEvent
  | AuditEventLoggedEvent
  | SecurityViolationEvent
  | NotificationCreatedEvent
  | NotificationReadEvent
  | NotificationDeletedEvent
  | SystemHealthCheckEvent
  | SystemMaintenanceEvent;

// Event Handlers
export class SharedDomainEventHandler {
  async handleUserCreated(event: UserCreatedEvent): Promise<void> {
    console.log(`User created: ${event.userEmail} (${event.role}) in tenant ${event.tenantId}`);
    // Additional business logic for user creation
  }

  async handleUserUpdated(event: UserUpdatedEvent): Promise<void> {
    console.log(`User updated: ${event.userId}`, event.changes);
    // Additional business logic for user updates
  }

  async handleUserAuthenticated(event: UserAuthenticatedEvent): Promise<void> {
    console.log(`User authenticated: ${event.userEmail} from ${event.ipAddress}`);
    // Additional business logic for user authentication
  }

  async handleUserDeactivated(event: UserDeactivatedEvent): Promise<void> {
    console.log(`User deactivated: ${event.userEmail} - Reason: ${event.reason}`);
    // Additional business logic for user deactivation
  }

  async handleTenantCreated(event: TenantCreatedEvent): Promise<void> {
    console.log(`Tenant created: ${event.tenantName} (${event.tenantDomain})`);
    // Additional business logic for tenant creation
  }

  async handleTenantUpdated(event: TenantUpdatedEvent): Promise<void> {
    console.log(`Tenant updated: ${event.tenantId}`, event.changes);
    // Additional business logic for tenant updates
  }

  async handleTenantDeactivated(event: TenantDeactivatedEvent): Promise<void> {
    console.log(`Tenant deactivated: ${event.tenantName} - Reason: ${event.reason}`);
    // Additional business logic for tenant deactivation
  }

  async handlePermissionCreated(event: PermissionCreatedEvent): Promise<void> {
    console.log(`Permission created: ${event.permissionName} (${event.resource}:${event.action})`);
    // Additional business logic for permission creation
  }

  async handlePermissionUpdated(event: PermissionUpdatedEvent): Promise<void> {
    console.log(`Permission updated: ${event.permissionId}`, event.changes);
    // Additional business logic for permission updates
  }

  async handlePermissionRevoked(event: PermissionRevokedEvent): Promise<void> {
    console.log(`Permission revoked: ${event.permissionId} from user ${event.userId} - Reason: ${event.reason}`);
    // Additional business logic for permission revocation
  }

  async handleRoleCreated(event: RoleCreatedEvent): Promise<void> {
    console.log(`Role created: ${event.roleName} with ${event.permissions.length} permissions`);
    // Additional business logic for role creation
  }

  async handleRoleUpdated(event: RoleUpdatedEvent): Promise<void> {
    console.log(`Role updated: ${event.roleId}`, event.changes);
    // Additional business logic for role updates
  }

  async handleRoleAssigned(event: RoleAssignedEvent): Promise<void> {
    console.log(`Role assigned: ${event.roleId} to user ${event.userId} by ${event.assignedBy}`);
    // Additional business logic for role assignment
  }

  async handleAuditEventLogged(event: AuditEventLoggedEvent): Promise<void> {
    console.log(`Audit event logged: ${event.action} on ${event.resource} by user ${event.userId}`);
    // Additional business logic for audit logging
  }

  async handleSecurityViolation(event: SecurityViolationEvent): Promise<void> {
    console.log(`Security violation: ${event.violationType} - ${event.description} (${event.severity})`);
    // Additional business logic for security violations
  }

  async handleNotificationCreated(event: NotificationCreatedEvent): Promise<void> {
    console.log(`Notification created: ${event.title} (${event.type}) for user ${event.userId}`);
    // Additional business logic for notification creation
  }

  async handleNotificationRead(event: NotificationReadEvent): Promise<void> {
    console.log(`Notification read: ${event.notificationId} by user ${event.userId}`);
    // Additional business logic for notification reading
  }

  async handleNotificationDeleted(event: NotificationDeletedEvent): Promise<void> {
    console.log(`Notification deleted: ${event.notificationId} by user ${event.userId}`);
    // Additional business logic for notification deletion
  }

  async handleSystemHealthCheck(event: SystemHealthCheckEvent): Promise<void> {
    console.log(`System health check: Score ${event.healthScore}% (${event.activeUsers}/${event.totalUsers} users, ${event.activeTenants}/${event.totalTenants} tenants)`);
    // Additional business logic for system health checks
  }

  async handleSystemMaintenance(event: SystemMaintenanceEvent): Promise<void> {
    console.log(`System maintenance: ${event.maintenanceType} - ${event.description}`);
    // Additional business logic for system maintenance
  }
}

export const sharedDomainEventHandler = new SharedDomainEventHandler();
