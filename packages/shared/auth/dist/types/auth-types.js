"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthMiddlewareOptions = exports.JWKS = exports.AuthErrorType = exports.PolicyResult = exports.Permission = exports.Role = exports.UserContext = exports.JWTPayload = void 0;
const zod_1 = require("zod");
// Authentication and Authorization Types
// JWT Payload structure
exports.JWTPayload = zod_1.z.object({
    sub: zod_1.z.string(), // Subject (user ID)
    tenantId: zod_1.z.string(),
    email: zod_1.z.string().email(),
    roles: zod_1.z.array(zod_1.z.string()),
    permissions: zod_1.z.array(zod_1.z.string()),
    iat: zod_1.z.number(), // Issued at
    exp: zod_1.z.number(), // Expires at
    iss: zod_1.z.string(), // Issuer
    aud: zod_1.z.string() // Audience
});
// User context for authenticated requests
exports.UserContext = zod_1.z.object({
    userId: zod_1.z.string(),
    tenantId: zod_1.z.string(),
    email: zod_1.z.string().email(),
    roles: zod_1.z.array(zod_1.z.string()),
    permissions: zod_1.z.array(zod_1.z.string()),
    token: zod_1.z.string(),
    expiresAt: zod_1.z.number()
});
// Role definition
exports.Role = zod_1.z.object({
    id: zod_1.z.string(),
    name: zod_1.z.string(),
    description: zod_1.z.string().optional(),
    permissions: zod_1.z.array(zod_1.z.string()),
    isActive: zod_1.z.boolean().default(true)
});
// Permission structure
exports.Permission = zod_1.z.object({
    resource: zod_1.z.string(), // e.g., "shipment", "order", "customer"
    action: zod_1.z.enum(['create', 'read', 'update', 'delete', 'manage']),
    scope: zod_1.z.string().optional(), // e.g., "own", "tenant", "all"
    conditions: zod_1.z.record(zod_1.z.any()).optional() // Additional conditions
});
// Policy evaluation result
exports.PolicyResult = zod_1.z.object({
    allowed: zod_1.z.boolean(),
    reason: zod_1.z.string().optional(),
    conditions: zod_1.z.record(zod_1.z.any()).optional()
});
// Authentication error types
exports.AuthErrorType = zod_1.z.enum([
    'INVALID_TOKEN',
    'EXPIRED_TOKEN',
    'INSUFFICIENT_PERMISSIONS',
    'TENANT_MISMATCH',
    'USER_NOT_FOUND',
    'ROLE_NOT_FOUND'
]);
// JWKS (JSON Web Key Set) structure
exports.JWKS = zod_1.z.object({
    keys: zod_1.z.array(zod_1.z.object({
        kty: zod_1.z.string(),
        use: zod_1.z.string(),
        kid: zod_1.z.string(),
        n: zod_1.z.string(),
        e: zod_1.z.string(),
        alg: zod_1.z.string()
    }))
});
// Authentication middleware options
exports.AuthMiddlewareOptions = zod_1.z.object({
    requireAuth: zod_1.z.boolean().default(true),
    requireRoles: zod_1.z.array(zod_1.z.string()).optional(),
    requirePermissions: zod_1.z.array(zod_1.z.string()).optional(),
    requireTenant: zod_1.z.boolean().default(true),
    tokenHeader: zod_1.z.string().default('authorization'),
    tenantHeader: zod_1.z.string().default('x-tenant-id')
});
//# sourceMappingURL=auth-types.js.map