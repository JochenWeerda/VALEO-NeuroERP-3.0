import { Request, Response, NextFunction } from 'express';
import { JWTValidator } from '../jwt/jwt-validator';
import { RBACPolicy } from '../policies/rbac-policy';
import { TenantContextManager } from '../context/tenant-context';
import { AuthMiddlewareOptions, UserContext, PolicyResult } from '../types/auth-types';

export class AuthMiddleware {
  private jwtValidator: JWTValidator;
  private rbacPolicy: RBACPolicy;
  private tenantContext: TenantContextManager;

  constructor(
    jwtValidator: JWTValidator,
    rbacPolicy: RBACPolicy,
    tenantContext: TenantContextManager
  ) {
    this.jwtValidator = jwtValidator;
    this.rbacPolicy = rbacPolicy;
    this.tenantContext = tenantContext;
  }

  /**
   * Express middleware for authentication and authorization
   */
  middleware(options: Partial<AuthMiddlewareOptions> = {}) {
    const defaultOptions: AuthMiddlewareOptions = {
      requireAuth: false,
      requireTenant: false,
      tokenHeader: 'authorization',
      tenantHeader: 'x-tenant-id',
      ...options
    };
    return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
      try {
        // Extract token from header
        const authHeader = req.headers[defaultOptions.tokenHeader] as string;
        if (!authHeader && defaultOptions.requireAuth) {
          res.status(401).json({
            error: 'Authentication required',
            code: 'MISSING_TOKEN'
          });
          return;
        }

        let user: UserContext | null = null;

        // Validate JWT if token provided
        if (authHeader) {
          const token = authHeader.replace('Bearer ', '');
          user = await this.jwtValidator.validateToken(token);

          // Set user context in request
          (req as any).user = user;

          // Validate tenant context
          const requestedTenantId = req.headers[defaultOptions.tenantHeader] as string;
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
          const hasRequiredRole = defaultOptions.requireRoles.some(role =>
            user!.roles.includes(role)
          );

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

      } catch (error) {
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
  static createMiddleware(
    jwtValidator: JWTValidator,
    rbacPolicy: RBACPolicy,
    tenantContext: TenantContextManager
  ): {
    requireAuth: (options?: AuthMiddlewareOptions) => any;
    optionalAuth: (options?: AuthMiddlewareOptions) => any;
    requireRoles: (roles: string[], options?: Omit<AuthMiddlewareOptions, 'requireRoles'>) => any;
    requirePermissions: (permissions: string[], options?: Omit<AuthMiddlewareOptions, 'requirePermissions'>) => any;
  } {
    const authMiddleware = new AuthMiddleware(jwtValidator, rbacPolicy, tenantContext);

    return {
      requireAuth: (options?: AuthMiddlewareOptions) =>
        authMiddleware.middleware({ ...options, requireAuth: true }),

      optionalAuth: (options?: AuthMiddlewareOptions) =>
        authMiddleware.middleware({ ...options, requireAuth: false }),

      requireRoles: (roles: string[], options?: Omit<AuthMiddlewareOptions, 'requireRoles'>) =>
        authMiddleware.middleware({ ...options, requireAuth: true, requireRoles: roles }),

      requirePermissions: (permissions: string[], options?: Omit<AuthMiddlewareOptions, 'requirePermissions'>) =>
        authMiddleware.middleware({ ...options, requireAuth: true, requirePermissions: permissions })
    };
  }
}

/**
 * Helper function to extract user from request
 */
export function getUserFromRequest(req: Request): UserContext | null {
  return (req as any).user || null;
}

/**
 * Helper function to check if user has permission
 */
export function hasPermission(
  rbacPolicy: RBACPolicy,
  req: Request,
  resource: string,
  action: string
): boolean {
  const user = getUserFromRequest(req);
  if (!user) return false;

  const result = rbacPolicy.canAccess(user, resource, action);
  return result.allowed;
}