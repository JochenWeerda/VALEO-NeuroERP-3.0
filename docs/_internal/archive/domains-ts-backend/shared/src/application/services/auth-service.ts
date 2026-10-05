/**
 * Authentication Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service für VALEO-NeuroERP-3.0
 * Migrated from VALEO-NeuroERP-2.0 with Architecture Integrity preservation
 */

import { DIContainer } from '@valeo-neuroerp-3.0/packages/utilities/src/di-container';
import { Brand } from '@valeo-neuroerp-3.0/packages/data-models/src/branded-types';

// ===== BRANDED TYPES =====
export type UserId = Brand<string, 'UserId'>;
export type SessionId = Brand<string, 'SessionId'>;
export type PermissionId = Brand<string, 'PermissionId'>;

// ===== DOMAIN ENTITIES =====
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

// ===== AUTHENTICATION SERVICE nach CRM Pattern =====
export class AuthenticationService {
    private readonly activeSessions: Map<SessionId, AuthSession> = new Map();
    private readonly users: Map<UserId, User> = new Map();
    private readonly validTokens: Set<string> = new Set();

    constructor() {
        console.log('[AUTH SERVICE] Initializing Authentication Service nach Architecture guidelines...');
        this.initializeAuthService();
    }

    /**
     * Initialize Authentication Service
     */
    private initializeAuthService(): void {
        console.log('[AUTH INIT] Initializing authentication nach Clean Architecture...');
        
        try {
            this.setupDefaultUsers();
            console.log('[AUTH INIT] ✓ Authentication service initialized nach Clean Architecture');
        } catch (error) {
            console.error('[AUTH INIT] Authentication initialization failed:', error);
            throw new Error(`Authentication configuration failed: ${error}`);
        }
    }

    /**
     * Setup Default Users nach Business Requirements
     */
    private setupDefaultUsers(): void {
        console.log('[AUTH SETUP] Setting up default users nach business model...');
        
        // Architecture: Create system users with appropriate permissions
        const defaultUsers = [
            {
                id: 'admin_001' as UserId,
                username: 'admin',
                email: 'admin@valeo-neuroerp.com',
                roles: ['administrator'],
                permissions: ['READ', 'WRITE', 'DELETE', 'MANAGE_USERS'] as PermissionId[],
                isActive: true
            },
            {
                id: 'manager_001' as UserId,
                username: 'manager',
                email: 'manager@valeo-neuroerp.com',
                roles: ['manager'],
                permissions: ['READ', 'WRITE'] as PermissionId[],
                isActive: true
            },
            {
                id: 'user_001' as UserId,
                username: 'user',
                email: 'user@valeo-neuroerp.com',
                roles: ['user'],
                permissions: ['READ'] as PermissionId[],
                isActive: true
            }
        ];

        for (const userData of defaultUsers) {
            const user: User = {
                ...userData,
                lastLogin: undefined
            };
            this.users.set(user.id, user);
        }
        
        console.log('[AUTH SETUP] ✓ Default users configured nach business model');
    }

    /**
     * Authenticate User login nach Business Rules
     */
    async authenticate(credentials: LoginCredentials): Promise<AuthResult> {
        try {
            console.log(`[AUTH LOGIN] Authenticating user: ${credentials.username}`);
            
            // Find user by username
            const user = Array.from(this.users.values()).find(
                u => u.username === credentials.username
            );
            
            if (!user) {
                return {
                    success: false,
                    error: 'User not found'
                };
            }

            if (!user.isActive) {
                return {
                    success: false,
                    error: 'User account is inactive'
                };
            }

            // Mock password verification (in production: use bcrypt/hash verification)
            if (credentials.password === 'password123' || credentials.password === 'admin') {
                const session = this.createSession(user.id);
                
                // Update user last login
                const updatedUser = {
                    ...user,
                    lastLogin: new Date()
                };
                this.users.set(user.id, updatedUser);
                
                console.log(`[AUTH LOGIN] ✓ User authenticated successfully: ${user.username}`);
                
                return {
                    success: true,
                    user: updatedUser,
                    session
                };
            }

            return {
                success: false,
                error: 'Invalid credentials'
            };

        } catch (error) {
            console.error('[AUTH LOGIN] Authentication failed:', error);
            return {
                success: false,
                error: 'Authentication service error'
            };
        }
    }

    /**
     * Create Authentication Session
     */
    private createSession(userId: UserId): AuthSession {
        const sessionId = this.generateSessionId();
        const token = this.generateToken();
        const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours

        const session: AuthSession = {
            id: sessionId,
            userId,
            token,
            expiresAt,
            createdAt: new Date()
        };

        this.activeSessions.set(sessionId, session);
        this.validTokens.add(token);

        return session;
    }

    /**
     * Validate Session Token
     */
    async validateToken(token: string): Promise<{ valid: boolean; user?: User }> {
        try {
            console.log('[AUTH VALIDATE] Validating token...');
            
            if (!this.validTokens.has(token)) {
                return { valid: false };
            }

            const session = Array.from(this.activeSessions.values()).find(s => s.token === token);
            if (!session) {
                return { valid: false };
            }

            if (session.expiresAt < new Date()) {
                console.log('[AUTH VALIDATE] Token expired, removing session');
                this.removeSession(session.id);
                return { valid: false };
            }

            const user = this.users.get(session.userId);
            if (!user || !user.isActive) {
                return { valid: false };
            }

            console.log('[AUTH VALIDATE] ✓ Token valid');
            return { valid: true, user };

        } catch (error) {
            console.error('[AUTH VALIDATE] Token validation failed:', error);
            return { valid: false };
        }
    }

    /**
     * Check User Permissions
     */
    async checkPermission(userId: UserId, requiredPermission: string): Promise<boolean> {
        const user = this.users.get(userId);
        if (!user || !user.isActive) {
            return false;
        }

        return user.permissions.includes(requiredPermission as PermissionId);
    }

    /**
     * Logout User Session
     */
    async logout(sessionId: SessionId): Promise<boolean> {
        try {
            console.log(`[AUTH LOGOUT] Logging out session: ${sessionId}`);
            
            const removed = this.removeSession(sessionId);
            
            if (removed) {
                console.log(`[AUTH LOGOUT] ✓ Successfully logged out: ${sessionId}`);
            }
            
            return removed;

        } catch (error) {
            console.error('[AUTH LOGOUT] Logout failed:', error);
            return false;
        }
    }

    /**
     * Remove Session
     */
    private removeSession(sessionId: SessionId): boolean {
        const session = this.activeSessions.get(sessionId);
        if (!session) {
            return false;
        }

        this.validTokens.delete(session.token);
        this.activeSessions.delete(sessionId);
        return true;
    }

    /**
     * Get Active Session Count
     */
    async getActiveSessionCount(): Promise<number> {
        // Clean expired sessions
        const now = new Date();
        for (const [sessionId, session] of this.activeSessions.entries()) {
            if (session.expiresAt < now) {
                this.removeSession(sessionId);
            }
        }

        return this.activeSessions.size;
    }

    /**
     * Health check nach Architecture Pattern
     */
    async healthCheck(): Promise<boolean> {
        try {
            console.log('[AUTH HEALTH] Checking authentication health nach Clean Architecture...');
            
            const sessionCount = await this.getActiveSessionCount();
            const userCount = this.users.size;
            
            const isHealthy = userCount > 0;
            
            if (!isHealthy) {
                console.error('[AUTH HEALTH] No users configured');
                return false;
            }

            console.log(`[AUTH HEALTH] ✓ Authentication service health validated (${userCount} users, ${sessionCount} active sessions)`);
            return true;
            
        } catch (error) {
            console.error('[AUTH HEALTH] Authentication health check failed:', error);
            return false;
        }
    }

    // Helper methods
    private generateSessionId(): SessionId {
        const id = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id as SessionId;
    }

    private generateToken(): string {
        return 'token_' + Date.now() + '_' + Math.random().toString(36).substr(2, 15);
    }
}

/**
 * Register Authentication Service in DI Container nach Clean Architecture
 */
export function registerAuthenticationService(): void {
    console.log('[AUTH REGISTRATION] Registering Authentication Service nach Clean Architecture...');
    
    DIContainer.register('AuthenticationService', new AuthenticationService(), {
        singleton: true,
        dependencies: []
    });
    
    console.log('[AUTH REGISTRATION] ✅ Authentication Service registered successfully nach Clean Architecture');
}
