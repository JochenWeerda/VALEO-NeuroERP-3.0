/**
 * Authentication Domain Events - MSOA Implementation nach Clean Architecture
 * Core Layer Domain Events migrated to VALEO-NeuroERP-3.0
 * Authentication business domain event definitions
 */
import { Brand } from '@valero-neuroerp/data-models/src/branded-types';
export type EventId = Brand<string, 'EventId'>;
export type UserId = Brand<string, 'UserId'>;
export type SessionId = Brand<string, 'SessionId'>;
/**
 * User Login Event
 */
export interface UserLoggedInEvent {
    readonly eventType: 'UserLoggedIn';
    readonly aggregateId: UserId;
    readonly sessionId: SessionId;
    readonly loginMethod: 'PASSWORD' | 'OAUTH' | 'SSO';
    readonly ipAddress: string;
    readonly userAgent: string;
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * User Logout Event
 */
export interface UserLoggedOutEvent {
    readonly eventType: 'UserLoggedOut';
    readonly aggregateId: UserId;
    readonly sessionId: SessionId;
    readonly duration: number;
    readonly reason: 'USER_INITIATED' | 'TIMEOUT' | 'ADMIN_FORCED' | 'SECURITY_VALIDATION';
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * Authentication Failed Event
 */
export interface AuthenticationFailedEvent {
    readonly eventType: 'AuthenticationFailed';
    readonly aggregateId?: UserId;
    readonly attemptedUsername: string;
    readonly reason: 'INVALID_CREDENTIALS' | 'ACCOUNT_LOCKED' | 'ACCOUNT_DISABLED' | 'TOO_MANY_ATTEMPTS';
    readonly ipAddress: string;
    readonly userAgent: string;
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * Password Changed Event
 */
export interface PasswordChangedEvent {
    readonly eventType: 'PasswordChanged';
    readonly aggregateId: UserId;
    readonly changedBy: UserId;
    readonly forcedChange: boolean;
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * Session Expired Event
 */
export interface SessionExpiredEvent {
    readonly eventType: 'SessionExpired';
    readonly aggregateId: UserId;
    readonly sessionId: SessionId;
    readonly expiredAt: Date;
    readonly reason: 'TIMEOUT' | 'INACTIVITY' | 'SECURITY_POLICY';
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * User Account Created Event
 */
export interface UserAccountCreatedEvent {
    readonly eventType: 'UserAccountCreated';
    readonly aggregateId: UserId;
    readonly createdBy?: UserId;
    readonly username: string;
    readonly email: string;
    readonly initialRole: string;
    readonly isActive: boolean;
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * Role Assigned Event
 */
export interface RoleAssignedEvent {
    readonly eventType: 'RoleAssigned';
    readonly aggregateId: UserId;
    readonly role: string;
    readonly assignedBy: UserId;
    readonly assignedAt: Date;
    readonly effectiveFrom: Date;
    readonly effectiveUntil?: Date;
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * Permission Granted Event
 */
export interface PermissionGrantedEvent {
    readonly eventType: 'PermissionGranted';
    readonly aggregateId: UserId;
    readonly permission: string;
    readonly resource?: string;
    readonly grantedBy: UserId;
    readonly grantedAt: Date;
    readonly expiresAt?: Date;
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * Security Alert Event
 */
export interface SecurityAlertEvent {
    readonly eventType: 'SecurityAlert';
    readonly aggregateId?: UserId;
    readonly alertType: 'SUSPICIOUS_ACTIVITY' | 'MULTIPLE_FAILED_LOGINS' | 'UNUSUAL_SESSION' | 'PRIVILEGE_ESCALATION';
    readonly severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    readonly description: string;
    readonly ipAddress?: string;
    readonly source: string;
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * Multi-Factor Authentication Event
 */
export interface MultiFactorAuthenticationEvent {
    readonly eventType: 'MultiFactorAuthentication';
    readonly aggregateId: UserId;
    readonly sessionId: SessionId;
    readonly mfaType: 'SMS' | 'EMAIL' | 'TOTP' | 'HARDWARE_TOKEN';
    readonly status: 'STARTED' | 'COMPLETED' | 'FAILED' | 'EXPIRED';
    readonly timestamp: Date;
    readonly metadata: Record<string, any>;
    readonly eventId: EventId;
}
/**
 * Union Type for all Authentication Domain Events
 */
export type AuthenticationDomainEvent = UserLoggedInEvent | UserLoggedOutEvent | AuthenticationFailedEvent | PasswordChangedEvent | SessionExpiredEvent | UserAccountCreatedEvent | RoleAssignedEvent | PermissionGrantedEvent | SecurityAlertEvent | MultiFactorAuthenticationEvent;
/**
 * Event Factory Functions nach Clean Architecture Domain Layer
 */
export declare class AuthEventFactory {
    /**
     * Create User Login Event
     */
    static createUserLoggedInEvent(eventData: {
        aggregateId: UserId;
        sessionId: SessionId;
        loginMethod: 'PASSWORD' | 'OAUTH' | 'SSO';
        ipAddress: string;
        userAgent: string;
        metadata?: Record<string, any>;
    }): UserLoggedInEvent;
    /**
     * Create Logout Event
     */
    static createUserLoggedOutEvent(eventData: {
        aggregateId: UserId;
        sessionId: SessionId;
        duration: number;
        reason: 'USER_INITIATED' | 'TIMEOUT' | 'ADMIN_FORCED' | 'SECURITY_VALIDATION';
        metadata?: Record<string, any>;
    }): UserLoggedOutEvent;
    /**
     * Create Authentication Failed Event
     */
    static createAuthenticationFailedEvent(eventData: {
        aggregateId?: UserId;
        attemptedUsername: string;
        reason: 'INVALID_CREDENTIALS' | 'ACCOUNT_LOCKED' | 'ACCOUNT_DISABLED' | 'TOO_MANY_ATTEMPTS';
        ipAddress: string;
        userAgent: string;
        metadata?: Record<string, any>;
    }): AuthenticationFailedEvent;
    /**
     * Create Security Alert Event
     */
    static createSecurityAlertEvent(eventData: {
        aggregateId?: UserId;
        alertType: 'SUSPICIOUS_ACTIVITY' | 'MULTIPLE_FAILED_LOGINS' | 'UNUSUAL_SESSION' | 'PRIVILEGE_ESCALATION';
        severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
        description: string;
        ipAddress?: string;
        source: string;
        metadata?: Record<string, any>;
    }): SecurityAlertEvent;
}
/**
 * Event Validation after Clean Architecture Domain Rules
 */
export declare class AuthEventValidator {
    /**
     * Validate Domain Event
     */
    static isValidAuthEvent(event: AuthenticationDomainEvent): boolean;
    /**
     * Validate Login Event
     */
    static isValidLoginEvent(event: UserLoggedInEvent): boolean;
    /**
     * Validate Logout Event
     */
    static isValidLogoutEvent(event: UserLoggedOutEvent): boolean;
}
declare const _default: {
    UserLoggedInEvent: any;
    UserLoggedOutEvent: any;
    AuthenticationFailedEvent: any;
    PasswordChangedEvent: any;
    SessionExpiredEvent: any;
    UserAccountCreatedEvent: any;
    RoleAssignedEvent: any;
    PermissionGrantedEvent: any;
    SecurityAlertEvent: any;
    MultiFactorAuthenticationEvent: any;
    AuthenticationDomainEvent: any;
    AuthEventFactory: typeof AuthEventFactory;
    AuthEventValidator: typeof AuthEventValidator;
};
export default _default;
//# sourceMappingURL=auth-events.d.ts.map