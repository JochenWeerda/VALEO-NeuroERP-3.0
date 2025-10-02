import { Request, Response, NextFunction } from 'express';
import { JWTValidator } from '../jwt/jwt-validator';
import { RBACPolicy } from '../policies/rbac-policy';
import { TenantContextManager } from '../context/tenant-context';
import { AuthMiddlewareOptions, UserContext } from '../types/auth-types';
export declare class AuthMiddleware {
    private jwtValidator;
    private rbacPolicy;
    private tenantContext;
    constructor(jwtValidator: JWTValidator, rbacPolicy: RBACPolicy, tenantContext: TenantContextManager);
    /**
     * Express middleware for authentication and authorization
     */
    middleware(options?: Partial<AuthMiddlewareOptions>): (req: Request, res: Response, next: NextFunction) => Promise<void>;
    /**
     * Middleware factory for different auth levels
     */
    static createMiddleware(jwtValidator: JWTValidator, rbacPolicy: RBACPolicy, tenantContext: TenantContextManager): {
        requireAuth: (options?: AuthMiddlewareOptions) => any;
        optionalAuth: (options?: AuthMiddlewareOptions) => any;
        requireRoles: (roles: string[], options?: Omit<AuthMiddlewareOptions, 'requireRoles'>) => any;
        requirePermissions: (permissions: string[], options?: Omit<AuthMiddlewareOptions, 'requirePermissions'>) => any;
    };
}
/**
 * Helper function to extract user from request
 */
export declare function getUserFromRequest(req: Request): UserContext | null;
/**
 * Helper function to check if user has permission
 */
export declare function hasPermission(rbacPolicy: RBACPolicy, req: Request, resource: string, action: string): boolean;
//# sourceMappingURL=auth-middleware.d.ts.map