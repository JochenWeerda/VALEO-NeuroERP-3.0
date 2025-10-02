"use strict";
/**
 * Authentication Service - MSOA Implementation nach Clean Architecture
 * Application Layer Service für VALEO-NeuroERP-3.0
 * Migrated from VALEO-NeuroERP-2.0 with Architecture Integrity preservation
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthenticationService = void 0;
exports.registerAuthenticationService = registerAuthenticationService;
const di_container_1 = require("@valero-neuroerp/utilities/src/di-container");
// ===== AUTHENTICATION SERVICE nach CRM Pattern =====
class AuthenticationService {
    activeSessions = new Map();
    users = new Map();
    validTokens = new Set();
    constructor() {
        console.log('[AUTH SERVICE] Initializing Authentication Service nach Architecture guidelines...');
        this.initializeAuthService();
    }
    /**
     * Initialize Authentication Service
     */
    initializeAuthService() {
        console.log('[AUTH INIT] Initializing authentication nach Clean Architecture...');
        try {
            this.setupDefaultUsers();
            console.log('[AUTH INIT] ✓ Authentication service initialized nach Clean Architecture');
        }
        catch (error) {
            console.error('[AUTH INIT] Authentication initialization failed:', error);
            throw new Error(`Authentication configuration failed: ${error}`);
        }
    }
    /**
     * Setup Default Users nach Business Requirements
     */
    setupDefaultUsers() {
        console.log('[AUTH SETUP] Setting up default users nach business model...');
        // Architecture: Create system users with appropriate permissions
        const defaultUsers = [
            {
                id: 'admin_001',
                username: 'admin',
                email: 'admin@valeo-neuroerp.com',
                roles: ['administrator'],
                permissions: ['READ', 'WRITE', 'DELETE', 'MANAGE_USERS'],
                isActive: true
            },
            {
                id: 'manager_001',
                username: 'manager',
                email: 'manager@valeo-neuroerp.com',
                roles: ['manager'],
                permissions: ['READ', 'WRITE'],
                isActive: true
            },
            {
                id: 'user_001',
                username: 'user',
                email: 'user@valeo-neuroerp.com',
                roles: ['user'],
                permissions: ['READ'],
                isActive: true
            }
        ];
        for (const userData of defaultUsers) {
            const user = {
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
    async authenticate(credentials) {
        try {
            console.log(`[AUTH LOGIN] Authenticating user: ${credentials.username}`);
            // Find user by username
            const user = Array.from(this.users.values()).find(u => u.username === credentials.username);
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
        }
        catch (error) {
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
    createSession(userId) {
        const sessionId = this.generateSessionId();
        const token = this.generateToken();
        const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours
        const session = {
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
    async validateToken(token) {
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
        }
        catch (error) {
            console.error('[AUTH VALIDATE] Token validation failed:', error);
            return { valid: false };
        }
    }
    /**
     * Check User Permissions
     */
    async checkPermission(userId, requiredPermission) {
        const user = this.users.get(userId);
        if (!user || !user.isActive) {
            return false;
        }
        return user.permissions.includes(requiredPermission);
    }
    /**
     * Logout User Session
     */
    async logout(sessionId) {
        try {
            console.log(`[AUTH LOGOUT] Logging out session: ${sessionId}`);
            const removed = this.removeSession(sessionId);
            if (removed) {
                console.log(`[AUTH LOGOUT] ✓ Successfully logged out: ${sessionId}`);
            }
            return removed;
        }
        catch (error) {
            console.error('[AUTH LOGOUT] Logout failed:', error);
            return false;
        }
    }
    /**
     * Remove Session
     */
    removeSession(sessionId) {
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
    async getActiveSessionCount() {
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
    async healthCheck() {
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
        }
        catch (error) {
            console.error('[AUTH HEALTH] Authentication health check failed:', error);
            return false;
        }
    }
    // Helper methods
    generateSessionId() {
        const id = 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        return id;
    }
    generateToken() {
        return 'token_' + Date.now() + '_' + Math.random().toString(36).substr(2, 15);
    }
}
exports.AuthenticationService = AuthenticationService;
/**
 * Register Authentication Service in DI Container nach Clean Architecture
 */
function registerAuthenticationService() {
    console.log('[AUTH REGISTRATION] Registering Authentication Service nach Clean Architecture...');
    di_container_1.DIContainer.register('AuthenticationService', new AuthenticationService(), {
        singleton: true,
        dependencies: []
    });
    console.log('[AUTH REGISTRATION] ✅ Authentication Service registered successfully nach Clean Architecture');
}
//# sourceMappingURL=auth-service.js.map