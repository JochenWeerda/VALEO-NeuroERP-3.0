import { FastifyRequest, FastifyReply } from 'fastify';
import { verifyJWT } from '../../infra/security/jwt';

export interface AuthenticatedUser {
  userId: string;
  email: string;
  roles: string[];
  permissions: string[];
  tenantId: string;
  profile: {
    firstName?: string;
    lastName?: string;
    department?: string;
  };
}

export interface AuthenticatedRequest extends FastifyRequest {
  user: AuthenticatedUser;
  tenantId: string;
}

// JWT Authentication middleware
export async function authMiddleware(request: FastifyRequest, reply: FastifyReply) {
  try {
    const authHeader = request.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return reply.code(401).send({
        error: 'Unauthorized',
        message: 'Missing or invalid authorization header',
      });
    }

    const token = authHeader.substring(7); // Remove 'Bearer ' prefix

    // Verify JWT token
    const decoded = await verifyJWT(token);

    // Extract user information from token
    const user: AuthenticatedUser = {
      userId: decoded.sub || decoded.userId,
      email: decoded.email || 'unknown@example.com',
      roles: decoded.roles || [],
      permissions: decoded.permissions || [],
      tenantId: decoded.tenantId || decoded.tenant_id,
      profile: {
        firstName: decoded.firstName || decoded.first_name,
        lastName: decoded.lastName || decoded.last_name,
        department: decoded.department,
      },
    };

    // Attach user to request
    (request as AuthenticatedRequest).user = user;
    (request as AuthenticatedRequest).tenantId = user.tenantId;

  } catch (error) {
    console.error('Authentication error:', error);

    const message = error instanceof Error ? error.message : 'Invalid token';

    return reply.code(401).send({
      error: 'Unauthorized',
      message,
    });
  }
}

// Role-based access control middleware
export function requireRoles(requiredRoles: string[]) {
  return async (request: FastifyRequest, reply: FastifyReply) => {
    const authRequest = request as AuthenticatedRequest;

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

// Permission-based access control middleware
export function requirePermissions(requiredPermissions: string[]) {
  return async (request: FastifyRequest, reply: FastifyReply) => {
    const authRequest = request as AuthenticatedRequest;

    if (!authRequest.user) {
      return reply.code(401).send({
        error: 'Unauthorized',
        message: 'Authentication required',
      });
    }

    const userPermissions = authRequest.user.permissions;
    const hasRequiredPermission = requiredPermissions.some(permission =>
      userPermissions.includes(permission)
    );

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

// Analytics-specific permission middleware
export const analyticsPermissions = {
  // KPI permissions
  VIEW_KPIS: 'analytics:kpis:read',
  CREATE_KPIS: 'analytics:kpis:create',
  UPDATE_KPIS: 'analytics:kpis:update',
  DELETE_KPIS: 'analytics:kpis:delete',
  RECALCULATE_KPIS: 'analytics:kpis:recalculate',

  // Report permissions
  VIEW_REPORTS: 'analytics:reports:read',
  CREATE_REPORTS: 'analytics:reports:create',
  DELETE_REPORTS: 'analytics:reports:delete',

  // Forecast permissions
  VIEW_FORECASTS: 'analytics:forecasts:read',
  CREATE_FORECASTS: 'analytics:forecasts:create',
  DELETE_FORECASTS: 'analytics:forecasts:delete',
  COMPARE_FORECASTS: 'analytics:forecasts:compare',

  // Cube permissions
  VIEW_CUBES: 'analytics:cubes:read',
  REFRESH_CUBES: 'analytics:cubes:refresh',

  // Admin permissions
  ADMIN_ANALYTICS: 'analytics:admin',
};

// Pre-configured middleware for common analytics operations
export const requireKpiReadAccess = requirePermissions([analyticsPermissions.VIEW_KPIS]);
export const requireKpiWriteAccess = requirePermissions([analyticsPermissions.CREATE_KPIS, analyticsPermissions.UPDATE_KPIS]);
export const requireKpiAdminAccess = requirePermissions([analyticsPermissions.ADMIN_ANALYTICS]);

export const requireReportReadAccess = requirePermissions([analyticsPermissions.VIEW_REPORTS]);
export const requireReportWriteAccess = requirePermissions([analyticsPermissions.CREATE_REPORTS]);
export const requireReportAdminAccess = requirePermissions([analyticsPermissions.ADMIN_ANALYTICS]);

export const requireForecastReadAccess = requirePermissions([analyticsPermissions.VIEW_FORECASTS]);
export const requireForecastWriteAccess = requirePermissions([analyticsPermissions.CREATE_FORECASTS]);
export const requireForecastAdminAccess = requirePermissions([analyticsPermissions.ADMIN_ANALYTICS]);

export const requireCubeReadAccess = requirePermissions([analyticsPermissions.VIEW_CUBES]);
export const requireCubeAdminAccess = requirePermissions([analyticsPermissions.ADMIN_ANALYTICS]);

// Tenant isolation middleware (ensures users can only access their tenant's data)
export async function tenantIsolationMiddleware(request: FastifyRequest, reply: FastifyReply) {
  const authRequest = request as AuthenticatedRequest;

  if (!authRequest.user) {
    return reply.code(401).send({
      error: 'Unauthorized',
      message: 'Authentication required',
    });
  }

  const userTenantId = authRequest.user.tenantId;

  // Check if user is trying to access data from a different tenant
  // This is an additional security check beyond the database-level tenant isolation
  if (request.params && typeof request.params === 'object' && 'tenantId' in request.params) {
    const requestedTenantId = (request.params as any).tenantId as string;
    if (requestedTenantId && requestedTenantId !== userTenantId) {
      return reply.code(403).send({
        error: 'Forbidden',
        message: 'Cannot access data from different tenant',
        userTenantId,
        requestedTenantId,
      });
    }
  }

  // For query parameters that might specify tenant
  if (request.query && typeof request.query === 'object' && 'tenantId' in request.query) {
    const requestedTenantId = (request.query as any).tenantId as string;
    if (requestedTenantId && requestedTenantId !== userTenantId) {
      return reply.code(403).send({
        error: 'Forbidden',
        message: 'Cannot access data from different tenant',
        userTenantId,
        requestedTenantId,
      });
    }
  }

  // Ensure tenantId is set on the request for database queries
  authRequest.tenantId = userTenantId;
}

// Combined middleware for analytics endpoints
export const analyticsAuthMiddleware = [authMiddleware, tenantIsolationMiddleware];

// Admin-only middleware
export const adminOnlyMiddleware = [
  authMiddleware,
  tenantIsolationMiddleware,
  requirePermissions([analyticsPermissions.ADMIN_ANALYTICS]),
];