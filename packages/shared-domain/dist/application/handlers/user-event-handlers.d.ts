/**
 * User Event Handlers for VALEO NeuroERP 3.0
 * Handles domain events related to user operations
 */
import { UserCreatedEvent, UserUpdatedEvent, UserActivatedEvent, UserDeactivatedEvent, UserRoleAddedEvent, UserRoleRemovedEvent, UserLoggedInEvent, UserLoggedOutEvent, UserEmailVerifiedEvent, UserTenantChangedEvent, UserDeletedEvent } from '../../domain/events/user-events.js';
export interface EventHandler<T> {
    handle(event: T): Promise<void>;
}
export declare class UserCreatedEventHandler implements EventHandler<UserCreatedEvent> {
    handle(event: UserCreatedEvent): Promise<void>;
    private sendWelcomeEmail;
    private createAuditLog;
    private updateUserMetrics;
}
export declare class UserUpdatedEventHandler implements EventHandler<UserUpdatedEvent> {
    handle(event: UserUpdatedEvent): Promise<void>;
    private createAuditLog;
    private updateSearchIndex;
}
export declare class UserActivatedEventHandler implements EventHandler<UserActivatedEvent> {
    handle(event: UserActivatedEvent): Promise<void>;
    private sendActivationNotification;
    private updateUserMetrics;
}
export declare class UserDeactivatedEventHandler implements EventHandler<UserDeactivatedEvent> {
    handle(event: UserDeactivatedEvent): Promise<void>;
    private revokeActiveSessions;
    private sendDeactivationNotification;
    private updateUserMetrics;
}
export declare class UserRoleAddedEventHandler implements EventHandler<UserRoleAddedEvent> {
    handle(event: UserRoleAddedEvent): Promise<void>;
    private updatePermissionsCache;
    private notifySecuritySystems;
}
export declare class UserRoleRemovedEventHandler implements EventHandler<UserRoleRemovedEvent> {
    handle(event: UserRoleRemovedEvent): Promise<void>;
    private updatePermissionsCache;
    private notifySecuritySystems;
}
export declare class UserLoggedInEventHandler implements EventHandler<UserLoggedInEvent> {
    handle(event: UserLoggedInEvent): Promise<void>;
    private updateLastLoginTimestamp;
    private createAuditLog;
    private checkSuspiciousActivity;
}
export declare class UserLoggedOutEventHandler implements EventHandler<UserLoggedOutEvent> {
    handle(event: UserLoggedOutEvent): Promise<void>;
    private createAuditLog;
    private cleanupSessionData;
}
export declare class UserEmailVerifiedEventHandler implements EventHandler<UserEmailVerifiedEvent> {
    handle(event: UserEmailVerifiedEvent): Promise<void>;
    private sendVerificationConfirmation;
    private updateUserMetrics;
}
export declare class UserTenantChangedEventHandler implements EventHandler<UserTenantChangedEvent> {
    handle(event: UserTenantChangedEvent): Promise<void>;
    private updateTenantMetrics;
    private createAuditLog;
}
export declare class UserDeletedEventHandler implements EventHandler<UserDeletedEvent> {
    handle(event: UserDeletedEvent): Promise<void>;
    private cleanupRelatedData;
    private createAuditLog;
    private updateMetrics;
}
//# sourceMappingURL=user-event-handlers.d.ts.map