/**
 * Authentication Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service für VALEO-NeuroERP-3.0
 * Migrated from VALEO-NeuroERP-2.0 with Architecture Integrity preservation
 */
import { Brand } from '@valero-neuroerp/data-models/src/branded-types';
export type UserId = Brand<string, 'UserId'>;
export type SessionId = Brand<string, 'SessionId'>;
export type PermissionId = Brand<string, 'PermissionId'>;
export interface User {
    readonly id: UserId;
    readonly username: string;
    readonly email: string;
    readonly roles: string[];
    readonly permissions: PermissionId[];
    readonly isActive: boolean;
    readonly lastLogin?: Date;
}
export interface AuthSession {
    readonly id: SessionId;
    readonly userId: UserId;
    readonly token: string;
    readonly expiresAt: Date;
    readonly createdAt: Date;
}
export interface LoginCredentials {
    readonly username: string;
    readonly password: string;
}
export interface AuthResult {
    readonly success: boolean;
    readonly user?: User;
    readonly session?: AuthSession;
    readonly error?: string;
}
export declare class AuthenticationService {
    private readonly activeSessions;
    private readonly users;
    private readonly validTokens;
    constructor();
    /**
     * Initialize Authentication Service
     */
    private initializeAuthService;
    /**
     * Setup Default Users nach Business Requirements
     */
    private setupDefaultUsers;
    /**
     * Authenticate User login nach Business Rules
     */
    authenticate(credentials: LoginCredentials): Promise<AuthResult>;
    /**
     * Create Authentication Session
     */
    private createSession;
    /**
     * Validate Session Token
     */
    validateToken(token: string): Promise<{
        valid: boolean;
        user?: User;
    }>;
    /**
     * Check User Permissions
     */
    checkPermission(userId: UserId, requiredPermission: string): Promise<boolean>;
    /**
     * Logout User Session
     */
    logout(sessionId: SessionId): Promise<boolean>;
    /**
     * Remove Session
     */
    private removeSession;
    /**
     * Get Active Session Count
     */
    getActiveSessionCount(): Promise<number>;
    /**
     * Health check nach Architecture Pattern
     */
    healthCheck(): Promise<boolean>;
    private generateSessionId;
    private generateToken;
}
/**
 * Register Authentication Service in DI Container nach Clean Architecture
 */
export declare function registerAuthenticationService(): void;
//# sourceMappingURL=auth-service.d.ts.map