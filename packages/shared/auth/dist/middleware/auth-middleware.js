"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthMiddleware = void 0;
exports.getUserFromRequest = getUserFromRequest;
exports.hasPermission = hasPermission;
class AuthMiddleware {
    constructor(jwtValidator, rbacPolicy, tenantContext) {
        this.jwtValidator = jwtValidator;
        this.rbacPolicy = rbacPolicy;
        this.tenantContext = tenantContext;
    }
    /**
     * Express middleware for authentication and authorization
     */
    middleware(options = {}) {
        const defaultOptions = {
            requireAuth: false,
            requireTenant: false,
            tokenHeader: 'authorization',
            tenantHeader: 'x-tenant-id',
            ...options
        };
        return async (req, res, next) => {
            try {
                // Extract token from header
                const authHeader = req.headers[defaultOptions.tokenHeader];
                if (!authHeader && defaultOptions.requireAuth) {
                    res.status(401).json({
                        error: 'Authentication required',
                        code: 'MISSING_TOKEN'
                    });
                    return;
                }
                let user = null;
                // Validate JWT if token provided
                if (authHeader) {
                    const token = authHeader.replace('Bearer ', '');
                    user = await this.jwtValidator.validateToken(token);
                    // Set user context in request
                    req.user = user;
                    // Validate tenant context
                    const requestedTenantId = req.headers[defaultOptions.tenantHeader];
                    if (defaultOptions.requireTenant && !this.tenantContext.validateTenantContext(user, requestedTenantId)) {
                        res.status(403).json({
                            error: 'Tenant access denied',
                            code: 'TENANT_MISMATCH'
                        });
                        return;
                    }
                }
                // Check role requirements
                if (defaultOptions.requireRoles && user) {
                    const hasRequiredRole = defaultOptions.requireRoles.some(role => user.roles.includes(role));
                    if (!hasRequiredRole) {
                        res.status(403).json({
                            error: 'Insufficient role permissions',
                            code: 'INSUFFICIENT_ROLE',
                            required: defaultOptions.requireRoles,
                            userRoles: user.roles
                        });
                        return;
                    }
                }
                // Check permission requirements
                if (defaultOptions.requirePermissions && user) {
                    for (const permission of defaultOptions.requirePermissions) {
                        const [resource, action] = permission.split(':');
                        const policyResult = this.rbacPolicy.canAccess(user, resource, action);
                        if (!policyResult.allowed) {
                            res.status(403).json({
                                error: 'Insufficient permissions',
                                code: 'INSUFFICIENT_PERMISSIONS',
                                required: permission,
                                reason: policyResult.reason
                            });
                            return;
                        }
                    }
                }
                next();
            }
            catch (error) {
                const message = error instanceof Error ? error.message : 'Authentication failed';
                res.status(401).json({
                    error: message,
                    code: 'AUTHENTICATION_FAILED'
                });
            }
        };
    }
    /**
     * Middleware factory for different auth levels
     */
    static createMiddleware(jwtValidator, rbacPolicy, tenantContext) {
        const authMiddleware = new AuthMiddleware(jwtValidator, rbacPolicy, tenantContext);
        return {
            requireAuth: (options) => authMiddleware.middleware({ ...options, requireAuth: true }),
            optionalAuth: (options) => authMiddleware.middleware({ ...options, requireAuth: false }),
            requireRoles: (roles, options) => authMiddleware.middleware({ ...options, requireAuth: true, requireRoles: roles }),
            requirePermissions: (permissions, options) => authMiddleware.middleware({ ...options, requireAuth: true, requirePermissions: permissions })
        };
    }
}
exports.AuthMiddleware = AuthMiddleware;
/**
 * Helper function to extract user from request
 */
function getUserFromRequest(req) {
    return req.user || null;
}
/**
 * Helper function to check if user has permission
 */
function hasPermission(rbacPolicy, req, resource, action) {
    const user = getUserFromRequest(req);
    if (!user)
        return false;
    const result = rbacPolicy.canAccess(user, resource, action);
    return result.allowed;
}
//# sourceMappingURL=auth-middleware.js.map