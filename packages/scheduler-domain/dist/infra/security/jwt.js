"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.JWTAuthenticator = void 0;
exports.getJWTAuthenticator = getJWTAuthenticator;
exports.initializeJWTAuthenticator = initializeJWTAuthenticator;
const jose_1 = require("jose");
class JWTAuthenticator {
    options;
    jwks = null;
    constructor(options) {
        this.options = options;
    }
    async initialize() {
        this.jwks = (0, jose_1.createRemoteJWKSet)(new URL(this.options.jwksUrl));
    }
    async authenticate(token) {
        if (!this.jwks) {
            throw new Error('JWT authenticator not initialized');
        }
        try {
            const { payload } = await (0, jose_1.jwtVerify)(token, this.jwks, {
                issuer: this.options.issuer,
                audience: this.options.audience,
            });
            return this.extractUserFromPayload(payload);
        }
        catch (error) {
            throw new Error(`JWT verification failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    }
    extractUserFromPayload(payload) {
        const sub = payload.sub;
        if (!sub) {
            throw new Error('JWT missing subject claim');
        }
        return {
            sub,
            email: payload.email,
            name: payload.name,
            roles: this.extractRoles(payload),
            tenantId: payload.tenant_id || payload['x-tenant-id'],
            permissions: this.extractPermissions(payload),
        };
    }
    extractRoles(payload) {
        const roles = payload.roles || payload['cognito:groups'] || payload.groups || [];
        if (Array.isArray(roles)) {
            return roles.filter((role) => typeof role === 'string');
        }
        if (typeof roles === 'string') {
            return [roles];
        }
        return [];
    }
    extractPermissions(payload) {
        const permissions = payload.permissions;
        if (Array.isArray(permissions)) {
            return permissions.filter((perm) => typeof perm === 'string');
        }
        const scope = payload.scope;
        if (typeof scope === 'string') {
            return scope.split(' ').filter(Boolean);
        }
        return [];
    }
    hasRole(user, requiredRole) {
        return user.roles?.includes(requiredRole) ?? false;
    }
    hasPermission(user, requiredPermission) {
        return user.permissions?.includes(requiredPermission) ?? false;
    }
    hasAnyRole(user, requiredRoles) {
        return requiredRoles.some(role => this.hasRole(user, role));
    }
    hasAnyPermission(user, requiredPermissions) {
        return requiredPermissions.some(permission => this.hasPermission(user, permission));
    }
}
exports.JWTAuthenticator = JWTAuthenticator;
let globalAuthenticator = null;
function getJWTAuthenticator() {
    if (!globalAuthenticator) {
        const jwksUrl = process.env.JWKS_URL || 'https://auth.example.com/.well-known/jwks.json';
        globalAuthenticator = new JWTAuthenticator({
            jwksUrl,
            issuer: process.env.JWT_ISSUER,
            audience: process.env.JWT_AUDIENCE,
        });
    }
    return globalAuthenticator;
}
async function initializeJWTAuthenticator() {
    const authenticator = getJWTAuthenticator();
    await authenticator.initialize();
}
//# sourceMappingURL=jwt.js.map