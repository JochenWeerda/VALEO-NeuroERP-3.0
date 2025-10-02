import { FastifyRequest, FastifyReply } from 'fastify';
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
export declare function authMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<undefined>;
export declare function requireRoles(requiredRoles: string[]): (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare function requirePermissions(requiredPermissions: string[]): (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const analyticsPermissions: {
    VIEW_KPIS: string;
    CREATE_KPIS: string;
    UPDATE_KPIS: string;
    DELETE_KPIS: string;
    RECALCULATE_KPIS: string;
    VIEW_REPORTS: string;
    CREATE_REPORTS: string;
    DELETE_REPORTS: string;
    VIEW_FORECASTS: string;
    CREATE_FORECASTS: string;
    DELETE_FORECASTS: string;
    COMPARE_FORECASTS: string;
    VIEW_CUBES: string;
    REFRESH_CUBES: string;
    ADMIN_ANALYTICS: string;
};
export declare const requireKpiReadAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireKpiWriteAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireKpiAdminAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireReportReadAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireReportWriteAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireReportAdminAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireForecastReadAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireForecastWriteAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireForecastAdminAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireCubeReadAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare const requireCubeAdminAccess: (request: FastifyRequest, reply: FastifyReply) => Promise<undefined>;
export declare function tenantIsolationMiddleware(request: FastifyRequest, reply: FastifyReply): Promise<undefined>;
export declare const analyticsAuthMiddleware: (typeof authMiddleware)[];
export declare const adminOnlyMiddleware: ((request: FastifyRequest, reply: FastifyReply) => Promise<undefined>)[];
export type { AuthenticatedRequest, AuthenticatedUser };
//# sourceMappingURL=auth.d.ts.map