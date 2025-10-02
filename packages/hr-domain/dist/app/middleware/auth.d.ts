/**
 * Authentication Middleware for VALEO NeuroERP 3.0 HR Domain
 * JWT validation with JWKS
 */
import { FastifyRequest, FastifyReply } from 'fastify';
interface AuthContext {
    userId: string;
    tenantId: string;
    roles: string[];
    permissions: string[];
    token: string;
}
declare module 'fastify' {
    interface FastifyRequest {
        auth?: AuthContext;
    }
}
export declare function initializeAuth(): Promise<void>;
export declare function authMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<undefined>;
export declare function requireAuth(request: FastifyRequest, reply: FastifyReply): Promise<undefined>;
export declare function requireRole(roles: string[]): Promise<(request: FastifyRequest, reply: FastifyReply) => Promise<undefined>>;
export declare function requirePermission(permissions: string[]): Promise<(request: FastifyRequest, reply: FastifyReply) => Promise<undefined>>;
export declare const hrPermissions: {
    EMPLOYEE_READ: string;
    EMPLOYEE_WRITE: string;
    EMPLOYEE_DELETE: string;
    TIME_READ: string;
    TIME_WRITE: string;
    TIME_APPROVE: string;
    LEAVE_READ: string;
    LEAVE_WRITE: string;
    LEAVE_APPROVE: string;
    SHIFT_READ: string;
    SHIFT_WRITE: string;
    PAYROLL_READ: string;
    PAYROLL_WRITE: string;
    PAYROLL_EXPORT: string;
    ROLE_READ: string;
    ROLE_WRITE: string;
};
export declare function requireHrPermission(permission: string): (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export {};
//# sourceMappingURL=auth.d.ts.map