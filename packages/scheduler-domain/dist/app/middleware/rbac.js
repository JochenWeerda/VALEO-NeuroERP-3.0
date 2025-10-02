"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requireAdminAccess = exports.requireScheduleDelete = exports.requireScheduleCreate = exports.requireScheduleWrite = exports.requireScheduleRead = exports.Permissions = void 0;
exports.requirePermissions = requirePermissions;
const jwt_1 = require("../../infra/security/jwt");
function requirePermissions(requirements) {
    return async function rbacMiddleware(request, reply) {
        if (!request.auth) {
            return reply.code(401).send({
                error: 'Unauthorized',
                message: 'Authentication required',
            });
        }
        const { user } = request.auth;
        const authenticator = (0, jwt_1.getJWTAuthenticator)();
        if (requirements.roles && requirements.roles.length > 0) {
            const hasRequiredRoles = requirements.requireAll
                ? requirements.roles.every(role => authenticator.hasRole(user, role))
                : requirements.roles.some(role => authenticator.hasRole(user, role));
            if (!hasRequiredRoles) {
                return reply.code(403).send({
                    error: 'Forbidden',
                    message: 'Insufficient role permissions',
                    required: requirements.roles,
                });
            }
        }
        if (requirements.permissions && requirements.permissions.length > 0) {
            const hasRequiredPermissions = requirements.requireAll
                ? requirements.permissions.every(perm => authenticator.hasPermission(user, perm))
                : requirements.permissions.some(perm => authenticator.hasPermission(user, perm));
            if (!hasRequiredPermissions) {
                return reply.code(403).send({
                    error: 'Forbidden',
                    message: 'Insufficient permissions',
                    required: requirements.permissions,
                });
            }
        }
    };
}
exports.Permissions = {
    CREATE_SCHEDULE: { permissions: ['schedules:create'] },
    READ_SCHEDULE: { permissions: ['schedules:read'] },
    UPDATE_SCHEDULE: { permissions: ['schedules:update'] },
    DELETE_SCHEDULE: { permissions: ['schedules:delete'] },
    EXECUTE_SCHEDULE: { permissions: ['schedules:execute'] },
    ADMIN_SCHEDULES: { roles: ['admin', 'scheduler-admin'] },
    VIEW_ALL_SCHEDULES: { permissions: ['schedules:read-all'] },
    MANAGE_WORKERS: { permissions: ['workers:manage'] },
    VIEW_WORKERS: { permissions: ['workers:read'] },
};
exports.requireScheduleRead = requirePermissions(exports.Permissions.READ_SCHEDULE);
exports.requireScheduleWrite = requirePermissions(exports.Permissions.UPDATE_SCHEDULE);
exports.requireScheduleCreate = requirePermissions(exports.Permissions.CREATE_SCHEDULE);
exports.requireScheduleDelete = requirePermissions(exports.Permissions.DELETE_SCHEDULE);
exports.requireAdminAccess = requirePermissions(exports.Permissions.ADMIN_SCHEDULES);
//# sourceMappingURL=rbac.js.map