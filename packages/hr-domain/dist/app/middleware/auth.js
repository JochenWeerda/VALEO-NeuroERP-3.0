"use strict";
/**
 * Authentication Middleware for VALEO NeuroERP 3.0 HR Domain
 * JWT validation with JWKS
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.hrPermissions = void 0;
exports.initializeAuth = initializeAuth;
exports.authMiddleware = authMiddleware;
exports.requireAuth = requireAuth;
exports.requireRole = requireRole;
exports.requirePermission = requirePermission;
exports.requireHrPermission = requireHrPermission;
const jose_1 = require("jose");
const JWKS_URL = process.env.JWKS_URL || 'https://auth.example.com/.well-known/jwks.json';
const JWT_ISSUER = process.env.JWT_ISSUER || 'https://auth.example.com';
const JWT_AUDIENCE = process.env.JWT_AUDIENCE || 'hr-domain';
let jwks = null;
async function initializeAuth() {
    try {
        jwks = (0, jose_1.createRemoteJWKSet)(new URL(JWKS_URL));
        console.log('✅ Auth middleware initialized with JWKS:', JWKS_URL);
    }
    catch (error) {
        console.error('❌ Failed to initialize auth middleware:', error);
        throw error;
    }
}
async function authMiddleware(request, reply) {
    try {
        const authHeader = request.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return reply.code(401).send({ error: 'Missing or invalid authorization header' });
        }
        const token = authHeader.substring(7);
        if (!jwks) {
            await initializeAuth();
        }
        const { payload } = await (0, jose_1.jwtVerify)(token, jwks, {
            issuer: JWT_ISSUER,
            audience: JWT_AUDIENCE,
            algorithms: ['RS256', 'RS384', 'RS512']
        });
        const jwtPayload = payload;
        // Validate token expiration
        if (jwtPayload.exp && jwtPayload.exp < Math.floor(Date.now() / 1000)) {
            return reply.code(401).send({ error: 'Token expired' });
        }
        // Extract tenant ID from token or header
        const tenantId = jwtPayload.tenantId || request.headers['x-tenant-id'];
        if (!tenantId) {
            return reply.code(400).send({ error: 'Tenant ID required' });
        }
        // Set auth context
        request.auth = {
            userId: jwtPayload.sub,
            tenantId,
            roles: jwtPayload.roles || [],
            permissions: jwtPayload.permissions || [],
            token
        };
    }
    catch (error) {
        console.error('Auth middleware error:', error);
        return reply.code(401).send({ error: 'Invalid token' });
    }
}
async function requireAuth(request, reply) {
    if (!request.auth) {
        return reply.code(401).send({ error: 'Authentication required' });
    }
}
async function requireRole(roles) {
    return async (request, reply) => {
        if (!request.auth) {
            return reply.code(401).send({ error: 'Authentication required' });
        }
        const hasRole = roles.some(role => request.auth.roles.includes(role));
        if (!hasRole) {
            return reply.code(403).send({ error: 'Insufficient permissions' });
        }
    };
}
async function requirePermission(permissions) {
    return async (request, reply) => {
        if (!request.auth) {
            return reply.code(401).send({ error: 'Authentication required' });
        }
        const hasPermission = permissions.some(permission => request.auth.permissions.includes(permission) ||
            request.auth.permissions.includes('*'));
        if (!hasPermission) {
            return reply.code(403).send({ error: 'Insufficient permissions' });
        }
    };
}
// HR-specific permission checks
exports.hrPermissions = {
    EMPLOYEE_READ: 'hr:employee:read',
    EMPLOYEE_WRITE: 'hr:employee:write',
    EMPLOYEE_DELETE: 'hr:employee:delete',
    TIME_READ: 'hr:time:read',
    TIME_WRITE: 'hr:time:write',
    TIME_APPROVE: 'hr:time:approve',
    LEAVE_READ: 'hr:leave:read',
    LEAVE_WRITE: 'hr:leave:write',
    LEAVE_APPROVE: 'hr:leave:approve',
    SHIFT_READ: 'hr:shift:read',
    SHIFT_WRITE: 'hr:shift:write',
    PAYROLL_READ: 'hr:payroll:read',
    PAYROLL_WRITE: 'hr:payroll:write',
    PAYROLL_EXPORT: 'hr:payroll:export',
    ROLE_READ: 'hr:role:read',
    ROLE_WRITE: 'hr:role:write'
};
function requireHrPermission(permission) {
    return async (request, reply) => {
        if (!request.auth) {
            return reply.code(401).send({ error: 'Authentication required' });
        }
        const hasPermission = request.auth.permissions.includes(permission) ||
            request.auth.permissions.includes('*');
        if (!hasPermission) {
            return reply.code(403).send({ error: 'Insufficient permissions' });
        }
    };
}
//# sourceMappingURL=auth.js.map