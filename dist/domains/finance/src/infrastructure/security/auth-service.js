"use strict";
var __esDecorate = (this && this.__esDecorate) || function (ctor, descriptorIn, decorators, contextIn, initializers, extraInitializers) {
    function accept(f) { if (f !== void 0 && typeof f !== "function") throw new TypeError("Function expected"); return f; }
    var kind = contextIn.kind, key = kind === "getter" ? "get" : kind === "setter" ? "set" : "value";
    var target = !descriptorIn && ctor ? contextIn["static"] ? ctor : ctor.prototype : null;
    var descriptor = descriptorIn || (target ? Object.getOwnPropertyDescriptor(target, contextIn.name) : {});
    var _, done = false;
    for (var i = decorators.length - 1; i >= 0; i--) {
        var context = {};
        for (var p in contextIn) context[p] = p === "access" ? {} : contextIn[p];
        for (var p in contextIn.access) context.access[p] = contextIn.access[p];
        context.addInitializer = function (f) { if (done) throw new TypeError("Cannot add initializers after decoration has completed"); extraInitializers.push(accept(f || null)); };
        var result = (0, decorators[i])(kind === "accessor" ? { get: descriptor.get, set: descriptor.set } : descriptor[key], context);
        if (kind === "accessor") {
            if (result === void 0) continue;
            if (result === null || typeof result !== "object") throw new TypeError("Object expected");
            if (_ = accept(result.get)) descriptor.get = _;
            if (_ = accept(result.set)) descriptor.set = _;
            if (_ = accept(result.init)) initializers.unshift(_);
        }
        else if (_ = accept(result)) {
            if (kind === "field") initializers.unshift(_);
            else descriptor[key] = _;
        }
    }
    if (target) Object.defineProperty(target, contextIn.name, descriptor);
    done = true;
};
var __runInitializers = (this && this.__runInitializers) || function (thisArg, initializers, value) {
    var useValue = arguments.length > 2;
    for (var i = 0; i < initializers.length; i++) {
        value = useValue ? initializers[i].call(thisArg, value) : initializers[i].call(thisArg);
    }
    return useValue ? value : void 0;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthService = exports.PermissionAction = exports.UserRole = void 0;
const inversify_1 = require("inversify");
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const bcrypt_1 = __importDefault(require("bcrypt"));
const crypto_1 = __importDefault(require("crypto"));
const metrics_service_1 = require("../observability/metrics-service");
var UserRole;
(function (UserRole) {
    UserRole["ADMIN"] = "admin";
    UserRole["ACCOUNTANT"] = "accountant";
    UserRole["AUDITOR"] = "auditor";
    UserRole["MANAGER"] = "manager";
    UserRole["VIEWER"] = "viewer";
})(UserRole || (exports.UserRole = UserRole = {}));
var PermissionAction;
(function (PermissionAction) {
    PermissionAction["CREATE"] = "create";
    PermissionAction["READ"] = "read";
    PermissionAction["UPDATE"] = "update";
    PermissionAction["DELETE"] = "delete";
    PermissionAction["APPROVE"] = "approve";
    PermissionAction["EXPORT"] = "export";
})(PermissionAction || (exports.PermissionAction = PermissionAction = {}));
let AuthService = (() => {
    let _classDecorators = [(0, inversify_1.injectable)()];
    let _classDescriptor;
    let _classExtraInitializers = [];
    let _classThis;
    var AuthService = class {
        static { _classThis = this; }
        static {
            const _metadata = typeof Symbol === "function" && Symbol.metadata ? Object.create(null) : void 0;
            __esDecorate(null, _classDescriptor = { value: _classThis }, _classDecorators, { kind: "class", name: _classThis.name, metadata: _metadata }, null, _classExtraInitializers);
            AuthService = _classThis = _classDescriptor.value;
            if (_metadata) Object.defineProperty(_classThis, Symbol.metadata, { enumerable: true, configurable: true, writable: true, value: _metadata });
            __runInitializers(_classThis, _classExtraInitializers);
        }
        jwtSecret;
        jwtRefreshSecret;
        bcryptRounds;
        metrics = metrics_service_1.MetricsService.getInstance();
        // In-memory user store (in production, use database)
        users = new Map();
        refreshTokens = new Set();
        constructor() {
            this.jwtSecret = process.env.JWT_SECRET || 'your-secret-key';
            this.jwtRefreshSecret = process.env.JWT_REFRESH_SECRET || 'your-refresh-secret';
            this.bcryptRounds = parseInt(process.env.BCRYPT_ROUNDS || '12');
            // Initialize with default admin user
            this.initializeDefaultUsers();
        }
        async initializeDefaultUsers() {
            const adminUser = {
                id: 'admin-001',
                email: 'admin@finance.valero-neuroerp.com',
                roles: [UserRole.ADMIN],
                permissions: this.getPermissionsForRoles([UserRole.ADMIN]),
                tenantId: 'default',
                isActive: true,
                mfaEnabled: false
            };
            const hashedPassword = await bcrypt_1.default.hash('Admin123!', this.bcryptRounds);
            this.users.set(adminUser.email, adminUser);
            // In production, store hashed password in database
        }
        getPermissionsForRoles(roles) {
            const permissions = [];
            for (const role of roles) {
                switch (role) {
                    case UserRole.ADMIN:
                        permissions.push('ledger:*', 'invoice:*', 'tax:*', 'audit:*', 'forecast:*', 'user:*', 'system:*');
                        break;
                    case UserRole.ACCOUNTANT:
                        permissions.push('ledger:create', 'ledger:read', 'ledger:update', 'invoice:create', 'invoice:read', 'invoice:update', 'tax:read', 'forecast:read');
                        break;
                    case UserRole.AUDITOR:
                        permissions.push('ledger:read', 'invoice:read', 'tax:read', 'audit:read', 'audit:export');
                        break;
                    case UserRole.MANAGER:
                        permissions.push('ledger:read', 'invoice:read', 'invoice:approve', 'tax:read', 'forecast:read', 'report:read');
                        break;
                    case UserRole.VIEWER:
                        permissions.push('ledger:read', 'invoice:read', 'tax:read', 'forecast:read');
                        break;
                }
            }
            return [...new Set(permissions)]; // Remove duplicates
        }
        async authenticate(credentials) {
            const startTime = Date.now();
            try {
                const user = this.users.get(credentials.email);
                if (!user || !user.isActive) {
                    this.metrics.incrementErrorCount('authentication', 'invalid_credentials');
                    throw new Error('Invalid credentials');
                }
                // In production, verify password hash from database
                const isValidPassword = await bcrypt_1.default.compare(credentials.password, 'hashed-password-placeholder');
                if (!isValidPassword) {
                    this.metrics.incrementErrorCount('authentication', 'invalid_credentials');
                    throw new Error('Invalid credentials');
                }
                // Check MFA if enabled
                if (user.mfaEnabled) {
                    if (!credentials.mfaCode) {
                        throw new Error('MFA code required');
                    }
                    // Verify MFA code (implementation depends on MFA provider)
                    const isValidMFA = await this.verifyMFACode(user.id, credentials.mfaCode);
                    if (!isValidMFA) {
                        this.metrics.incrementErrorCount('authentication', 'invalid_mfa');
                        throw new Error('Invalid MFA code');
                    }
                }
                // Update last login
                user.lastLogin = new Date();
                // Generate tokens
                const token = this.generateAccessToken(user);
                const refreshToken = this.generateRefreshToken(user);
                this.refreshTokens.add(refreshToken);
                this.metrics.recordApiResponseTime('POST', '/auth/login', 200, (Date.now() - startTime) / 1000);
                return {
                    accessToken: token,
                    refreshToken,
                    expiresIn: 3600, // 1 hour
                    tokenType: 'Bearer'
                };
            }
            catch (error) {
                this.metrics.incrementErrorCount('authentication', 'login_failed');
                throw error;
            }
        }
        async refreshToken(refreshToken) {
            try {
                if (!this.refreshTokens.has(refreshToken)) {
                    throw new Error('Invalid refresh token');
                }
                const decoded = jsonwebtoken_1.default.verify(refreshToken, this.jwtRefreshSecret);
                const user = this.users.get(decoded.email);
                if (!user || !user.isActive) {
                    throw new Error('User not found or inactive');
                }
                // Remove old refresh token
                this.refreshTokens.delete(refreshToken);
                // Generate new tokens
                const newToken = this.generateAccessToken(user);
                const newRefreshToken = this.generateRefreshToken(user);
                this.refreshTokens.add(newRefreshToken);
                return {
                    accessToken: newToken,
                    refreshToken: newRefreshToken,
                    expiresIn: 3600,
                    tokenType: 'Bearer'
                };
            }
            catch (error) {
                this.metrics.incrementErrorCount('authentication', 'token_refresh_failed');
                throw error;
            }
        }
        async logout(refreshToken) {
            this.refreshTokens.delete(refreshToken);
        }
        verifyAccessToken(token) {
            try {
                const decoded = jsonwebtoken_1.default.verify(token, this.jwtSecret);
                const user = this.users.get(decoded.email);
                return user || null;
            }
            catch (error) {
                return null;
            }
        }
        hasPermission(user, resource, action) {
            // Check if user has wildcard permission for resource
            if (user.permissions.includes(`${resource}:*`)) {
                return true;
            }
            // Check specific permission
            return user.permissions.includes(`${resource}:${action}`);
        }
        hasRole(user, role) {
            return user.roles.includes(role);
        }
        generateAccessToken(user) {
            return jsonwebtoken_1.default.sign({
                sub: user.id,
                email: user.email,
                roles: user.roles,
                permissions: user.permissions,
                tenantId: user.tenantId
            }, this.jwtSecret, { expiresIn: '1h' });
        }
        generateRefreshToken(user) {
            return jsonwebtoken_1.default.sign({
                sub: user.id,
                email: user.email
            }, this.jwtRefreshSecret, { expiresIn: '7d' });
        }
        async verifyMFACode(userId, code) {
            // Implementation depends on MFA provider (e.g., TOTP, SMS, etc.)
            // For now, return true for any 6-digit code
            return /^\d{6}$/.test(code);
        }
        // User management methods
        async createUser(userData) {
            const user = {
                ...userData,
                id: crypto_1.default.randomUUID(),
                permissions: this.getPermissionsForRoles(userData.roles)
            };
            this.users.set(user.email, user);
            return user;
        }
        getUserById(id) {
            for (const user of this.users.values()) {
                if (user.id === id) {
                    return user;
                }
            }
            return null;
        }
        getUserByEmail(email) {
            return this.users.get(email) || null;
        }
        async updateUser(id, updates) {
            const user = this.getUserById(id);
            if (!user) {
                return null;
            }
            Object.assign(user, updates);
            // Recalculate permissions if roles changed
            if (updates.roles) {
                user.permissions = this.getPermissionsForRoles(updates.roles);
            }
            return user;
        }
        async deleteUser(id) {
            const user = this.getUserById(id);
            if (!user) {
                return false;
            }
            this.users.delete(user.email);
            return true;
        }
    };
    return AuthService = _classThis;
})();
exports.AuthService = AuthService;
exports.default = AuthService;
