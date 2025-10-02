/**
 * User Domain Events for VALEO NeuroERP 3.0
 * Events related to user lifecycle and operations
 */

import { BaseDomainEvent } from './base-domain-event.js';
import type { UserId, RoleId, TenantId, AuditId } from '../value-objects/branded-types.js';
import type { Email, PhoneNumber, Address } from '../value-objects/common-value-objects.js';

// User Created Event
export class UserCreatedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      username: string;
      email: string;
      firstName: string;
      lastName: string;
      tenantId: TenantId;
      createdBy?: AuditId;
    }
  ) {
    super(aggregateId as any, 'UserCreated', 1);
  }
}

// User Updated Event
export class UserUpdatedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      firstName?: string;
      lastName?: string;
      phoneNumber?: string;
      address?: string;
      updatedBy?: AuditId;
    }
  ) {
    super(aggregateId as any, 'UserUpdated', 1);
  }
}

// User Email Changed Event
export class UserEmailChangedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      oldEmail: string;
      newEmail: string;
      changedBy?: AuditId;
    }
  ) {
    super(aggregateId as any, 'UserEmailChanged', 1);
  }
}

// User Email Verified Event
export class UserEmailVerifiedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      verifiedAt: Date;
      verifiedBy?: AuditId;
    }
  ) {
    super(aggregateId as any, 'UserEmailVerified', 1);
  }
}

// User Activated Event
export class UserActivatedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      activatedAt: Date;
      activatedBy?: AuditId;
    }
  ) {
    super(aggregateId as any, 'UserActivated', 1);
  }
}

// User Deactivated Event
export class UserDeactivatedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      deactivatedAt: Date;
      deactivatedBy?: AuditId;
      reason?: string;
    }
  ) {
    super(aggregateId as any, 'UserDeactivated', 1);
  }
}

// User Role Added Event
export class UserRoleAddedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      roleId: RoleId;
      addedAt: Date;
      addedBy?: AuditId;
    }
  ) {
    super(aggregateId as any, 'UserRoleAdded', 1);
  }
}

// User Role Removed Event
export class UserRoleRemovedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      roleId: RoleId;
      removedAt: Date;
      removedBy?: AuditId;
    }
  ) {
    super(aggregateId as any, 'UserRoleRemoved', 1);
  }
}

// User Logged In Event
export class UserLoggedInEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      loginAt: Date;
      ipAddress?: string;
      userAgent?: string;
      sessionId?: string;
    }
  ) {
    super(aggregateId as any, 'UserLoggedIn', 1);
  }
}

// User Logged Out Event
export class UserLoggedOutEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      logoutAt: Date;
      sessionId?: string;
      logoutReason?: string;
    }
  ) {
    super(aggregateId as any, 'UserLoggedOut', 1);
  }
}

// User Tenant Changed Event
export class UserTenantChangedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      oldTenantId: TenantId;
      newTenantId: TenantId;
      changedAt: Date;
      changedBy?: AuditId;
    }
  ) {
    super(aggregateId as any, 'UserTenantChanged', 1);
  }
}

// User Deleted Event
export class UserDeletedEvent extends BaseDomainEvent {
  constructor(
    aggregateId: UserId,
    public readonly data: {
      deletedAt: Date;
      deletedBy?: AuditId;
      reason?: string;
    }
  ) {
    super(aggregateId as any, 'UserDeleted', 1);
  }
}
