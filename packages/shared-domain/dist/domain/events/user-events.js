/**
 * User Domain Events for VALEO NeuroERP 3.0
 * Events related to user lifecycle and operations
 */
import { BaseDomainEvent } from './base-domain-event.js';
// User Created Event
export class UserCreatedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserCreated', 1);
        this.data = data;
    }
}
// User Updated Event
export class UserUpdatedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserUpdated', 1);
        this.data = data;
    }
}
// User Email Changed Event
export class UserEmailChangedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserEmailChanged', 1);
        this.data = data;
    }
}
// User Email Verified Event
export class UserEmailVerifiedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserEmailVerified', 1);
        this.data = data;
    }
}
// User Activated Event
export class UserActivatedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserActivated', 1);
        this.data = data;
    }
}
// User Deactivated Event
export class UserDeactivatedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserDeactivated', 1);
        this.data = data;
    }
}
// User Role Added Event
export class UserRoleAddedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserRoleAdded', 1);
        this.data = data;
    }
}
// User Role Removed Event
export class UserRoleRemovedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserRoleRemoved', 1);
        this.data = data;
    }
}
// User Logged In Event
export class UserLoggedInEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserLoggedIn', 1);
        this.data = data;
    }
}
// User Logged Out Event
export class UserLoggedOutEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserLoggedOut', 1);
        this.data = data;
    }
}
// User Tenant Changed Event
export class UserTenantChangedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserTenantChanged', 1);
        this.data = data;
    }
}
// User Deleted Event
export class UserDeletedEvent extends BaseDomainEvent {
    data;
    constructor(aggregateId, data) {
        super(aggregateId, 'UserDeleted', 1);
        this.data = data;
    }
}
//# sourceMappingURL=user-events.js.map