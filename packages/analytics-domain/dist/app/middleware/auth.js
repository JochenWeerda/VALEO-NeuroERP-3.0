"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.adminOnlyMiddleware = exports.analyticsAuthMiddleware = exports.requireCubeAdminAccess = exports.requireCubeReadAccess = exports.requireForecastAdminAccess = exports.requireForecastWriteAccess = exports.requireForecastReadAccess = exports.requireReportAdminAccess = exports.requireReportWriteAccess = exports.requireReportReadAccess = exports.requireKpiAdminAccess = exports.requireKpiWriteAccess = exports.requireKpiReadAccess = exports.analyticsPermissions = void 0;
exports.authMiddleware = authMiddleware;
exports.requireRoles = requireRoles;
exports.requirePermissions = requirePermissions;
exports.tenantIsolationMiddleware = tenantIsolationMiddleware;
const jwt_1 = require("../../infra/security/jwt");
async function authMiddleware(request, reply) {
    try {
        const authHeader = request.headers.authorization;
        if (!authHeader || !authHeader.startsWith('Bearer ')) {
            return reply.code(401).send({
                error: 'Unauthorized',
                message: 'Missing or invalid authorization header',
            });
        }
        const token = authHeader.substring(7);
        const decoded = await (0, jwt_1.verifyJWT)(token);
        const user = {
            userId: decoded.sub || decoded.userId,
            email: decoded.email,
            roles: decoded.roles || [],
            permissions: decoded.permissions || [],
            tenantId: decoded.tenantId || decoded.tenant_id,
            profile: {
                firstName: decoded.firstName || decoded.first_name,
                lastName: decoded.lastName || decoded.last_name,
                department: decoded.department,
            },
        };
        request.user = user;
        request.tenantId = user.tenantId;
    }
    catch (error) {
        console.error('Authentication error:', error);
        const message = error instanceof Error ? error.message : 'Invalid token';
        return reply.code(401).send({
            error: 'Unauthorized',
            message,
        });
    }
}
function requireRoles(requiredRoles) {
    return async (request, reply) => {
        const authRequest = request;
        if (!authRequest.user) {
            return reply.code(401).send({
                error: 'Unauthorized',
                message: 'Authentication required',
            });
        }
        const userRoles = authRequest.user.roles;
        const hasRequiredRole = requiredRoles.some(role => userRoles.includes(role));
        if (!hasRequiredRole) {
            return reply.code(403).send({
                error: 'Forbidden',
                message: 'Insufficient permissions',
                requiredRoles,
                userRoles,
            });
        }
    };
}
function requirePermissions(requiredPermissions) {
    return async (request, reply) => {
        const authRequest = request;
        if (!authRequest.user) {
            return reply.code(401).send({
                error: 'Unauthorized',
                message: 'Authentication required',
            });
        }
        const userPermissions = authRequest.user.permissions;
        const hasRequiredPermission = requiredPermissions.some(permission => userPermissions.includes(permission));
        if (!hasRequiredPermission) {
            return reply.code(403).send({
                error: 'Forbidden',
                message: 'Insufficient permissions',
                requiredPermissions,
                userPermissions,
            });
        }
    };
}
exports.analyticsPermissions = {
    VIEW_KPIS: 'analytics:kpis:read',
    CREATE_KPIS: 'analytics:kpis:create',
    UPDATE_KPIS: 'analytics:kpis:update',
    DELETE_KPIS: 'analytics:kpis:delete',
    RECALCULATE_KPIS: 'analytics:kpis:recalculate',
    VIEW_REPORTS: 'analytics:reports:read',
    CREATE_REPORTS: 'analytics:reports:create',
    DELETE_REPORTS: 'analytics:reports:delete',
    VIEW_FORECASTS: 'analytics:forecasts:read',
    CREATE_FORECASTS: 'analytics:forecasts:create',
    DELETE_FORECASTS: 'analytics:forecasts:delete',
    COMPARE_FORECASTS: 'analytics:forecasts:compare',
    VIEW_CUBES: 'analytics:cubes:read',
    REFRESH_CUBES: 'analytics:cubes:refresh',
    ADMIN_ANALYTICS: 'analytics:admin',
};
exports.requireKpiReadAccess = requirePermissions([exports.analyticsPermissions.VIEW_KPIS]);
exports.requireKpiWriteAccess = requirePermissions([exports.analyticsPermissions.CREATE_KPIS, exports.analyticsPermissions.UPDATE_KPIS]);
exports.requireKpiAdminAccess = requirePermissions([exports.analyticsPermissions.ADMIN_ANALYTICS]);
exports.requireReportReadAccess = requirePermissions([exports.analyticsPermissions.VIEW_REPORTS]);
exports.requireReportWriteAccess = requirePermissions([exports.analyticsPermissions.CREATE_REPORTS]);
exports.requireReportAdminAccess = requirePermissions([exports.analyticsPermissions.ADMIN_ANALYTICS]);
exports.requireForecastReadAccess = requirePermissions([exports.analyticsPermissions.VIEW_FORECASTS]);
exports.requireForecastWriteAccess = requirePermissions([exports.analyticsPermissions.CREATE_FORECASTS]);
exports.requireForecastAdminAccess = requirePermissions([exports.analyticsPermissions.ADMIN_ANALYTICS]);
exports.requireCubeReadAccess = requirePermissions([exports.analyticsPermissions.VIEW_CUBES]);
exports.requireCubeAdminAccess = requirePermissions([exports.analyticsPermissions.ADMIN_ANALYTICS]);
async function tenantIsolationMiddleware(request, reply) {
    const authRequest = request;
    if (!authRequest.user) {
        return reply.code(401).send({
            error: 'Unauthorized',
            message: 'Authentication required',
        });
    }
    const userTenantId = authRequest.user.tenantId;
    if (request.params && 'tenantId' in request.params) {
        const requestedTenantId = request.params.tenantId;
        if (requestedTenantId && requestedTenantId !== userTenantId) {
            return reply.code(403).send({
                error: 'Forbidden',
                message: 'Cannot access data from different tenant',
                userTenantId,
                requestedTenantId,
            });
        }
    }
    if (request.query && 'tenantId' in request.query) {
        const requestedTenantId = request.query.tenantId;
        if (requestedTenantId && requestedTenantId !== userTenantId) {
            return reply.code(403).send({
                error: 'Forbidden',
                message: 'Cannot access data from different tenant',
                userTenantId,
                requestedTenantId,
            });
        }
    }
    authRequest.tenantId = userTenantId;
}
exports.analyticsAuthMiddleware = [authMiddleware, tenantIsolationMiddleware];
exports.adminOnlyMiddleware = [
    authMiddleware,
    tenantIsolationMiddleware,
    requirePermissions([exports.analyticsPermissions.ADMIN_ANALYTICS]),
];
//# sourceMappingURL=auth.js.map