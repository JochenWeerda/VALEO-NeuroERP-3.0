import { FastifyReply, FastifyRequest } from 'fastify';
import { getJWTAuthenticator } from '../../infra/security/jwt';

export interface PermissionRequirement {
  roles?: readonly string[];
  permissions?: readonly string[];
  requireAll?: boolean; // If true, user must have ALL permissions/roles, otherwise ANY
}

export function requirePermissions(requirements: PermissionRequirement) {
  return async function rbacMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<void> {
    if (!request.auth) {
      return reply.code(401).send({
        error: 'Unauthorized',
        message: 'Authentication required',
      });
    }

    const { user } = request.auth;
    const authenticator = getJWTAuthenticator();

    // Check roles
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

    // Check permissions
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

// Predefined permission requirements for common operations
export const Permissions = {
  // Schedule management
  CREATE_SCHEDULE: { permissions: ['schedules:create'] },
  READ_SCHEDULE: { permissions: ['schedules:read'] },
  UPDATE_SCHEDULE: { permissions: ['schedules:update'] },
  DELETE_SCHEDULE: { permissions: ['schedules:delete'] },
  EXECUTE_SCHEDULE: { permissions: ['schedules:execute'] },

  // Admin operations
  ADMIN_SCHEDULES: { roles: ['admin', 'scheduler-admin'] },
  VIEW_ALL_SCHEDULES: { permissions: ['schedules:read-all'] },

  // Worker management
  MANAGE_WORKERS: { permissions: ['workers:manage'] },
  VIEW_WORKERS: { permissions: ['workers:read'] },
} as const;

// Convenience functions for common permission checks
export const requireScheduleRead = requirePermissions(Permissions.READ_SCHEDULE);
export const requireScheduleWrite = requirePermissions(Permissions.UPDATE_SCHEDULE);
export const requireScheduleCreate = requirePermissions(Permissions.CREATE_SCHEDULE);
export const requireScheduleDelete = requirePermissions(Permissions.DELETE_SCHEDULE);
export const requireAdminAccess = requirePermissions(Permissions.ADMIN_SCHEDULES);