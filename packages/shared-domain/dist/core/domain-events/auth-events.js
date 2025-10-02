"use strict";
/**
 * Authentication Domain Events - MSOA Implementation nach Clean Architecture
 * Core Layer Domain Events migrated to VALEO-NeuroERP-3.0
 * Authentication business domain event definitions
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthEventValidator = exports.AuthEventFactory = void 0;
/**
 * Event Factory Functions nach Clean Architecture Domain Layer
 */
class AuthEventFactory {
    /**
     * Create User Login Event
     */
    static createUserLoggedInEvent(eventData) {
        return {
            eventType: 'UserLoggedIn',
            aggregateId: eventData.aggregateId,
            sessionId: eventData.sessionId,
            loginMethod: eventData.loginMethod,
            ipAddress: eventData.ipAddress,
            userAgent: eventData.userAgent,
            timestamp: new Date(),
            metadata: eventData.metadata || {},
            eventId: `login_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
    }
    /**
     * Create Logout Event
     */
    static createUserLoggedOutEvent(eventData) {
        return {
            eventType: 'UserLoggedOut',
            aggregateId: eventData.aggregateId,
            sessionId: eventData.sessionId,
            duration: eventData.duration,
            reason: eventData.reason,
            timestamp: new Date(),
            metadata: eventData.metadata || {},
            eventId: `logout_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
    }
    /**
     * Create Authentication Failed Event
     */
    static createAuthenticationFailedEvent(eventData) {
        return {
            eventType: 'AuthenticationFailed',
            aggregateId: eventData.aggregateId,
            attemptedUsername: eventData.attemptedUsername,
            reason: eventData.reason,
            ipAddress: eventData.ipAddress,
            userAgent: eventData.userAgent,
            timestamp: new Date(),
            metadata: eventData.metadata || {},
            eventId: `auth_failed_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
    }
    /**
     * Create Security Alert Event
     */
    static createSecurityAlertEvent(eventData) {
        return {
            eventType: 'SecurityAlert',
            aggregateId: eventData.aggregateId,
            alertType: eventData.alertType,
            severity: eventData.severity,
            description: eventData.description,
            ipAddress: eventData.ipAddress,
            source: eventData.source,
            timestamp: new Date(),
            metadata: eventData.metadata || {},
            eventId: `security_alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        };
    }
}
exports.AuthEventFactory = AuthEventFactory;
/**
 * Event Validation after Clean Architecture Domain Rules
 */
class AuthEventValidator {
    /**
     * Validate Domain Event
     */
    static isValidAuthEvent(event) {
        console.log(`[AUTH EVENT VALIDATOR] Validating event nach Clean Architecture domain rules: ${event.eventType}`);
        if (!event.eventId || !event.timestamp) {
            return false;
        }
        if (event.timestamp > new Date()) {
            console.warn('[AUTH EVENT VALIDATOR] Event timestamp is in the future');
            return false;
        }
        // Architecture: Add more domain-specific validation logic here
        return true;
    }
    /**
     * Validate Login Event
     */
    static isValidLoginEvent(event) {
        return AuthEventValidator.isValidAuthEvent(event) &&
            !!event.aggregateId &&
            !!event.sessionId &&
            !!event.ipAddress;
    }
    /**
     * Validate Logout Event
     */
    static isValidLogoutEvent(event) {
        return AuthEventValidator.isValidAuthEvent(event) &&
            !!event.aggregateId &&
            !!event.sessionId &&
            event.duration >= 0;
    }
}
exports.AuthEventValidator = AuthEventValidator;
exports.default = {
    // Domain Events
    UserLoggedInEvent,
    UserLoggedOutEvent,
    AuthenticationFailedEvent,
    PasswordChangedEvent,
    SessionExpiredEvent,
    UserAccountCreatedEvent,
    RoleAssignedEvent,
    PermissionGrantedEvent,
    SecurityAlertEvent,
    MultiFactorAuthenticationEvent,
    // Union Type
    AuthenticationDomainEvent,
    // Factory & Validator
    AuthEventFactory,
    AuthEventValidator
};
//# sourceMappingURL=auth-events.js.map