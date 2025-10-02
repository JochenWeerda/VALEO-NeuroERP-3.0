/**
 * User Domain Events for VALEO NeuroERP 3.0
 * Events related to user lifecycle and operations
 */
import { BaseDomainEvent } from './base-domain-event.js';
import type { UserId, RoleId, TenantId, AuditId } from '../value-objects/branded-types.js';
export declare class UserCreatedEvent extends BaseDomainEvent {
    readonly data: {
        username: string;
        email: string;
        firstName: string;
        lastName: string;
        tenantId: TenantId;
        createdBy?: AuditId;
    };
    constructor(aggregateId: UserId, data: {
        username: string;
        email: string;
        firstName: string;
        lastName: string;
        tenantId: TenantId;
        createdBy?: AuditId;
    });
}
export declare class UserUpdatedEvent extends BaseDomainEvent {
    readonly data: {
        firstName?: string;
        lastName?: string;
        phoneNumber?: string;
        address?: string;
        updatedBy?: AuditId;
    };
    constructor(aggregateId: UserId, data: {
        firstName?: string;
        lastName?: string;
        phoneNumber?: string;
        address?: string;
        updatedBy?: AuditId;
    });
}
export declare class UserEmailChangedEvent extends BaseDomainEvent {
    readonly data: {
        oldEmail: string;
        newEmail: string;
        changedBy?: AuditId;
    };
    constructor(aggregateId: UserId, data: {
        oldEmail: string;
        newEmail: string;
        changedBy?: AuditId;
    });
}
export declare class UserEmailVerifiedEvent extends BaseDomainEvent {
    readonly data: {
        verifiedAt: Date;
        verifiedBy?: AuditId;
    };
    constructor(aggregateId: UserId, data: {
        verifiedAt: Date;
        verifiedBy?: AuditId;
    });
}
export declare class UserActivatedEvent extends BaseDomainEvent {
    readonly data: {
        activatedAt: Date;
        activatedBy?: AuditId;
    };
    constructor(aggregateId: UserId, data: {
        activatedAt: Date;
        activatedBy?: AuditId;
    });
}
export declare class UserDeactivatedEvent extends BaseDomainEvent {
    readonly data: {
        deactivatedAt: Date;
        deactivatedBy?: AuditId;
        reason?: string;
    };
    constructor(aggregateId: UserId, data: {
        deactivatedAt: Date;
        deactivatedBy?: AuditId;
        reason?: string;
    });
}
export declare class UserRoleAddedEvent extends BaseDomainEvent {
    readonly data: {
        roleId: RoleId;
        addedAt: Date;
        addedBy?: AuditId;
    };
    constructor(aggregateId: UserId, data: {
        roleId: RoleId;
        addedAt: Date;
        addedBy?: AuditId;
    });
}
export declare class UserRoleRemovedEvent extends BaseDomainEvent {
    readonly data: {
        roleId: RoleId;
        removedAt: Date;
        removedBy?: AuditId;
    };
    constructor(aggregateId: UserId, data: {
        roleId: RoleId;
        removedAt: Date;
        removedBy?: AuditId;
    });
}
export declare class UserLoggedInEvent extends BaseDomainEvent {
    readonly data: {
        loginAt: Date;
        ipAddress?: string;
        userAgent?: string;
        sessionId?: string;
    };
    constructor(aggregateId: UserId, data: {
        loginAt: Date;
        ipAddress?: string;
        userAgent?: string;
        sessionId?: string;
    });
}
export declare class UserLoggedOutEvent extends BaseDomainEvent {
    readonly data: {
        logoutAt: Date;
        sessionId?: string;
        logoutReason?: string;
    };
    constructor(aggregateId: UserId, data: {
        logoutAt: Date;
        sessionId?: string;
        logoutReason?: string;
    });
}
export declare class UserTenantChangedEvent extends BaseDomainEvent {
    readonly data: {
        oldTenantId: TenantId;
        newTenantId: TenantId;
        changedAt: Date;
        changedBy?: AuditId;
    };
    constructor(aggregateId: UserId, data: {
        oldTenantId: TenantId;
        newTenantId: TenantId;
        changedAt: Date;
        changedBy?: AuditId;
    });
}
export declare class UserDeletedEvent extends BaseDomainEvent {
    readonly data: {
        deletedAt: Date;
        deletedBy?: AuditId;
        reason?: string;
    };
    constructor(aggregateId: UserId, data: {
        deletedAt: Date;
        deletedBy?: AuditId;
        reason?: string;
    });
}
//# sourceMappingURL=user-events.d.ts.map