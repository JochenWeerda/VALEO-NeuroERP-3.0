/**
 * Domain Layer Exports for VALEO NeuroERP 3.0
 * Clean Architecture - Domain Layer
 */
// Entities
export { BaseEntity, AuditableEntity } from './entities/base-entity.js';
export { User } from './entities/user.js';
// Value Objects
export * from './value-objects/branded-types.js';
export { Email, PhoneNumber, Address, Money, Percentage, DateRange } from './value-objects/common-value-objects.js';
// Domain Events
export { BaseDomainEvent } from './events/base-domain-event.js';
export { UserCreatedEvent, UserUpdatedEvent, UserEmailChangedEvent, UserEmailVerifiedEvent, UserActivatedEvent, UserDeactivatedEvent, UserRoleAddedEvent, UserRoleRemovedEvent, UserLoggedInEvent, UserLoggedOutEvent, UserTenantChangedEvent, UserDeletedEvent } from './events/user-events.js';
//# sourceMappingURL=index.js.map